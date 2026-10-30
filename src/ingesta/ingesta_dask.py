"""Ingesta con Dask: del CSV de Lending Club a un Parquet limpio.

Uso:
    python -m src.ingesta.ingesta_dask

Pasos:
    1. Descomprime el ``.csv.gz`` una sola vez. Un archivo gzip no se puede
       partir en bloques, así que Dask lo leería en una sola partición, sin
       paralelismo (ver docs/decisiones.md, decisión 003).
    2. Lee el CSV con Dask en particiones de 64 MB, solo con las columnas
       necesarias y con los tipos declarados explícitamente.
    3. Filtra los préstamos terminados, deriva variables y guarda en Parquet.
    4. Mide el mismo trabajo con Pandas para comparar tiempos.
"""

import gzip
import json
import shutil
import time

import dask.dataframe as dd
import pandas as pd

from src import config
from src.utils.transformaciones import preparar_particion

TAMANO_BLOQUE = "64MB"


def descomprimir(origen=config.ARCHIVO_GZ, destino=config.ARCHIVO_CSV) -> None:
    """Descomprime el archivo gzip si todavía no existe el CSV.

    Args:
        origen: Ruta del ``.csv.gz`` descargado de Kaggle.
        destino: Ruta del ``.csv`` descomprimido.

    Raises:
        FileNotFoundError: Si no está el archivo descargado en ``data/raw``.
    """
    if destino.exists():
        return
    if not origen.exists():
        raise FileNotFoundError(
            f"No se encontró {origen}. Descárgalo de Kaggle y colócalo en data/raw/."
        )
    destino.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(origen, "rb") as entrada, open(destino, "wb") as salida:
        shutil.copyfileobj(entrada, salida, length=16 * 1024 * 1024)


def leer_con_dask(ruta=config.ARCHIVO_CSV, bloque: str = TAMANO_BLOQUE) -> dd.DataFrame:
    """Lee el CSV en particiones con tipos declarados.

    Args:
        ruta: CSV descomprimido.
        bloque: Tamaño de cada partición.

    Returns:
        DataFrame de Dask perezoso (todavía no se ha leído nada).
    """
    return dd.read_csv(
        ruta,
        usecols=list(config.DTYPES),
        dtype=config.DTYPES,
        blocksize=bloque,
    )


def procesar_con_dask(ruta=config.ARCHIVO_CSV, destino=config.PARQUET_PRESTAMOS) -> dict:
    """Ejecuta la transformación con Dask y guarda el Parquet.

    Args:
        ruta: CSV descomprimido.
        destino: Carpeta del Parquet de salida.

    Returns:
        Número de particiones, filas escritas y segundos que tomó.
    """
    inicio = time.perf_counter()
    crudo = leer_con_dask(ruta)
    meta = preparar_particion(crudo._meta)
    limpio = crudo.map_partitions(preparar_particion, meta=meta)
    # to_parquet es la acción que dispara todo el cálculo perezoso.
    limpio.to_parquet(destino, write_index=False, overwrite=True)
    filas = len(dd.read_parquet(destino))
    return {
        "particiones": crudo.npartitions,
        "filas": int(filas),
        "segundos": round(time.perf_counter() - inicio, 1),
    }


def procesar_con_pandas(ruta=config.ARCHIVO_CSV) -> dict:
    """Hace el mismo trabajo con Pandas, en memoria, para comparar tiempos.

    Args:
        ruta: CSV descomprimido.

    Returns:
        Filas resultantes, segundos y memoria usada por el DataFrame crudo.
    """
    inicio = time.perf_counter()
    crudo = pd.read_csv(ruta, usecols=list(config.DTYPES), dtype=config.DTYPES)
    memoria_mb = crudo.memory_usage(deep=True).sum() / 1e6
    limpio = preparar_particion(crudo)
    return {
        "filas": int(len(limpio)),
        "segundos": round(time.perf_counter() - inicio, 1),
        "memoria_cruda_mb": round(memoria_mb),
    }


def guardar_muestra(n: int = 1000, semilla: int = 42) -> None:
    """Guarda una muestra pequeña para las pruebas y para quien no tenga el dataset.

    Args:
        n: Número de filas.
        semilla: Semilla para que la muestra sea reproducible.
    """
    df = pd.read_parquet(config.PARQUET_PRESTAMOS)
    config.DATA_MUESTRA.mkdir(parents=True, exist_ok=True)
    df.sample(n=n, random_state=semilla).to_csv(
        config.DATA_MUESTRA / "muestra_prestamos.csv", index=False
    )


def main() -> None:
    """Corre la ingesta completa y guarda la comparación de tiempos."""
    descomprimir()
    resultado = {"dask": procesar_con_dask(), "pandas": procesar_con_pandas()}
    guardar_muestra()
    config.REPORTES.mkdir(parents=True, exist_ok=True)
    (config.REPORTES / "tiempos_ingesta.json").write_text(
        json.dumps(resultado, indent=2), encoding="utf-8"
    )
    print(json.dumps(resultado, indent=2))


if __name__ == "__main__":
    main()
