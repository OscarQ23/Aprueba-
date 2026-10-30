"""Transformaciones de columnas compartidas por la ingesta y la API.

Viven en un solo lugar para que el modelo reciba exactamente las mismas
variables al entrenar (Dask) y al responder solicitudes (FastAPI).
"""

import numpy as np
import pandas as pd

from src import config


def plazo_en_meses(term: pd.Series) -> pd.Series:
    """Convierte ``" 36 months"`` en ``36.0``.

    Args:
        term: Columna ``term`` de Lending Club.

    Returns:
        Plazo en meses como número; NaN si no se puede leer.
    """
    numero = term.astype("string").str.extract(r"(\d+)")[0]
    return pd.to_numeric(numero, errors="coerce").astype("float64")


def anios_de_empleo(emp_length: pd.Series) -> pd.Series:
    """Convierte ``"10+ years"`` en ``10`` y ``"< 1 year"`` en ``0``.

    Args:
        emp_length: Columna ``emp_length`` de Lending Club.

    Returns:
        Años de empleo como número; NaN si el dato no viene.
    """
    texto = emp_length.astype("string")
    anios = pd.to_numeric(texto.str.extract(r"(\d+)")[0], errors="coerce").astype("float64")
    menos_de_uno = texto.str.startswith("<").fillna(False).astype(bool).to_numpy()
    return anios.where(~menos_de_uno, 0.0)


def antiguedad_credito(earliest_cr_line: pd.Series, issue_d: pd.Series) -> pd.Series:
    """Años entre la primera línea de crédito y el desembolso.

    Args:
        earliest_cr_line: Mes de la primera línea de crédito (``"Aug-2003"``).
        issue_d: Mes de desembolso (``"Dec-2015"``).

    Returns:
        Antigüedad del historial crediticio en años.
    """
    inicio = pd.to_datetime(earliest_cr_line, format="%b-%Y", errors="coerce")
    desembolso = pd.to_datetime(issue_d, format="%b-%Y", errors="coerce")
    return (desembolso - inicio).dt.days / 365.25


def agregar_variables(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega las variables derivadas que usa el modelo.

    Args:
        df: Préstamos con las columnas de ``config.COLUMNAS_SOLICITUD``.

    Returns:
        Copia del DataFrame con ``plazo_meses``, ``anios_empleo``,
        ``antiguedad_credito_anios`` y ``cosecha`` (mes de desembolso como
        texto ``"YYYY-MM"``; Spark no lee fechas de Parquet en nanosegundos).
    """
    df = df.copy()
    df["plazo_meses"] = plazo_en_meses(df["term"])
    df["anios_empleo"] = anios_de_empleo(df["emp_length"])
    df["antiguedad_credito_anios"] = antiguedad_credito(df["earliest_cr_line"], df["issue_d"])
    desembolso = pd.to_datetime(df["issue_d"], format="%b-%Y", errors="coerce")
    df["cosecha"] = desembolso.dt.strftime("%Y-%m")
    return df


def agregar_resultado(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega la variable objetivo y el resultado económico de cada préstamo.

    ``resultado_neto`` usa columnas posteriores al desembolso: solo sirve para
    evaluar decisiones de negocio, nunca como variable del modelo.

    Args:
        df: Préstamos con las columnas de ``config.COLUMNAS_RESULTADO``.

    Returns:
        Copia con ``es_malo`` (1 = castigado) y ``resultado_neto`` en USD.
    """
    df = df.copy()
    df[config.VARIABLE_OBJETIVO] = df["loan_status"].isin(config.ESTADOS_MALOS).astype("int8")
    df["resultado_neto"] = (
        df["total_rec_prncp"] + df["total_rec_int"] + df["recoveries"] - df["funded_amnt"]
    ).astype("float64")
    return df


def limpiar(df: pd.DataFrame) -> pd.DataFrame:
    """Descarta valores imposibles que vienen en el dataset.

    Args:
        df: Préstamos con variables derivadas.

    Returns:
        Copia con ``dti`` y ``revol_util`` fuera de rango convertidos a NaN y
        sin filas de ingreso anual igual o menor a cero.
    """
    df = df.copy()
    df["dti"] = df["dti"].where(df["dti"].between(0, 100))
    df["revol_util"] = df["revol_util"].where(df["revol_util"].between(0, 150))
    return df[df["annual_inc"] > 0]


def preparar_particion(df: pd.DataFrame) -> pd.DataFrame:
    """Pipeline completo para una partición: filtrar, derivar, limpiar.

    Args:
        df: Partición cruda leída del CSV.

    Returns:
        Solo préstamos terminados, con variables y resultado.
    """
    terminados = df[df["loan_status"].isin(config.ESTADOS_BUENOS + config.ESTADOS_MALOS)]
    salida = limpiar(agregar_resultado(agregar_variables(terminados)))
    salida["anio_cosecha"] = pd.to_numeric(salida["cosecha"].str[:4], errors="coerce").astype("Int16")
    return salida.replace([np.inf, -np.inf], np.nan)
