"""Pruebas de HU-02; Spark se activa solo en la ejecución dedicada."""

import os
from unittest.mock import Mock

import pytest

from src.analisis.mora_cosechas_spark import (
    calcular_mora_cosechas,
    crear_sesion,
    guardar_csv_agregado,
    guardar_en_mysql,
    leer_prestamos,
)


def test_mysql_crea_clave_primaria_y_hace_upsert():
    cursor = Mock()
    conexion = Mock()
    conexion.cursor.return_value = cursor
    filas = [
        {
            "cosecha": "2026-01",
            "grado": "A",
            "prestamos": 10,
            "impagos": 2,
            "monto_originado": 10000.0,
            "monto_impago": 2000.0,
            "tasa_mora": 0.2,
            "prestamos_acumulados": 10,
            "impagos_acumulados": 2,
            "tasa_mora_acumulada": 0.2,
        }
    ]

    cantidad = guardar_en_mysql(filas, conexion=conexion)

    ddl = cursor.execute.call_args.args[0]
    upsert = cursor.executemany.call_args.args[0]
    assert "PRIMARY KEY (cosecha, grado)" in ddl
    assert "ON DUPLICATE KEY UPDATE" in upsert
    assert cantidad == 1
    conexion.commit.assert_called_once_with()
    cursor.close.assert_called_once_with()
    conexion.close.assert_not_called()


def test_csv_agregado_conserva_encabezado_y_filas(tmp_path):
    salida = tmp_path / "mora.csv"
    cantidad = guardar_csv_agregado(
        [{"cosecha": "2026-01", "grado": "A", "tasa_mora": 0.2}],
        salida,
    )

    contenido = salida.read_text(encoding="utf-8")
    assert cantidad == 1
    assert contenido.splitlines()[0] == "cosecha,grado,tasa_mora"
    assert "2026-01,A,0.2" in contenido


def test_mysql_divide_la_escritura_en_lotes():
    cursor = Mock()
    conexion = Mock()
    conexion.cursor.return_value = cursor
    fila = {
        "cosecha": "2026-01",
        "grado": "A",
        "prestamos": 1,
        "impagos": 0,
        "monto_originado": 100.0,
        "monto_impago": 0.0,
        "tasa_mora": 0.0,
        "prestamos_acumulados": 1,
        "impagos_acumulados": 0,
        "tasa_mora_acumulada": 0.0,
    }

    guardar_en_mysql([fila] * 205, conexion=conexion, tamano_lote=100)

    tamanos = [len(llamada.args[1]) for llamada in cursor.executemany.call_args_list]
    assert tamanos == [100, 100, 5]


@pytest.mark.skipif(
    os.getenv("RUN_SPARK_TESTS") != "1",
    reason="activar con RUN_SPARK_TESTS=1 en el entorno Spark configurado",
)
def test_ventana_calcula_mora_acumulada_por_grado(tmp_path):
    ruta = tmp_path / "prestamos.csv"
    ruta.write_text(
        "cosecha,grade,es_malo,loan_amnt\n"
        "2024-01,A,0,1000.0\n"
        "2024-01,A,1,500.0\n"
        "2024-02,A,1,800.0\n"
        "2024-01,B,0,600.0\n",
        encoding="utf-8",
    )
    spark = crear_sesion("local[2]")
    try:
        prestamos = leer_prestamos(spark, ruta)
        filas = {
            (fila["grado"], fila["cosecha"]): fila.asDict()
            for fila in calcular_mora_cosechas(prestamos).collect()
        }

        assert filas[("A", "2024-01")]["tasa_mora"] == 0.5
        assert filas[("A", "2024-02")]["prestamos_acumulados"] == 3
        assert filas[("A", "2024-02")]["impagos_acumulados"] == 2
        assert filas[("A", "2024-02")]["tasa_mora_acumulada"] == 0.666667
        assert filas[("B", "2024-01")]["tasa_mora_acumulada"] == 0.0
    finally:
        spark.stop()
