"""Pruebas de calidad de datos sobre las transformaciones de la ingesta."""

import numpy as np
import pandas as pd

from src.utils.transformaciones import (
    agregar_resultado,
    anios_de_empleo,
    antiguedad_credito,
    limpiar,
    plazo_en_meses,
)


def test_plazo_en_meses_lee_el_numero():
    assert plazo_en_meses(pd.Series([" 36 months", " 60 months"])).tolist() == [36, 60]


def test_anios_de_empleo_casos_especiales():
    resultado = anios_de_empleo(pd.Series(["10+ years", "< 1 year", "3 years", None]))
    assert resultado.iloc[:3].tolist() == [10, 0, 3]
    assert np.isnan(resultado.iloc[3])


def test_antiguedad_credito_en_anios():
    anios = antiguedad_credito(pd.Series(["Jan-2000"]), pd.Series(["Jan-2010"]))
    assert abs(anios.iloc[0] - 10) < 0.01


def test_resultado_marca_castigados_y_calcula_perdida():
    df = pd.DataFrame(
        {
            "loan_status": ["Fully Paid", "Charged Off"],
            "funded_amnt": [1000.0, 1000.0],
            "total_rec_prncp": [1000.0, 300.0],
            "total_rec_int": [150.0, 50.0],
            "recoveries": [0.0, 100.0],
        }
    )
    salida = agregar_resultado(df)
    assert salida["es_malo"].tolist() == [0, 1]
    assert salida["resultado_neto"].tolist() == [150.0, -550.0]


def test_limpiar_descarta_valores_imposibles():
    df = pd.DataFrame({"dti": [20.0, 999.0], "revol_util": [50.0, -5.0], "annual_inc": [5e4, 6e4]})
    salida = limpiar(df)
    assert salida["dti"].isna().tolist() == [False, True]
    assert salida["revol_util"].isna().tolist() == [False, True]


def test_limpiar_quita_ingresos_no_positivos():
    df = pd.DataFrame({"dti": [10.0, 10.0], "revol_util": [10.0, 10.0], "annual_inc": [0.0, 4e4]})
    assert len(limpiar(df)) == 1
