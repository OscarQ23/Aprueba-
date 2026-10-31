"""Pruebas del modelo reproducible de ROI."""

import json

import pytest

from src.analisis.roi import (
    SupuestosROI,
    beneficio_bruto_mensual,
    exportar_resultados,
    generar_flujo,
    resumir_horizonte,
)


def test_beneficio_bruto_usa_reduccion_de_impago_y_lgd():
    assert beneficio_bruto_mensual(SupuestosROI()) == pytest.approx(5040.0)


def test_flujo_incluye_inversion_inicial_y_recuperacion():
    supuestos = SupuestosROI()
    flujo = generar_flujo(supuestos, 12)
    resumen = resumir_horizonte(supuestos, 12)

    assert flujo[0]["flujo_neto"] == -15000.0
    assert flujo[1]["flujo_neto"] == pytest.approx(4040.0)
    assert flujo[-1]["flujo_acumulado"] == pytest.approx(33480.0)
    assert resumen["mes_recuperacion"] == 4
    assert resumen["roi"] == pytest.approx(1.24)


def test_rechaza_tasas_fuera_de_rango():
    with pytest.raises(ValueError, match="entre 0 y 1"):
        SupuestosROI(tasa_aprobacion=1.1)


def test_exporta_supuestos_y_horizontes(tmp_path):
    ruta_csv = tmp_path / "flujo.csv"
    ruta_json = tmp_path / "resumen.json"
    exportar_resultados(SupuestosROI(), ruta_csv, ruta_json)

    resumen = json.loads(ruta_json.read_text(encoding="utf-8"))
    assert ruta_csv.read_text(encoding="utf-8").count("\n") == 26
    assert resumen["supuestos"]["solicitudes_mensuales"] == 300
    assert resumen["horizonte_12_meses"]["flujo_neto"] == 33480.0
    assert resumen["horizonte_24_meses"]["flujo_neto"] == 81960.0
