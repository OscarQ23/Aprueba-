"""Pruebas de la curva de aprendizaje, usando la muestra versionada en el repo."""

import pytest

from src import config
from src.modelos.curva_aprendizaje import (
    cargar_datos,
    curva_aprendizaje,
    dividir_fuera_de_tiempo,
    linea_base_grado,
    resumir,
    tamanos_por_defecto,
)
from src.modelos.pipelines import construir_gradient_boosting


@pytest.fixture(scope="module")
def muestra():
    return cargar_datos(config.DATA_MUESTRA / "muestra_prestamos.csv")


def test_division_fuera_de_tiempo_no_mezcla_epocas(muestra):
    entrenamiento, prueba = dividir_fuera_de_tiempo(muestra, 0.2)
    assert entrenamiento["cosecha"].max() < prueba["cosecha"].min()
    assert len(entrenamiento) + len(prueba) == len(muestra)
    assert abs(len(prueba) / len(muestra) - 0.2) < 0.05


def test_tamanos_por_defecto_duplican_y_terminan_en_el_total():
    assert tamanos_por_defecto(800) == [100, 200, 400, 800]
    assert tamanos_por_defecto(1_000_000)[-1] == 1_000_000
    assert tamanos_por_defecto(50) == [50]


def test_linea_base_grado_tiene_auc_valido(muestra):
    _, prueba = dividir_fuera_de_tiempo(muestra)
    base = linea_base_grado(prueba)
    assert 0.5 < base["auc_grado"] < 1
    assert 0 < base["exactitud_todos_buenos"] < 1


def test_curva_mide_ambos_modelos_y_omite_tamanos_excesivos(muestra):
    entrenamiento, prueba = dividir_fuera_de_tiempo(muestra)
    resultados = curva_aprendizaje(
        entrenamiento, prueba, tamanos=[100, 10**9], repeticiones=2
    )
    assert set(resultados["n"]) == {100}
    assert set(resultados["modelo"]) == {"logistica", "mlp", "boosting"}
    assert len(resultados) == 6
    assert resultados["auc"].between(0, 1).all()
    assert list(resumir(resultados)["n"]) == [100, 100, 100]


def test_boosting_tolera_nulos_y_categorias_nuevas(muestra):
    entrenamiento, _ = dividir_fuera_de_tiempo(muestra)
    X = entrenamiento[config.VARIABLES_NUMERICAS + config.VARIABLES_CATEGORICAS]
    modelo = construir_gradient_boosting().fit(X, entrenamiento[config.VARIABLE_OBJETIVO])
    nueva = X.head(3).copy()
    nueva["anios_empleo"] = None
    nueva["purpose"] = "categoria_que_nunca_vio"
    probabilidad = modelo.predict_proba(nueva)[:, 1]
    assert probabilidad.shape == (3,)
    assert ((probabilidad >= 0) & (probabilidad <= 1)).all()


def test_el_modelo_no_usa_columnas_posteriores_al_desembolso():
    posteriores_al_desembolso = {
        "total_pymnt",
        "total_pymnt_inv",
        "out_prncp",
        "last_pymnt_d",
        "last_pymnt_amnt",
        "collection_recovery_fee",
        "total_rec_late_fee",
        "last_fico_range_low",
    }
    prohibidas = (
        set(config.COLUMNAS_RESULTADO)
        | posteriores_al_desembolso
        | {"grade", "int_rate", "installment"}
    )
    usadas = set(config.VARIABLES_NUMERICAS + config.VARIABLES_CATEGORICAS)
    assert not usadas & prohibidas
