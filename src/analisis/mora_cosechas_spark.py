"""Mora por cosecha y grado con PySpark y persistencia opcional en MySQL.

Uso sobre la muestra versionada::

    python -m src.analisis.mora_cosechas_spark \
        --entrada data/muestra/muestra_prestamos.csv

El cálculo conserva ``grade`` únicamente como dimensión de análisis y línea
base. El modelo predictivo no lo usa como variable de entrada.
"""

import argparse
import csv
import time
from pathlib import Path
from typing import Dict, Iterable, Mapping

import mysql.connector
from pyspark.sql import DataFrame, SparkSession, Window
from pyspark.sql import functions as F

from src import config

COLUMNAS_ENTRADA = ["cosecha", "grade", "es_malo", "loan_amnt"]

DDL_MORA_COSECHAS = """
CREATE TABLE IF NOT EXISTS mora_cosechas (
    cosecha CHAR(7) NOT NULL,
    grado VARCHAR(2) NOT NULL,
    prestamos BIGINT NOT NULL,
    impagos BIGINT NOT NULL,
    monto_originado DECIMAL(18, 2) NOT NULL,
    monto_impago DECIMAL(18, 2) NOT NULL,
    tasa_mora DECIMAL(10, 6) NOT NULL,
    prestamos_acumulados BIGINT NOT NULL,
    impagos_acumulados BIGINT NOT NULL,
    tasa_mora_acumulada DECIMAL(10, 6) NOT NULL,
    PRIMARY KEY (cosecha, grado)
)""".strip()

SQL_UPSERT_MORA = """
INSERT INTO mora_cosechas (
    cosecha, grado, prestamos, impagos, monto_originado, monto_impago,
    tasa_mora, prestamos_acumulados, impagos_acumulados, tasa_mora_acumulada
) VALUES (
    %(cosecha)s, %(grado)s, %(prestamos)s, %(impagos)s,
    %(monto_originado)s, %(monto_impago)s, %(tasa_mora)s,
    %(prestamos_acumulados)s, %(impagos_acumulados)s,
    %(tasa_mora_acumulada)s
)
ON DUPLICATE KEY UPDATE
    prestamos = VALUES(prestamos),
    impagos = VALUES(impagos),
    monto_originado = VALUES(monto_originado),
    monto_impago = VALUES(monto_impago),
    tasa_mora = VALUES(tasa_mora),
    prestamos_acumulados = VALUES(prestamos_acumulados),
    impagos_acumulados = VALUES(impagos_acumulados),
    tasa_mora_acumulada = VALUES(tasa_mora_acumulada)
""".strip()


def crear_sesion(master: str = "local[*]") -> SparkSession:
    """Crea una sesión Spark local sin interfaz web."""
    return (
        SparkSession.builder.master(master)
        .appName("aprueba-mora-cosechas")
        .config("spark.ui.enabled", "false")
        .config("spark.python.worker.faulthandler.enabled", "true")
        .getOrCreate()
    )


def leer_prestamos(spark: SparkSession, ruta: Path) -> DataFrame:
    """Lee las columnas mínimas desde CSV o desde un directorio Parquet."""
    ruta = Path(ruta)
    if ruta.suffix.lower() == ".csv":
        # Se lee como texto para conservar los nombres del CSV completo y evitar
        # que Spark interprete una cosecha ``YYYY-MM`` como fecha.
        datos = spark.read.option("header", True).csv(str(ruta))
    else:
        datos = spark.read.parquet(str(ruta))
    faltantes = sorted(set(COLUMNAS_ENTRADA) - set(datos.columns))
    if faltantes:
        raise ValueError(f"Faltan columnas para el análisis: {', '.join(faltantes)}")
    # TRANSFORMACIÓN: select es perezosa; todavía no lee todas las filas.
    return datos.select(
        F.col("cosecha").cast("string").alias("cosecha"),
        F.col("grade").cast("string").alias("grade"),
        F.col("es_malo").cast("int").alias("es_malo"),
        F.col("loan_amnt").cast("double").alias("loan_amnt"),
    )


def calcular_mora_cosechas(prestamos: DataFrame) -> DataFrame:
    """Agrega mora mensual y calcula acumulados mediante una ventana por grado."""
    # TRANSFORMACIONES: filtros, groupBy y agregaciones construyen el plan lógico.
    validos = prestamos.filter(
        F.col("cosecha").isNotNull()
        & F.col("grade").isNotNull()
        & F.col("es_malo").isin(0, 1)
        & F.col("loan_amnt").isNotNull()
    )
    por_cosecha = validos.groupBy("cosecha", "grade").agg(
        F.count("*").alias("prestamos"),
        F.sum(F.col("es_malo").cast("long")).alias("impagos"),
        F.sum(F.col("loan_amnt").cast("double")).alias("monto_originado"),
        F.sum(
            F.when(F.col("es_malo") == 1, F.col("loan_amnt")).otherwise(0.0)
        ).alias("monto_impago"),
    )
    por_cosecha = por_cosecha.withColumn(
        "tasa_mora", F.col("impagos") / F.col("prestamos")
    )

    # FUNCIÓN DE VENTANA: acumulado cronológico independiente para cada grado.
    ventana = (
        Window.partitionBy("grade")
        .orderBy("cosecha")
        .rowsBetween(Window.unboundedPreceding, Window.currentRow)
    )
    resultado = (
        por_cosecha.withColumn("prestamos_acumulados", F.sum("prestamos").over(ventana))
        .withColumn("impagos_acumulados", F.sum("impagos").over(ventana))
        .withColumn(
            "tasa_mora_acumulada",
            F.col("impagos_acumulados") / F.col("prestamos_acumulados"),
        )
        .select(
            "cosecha",
            F.col("grade").alias("grado"),
            "prestamos",
            "impagos",
            F.round("monto_originado", 2).alias("monto_originado"),
            F.round("monto_impago", 2).alias("monto_impago"),
            F.round("tasa_mora", 6).alias("tasa_mora"),
            "prestamos_acumulados",
            "impagos_acumulados",
            F.round("tasa_mora_acumulada", 6).alias("tasa_mora_acumulada"),
        )
        .orderBy("grado", "cosecha")
    )
    return resultado


def conectar_mysql():
    """Abre una conexión MySQL usando exclusivamente variables de entorno."""
    return mysql.connector.connect(
        host=config.MYSQL_HOST,
        port=config.MYSQL_PORT,
        user=config.MYSQL_USER,
        password=config.MYSQL_PASSWORD,
        database=config.MYSQL_DATABASE,
    )


def guardar_en_mysql(
    filas: Iterable[Mapping],
    conexion=None,
    tamano_lote: int = 100,
) -> int:
    """Crea la tabla e inserta o actualiza indicadores en lotes pequeños."""
    if tamano_lote < 1:
        raise ValueError("tamano_lote debe ser al menos 1")
    documentos = [dict(fila) for fila in filas]
    propia = conexion is None
    conexion = conexion or conectar_mysql()
    cursor = conexion.cursor()
    try:
        cursor.execute(DDL_MORA_COSECHAS)
        for inicio in range(0, len(documentos), tamano_lote):
            cursor.executemany(
                SQL_UPSERT_MORA,
                documentos[inicio : inicio + tamano_lote],
            )
        conexion.commit()
    finally:
        cursor.close()
        if propia:
            conexion.close()
    return len(documentos)


def guardar_csv_agregado(filas: Iterable[Mapping], salida: Path) -> int:
    """Escribe el resultado ya agregado sin depender de ``winutils.exe``."""
    documentos = [dict(fila) for fila in filas]
    salida = Path(salida)
    salida.parent.mkdir(parents=True, exist_ok=True)
    if not documentos:
        raise ValueError("el análisis no produjo filas para exportar")
    with salida.open("w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=list(documentos[0]))
        escritor.writeheader()
        escritor.writerows(documentos)
    return len(documentos)


def ejecutar(
    entrada: Path,
    salida: Path,
    persistir_mysql: bool = False,
) -> Dict[str, float]:
    """Ejecuta el análisis, escribe CSV y opcionalmente persiste en MySQL."""
    inicio = time.perf_counter()
    spark = crear_sesion()
    try:
        resultado = calcular_mora_cosechas(leer_prestamos(spark, entrada))
        # ACCIÓN: collect materializa el plan. Es seguro porque el resultado ya
        # está agregado a unas pocas filas por mes y grado.
        filas = [fila.asDict() for fila in resultado.collect()]
        grupos = guardar_csv_agregado(filas, salida)
        filas_mysql = 0
        if persistir_mysql:
            filas_mysql = guardar_en_mysql(filas)
        return {
            "grupos": int(grupos),
            "filas_mysql": int(filas_mysql),
            "segundos": round(time.perf_counter() - inicio, 2),
        }
    finally:
        spark.stop()


def _entrada_predeterminada() -> Path:
    if config.PARQUET_PRESTAMOS.exists():
        return config.PARQUET_PRESTAMOS
    return config.DATA_MUESTRA / "muestra_prestamos.csv"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entrada", type=Path, default=_entrada_predeterminada())
    parser.add_argument(
        "--salida",
        type=Path,
        default=config.REPORTES / "mora_cosechas_spark.csv",
    )
    parser.add_argument("--mysql", action="store_true", help="Persistir también en MySQL")
    argumentos = parser.parse_args()
    resultado = ejecutar(argumentos.entrada, argumentos.salida, argumentos.mysql)
    print(resultado)


if __name__ == "__main__":
    main()
