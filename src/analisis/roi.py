"""Modelo reproducible de ROI y flujo de caja para Aprueba+.

Los valores por defecto son un escenario ilustrativo, no datos de una empresa.
Todos los supuestos se exportan junto con los resultados para evitar presentar
estimaciones como hechos observados.

Uso:
    python -m src.analisis.roi
"""

import csv
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional

from src import config


@dataclass(frozen=True)
class SupuestosROI:
    """Supuestos económicos modificables del escenario de evaluación."""

    solicitudes_mensuales: int = 300
    tasa_aprobacion: float = 0.60
    monto_promedio: float = 1000.0
    tasa_impago_sin_modelo: float = 0.20
    tasa_impago_con_modelo: float = 0.16
    perdida_dado_impago: float = 0.70
    inversion_inicial: float = 15000.0
    costo_operativo_mensual: float = 1000.0

    def __post_init__(self) -> None:
        if self.solicitudes_mensuales <= 0:
            raise ValueError("solicitudes_mensuales debe ser mayor que cero")
        for nombre in (
            "tasa_aprobacion",
            "tasa_impago_sin_modelo",
            "tasa_impago_con_modelo",
            "perdida_dado_impago",
        ):
            valor = getattr(self, nombre)
            if not 0 <= valor <= 1:
                raise ValueError(f"{nombre} debe estar entre 0 y 1")
        if self.tasa_impago_con_modelo > self.tasa_impago_sin_modelo:
            raise ValueError("el escenario de beneficio requiere no aumentar la tasa de impago")
        for nombre in ("monto_promedio", "inversion_inicial", "costo_operativo_mensual"):
            if getattr(self, nombre) < 0:
                raise ValueError(f"{nombre} no puede ser negativo")


def beneficio_bruto_mensual(supuestos: SupuestosROI) -> float:
    """Calcula la pérdida esperada evitada cada mes."""
    prestamos_aprobados = supuestos.solicitudes_mensuales * supuestos.tasa_aprobacion
    reduccion_impago = (
        supuestos.tasa_impago_sin_modelo - supuestos.tasa_impago_con_modelo
    )
    perdida_por_impago = supuestos.monto_promedio * supuestos.perdida_dado_impago
    return prestamos_aprobados * reduccion_impago * perdida_por_impago


def generar_flujo(supuestos: SupuestosROI, meses: int = 24) -> List[Dict[str, float]]:
    """Genera los flujos mensuales, incluido el desembolso inicial del mes cero."""
    if meses < 1:
        raise ValueError("meses debe ser al menos 1")
    filas = []
    acumulado = -supuestos.inversion_inicial
    filas.append(
        {
            "mes": 0,
            "beneficio_bruto": 0.0,
            "costo": supuestos.inversion_inicial,
            "flujo_neto": -supuestos.inversion_inicial,
            "flujo_acumulado": acumulado,
        }
    )
    beneficio = beneficio_bruto_mensual(supuestos)
    flujo_mensual = beneficio - supuestos.costo_operativo_mensual
    for mes in range(1, meses + 1):
        acumulado += flujo_mensual
        filas.append(
            {
                "mes": mes,
                "beneficio_bruto": round(beneficio, 2),
                "costo": supuestos.costo_operativo_mensual,
                "flujo_neto": round(flujo_mensual, 2),
                "flujo_acumulado": round(acumulado, 2),
            }
        )
    return filas


def resumir_horizonte(supuestos: SupuestosROI, meses: int) -> Dict[str, Optional[float]]:
    """Resume beneficio, costos, ROI y periodo de recuperación."""
    flujo = generar_flujo(supuestos, meses)
    beneficio_total = sum(fila["beneficio_bruto"] for fila in flujo)
    costo_total = sum(fila["costo"] for fila in flujo)
    flujo_neto = beneficio_total - costo_total
    recuperacion = next(
        (int(fila["mes"]) for fila in flujo if fila["flujo_acumulado"] >= 0),
        None,
    )
    return {
        "meses": meses,
        "beneficio_total": round(beneficio_total, 2),
        "costo_total": round(costo_total, 2),
        "flujo_neto": round(flujo_neto, 2),
        "roi": round(flujo_neto / costo_total, 4) if costo_total else math.inf,
        "mes_recuperacion": recuperacion,
    }


def exportar_resultados(
    supuestos: SupuestosROI,
    ruta_flujo: Path = config.REPORTES / "flujo_caja_24_meses.csv",
    ruta_resumen: Path = config.REPORTES / "roi_resumen.json",
) -> None:
    """Exporta flujo a 24 meses y resúmenes a 12 y 24 meses."""
    ruta_flujo.parent.mkdir(parents=True, exist_ok=True)
    flujo = generar_flujo(supuestos, 24)
    with ruta_flujo.open("w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=list(flujo[0]))
        escritor.writeheader()
        escritor.writerows(flujo)
    resultado = {
        "advertencia": "Escenario ilustrativo; validar supuestos con la financiera.",
        "supuestos": asdict(supuestos),
        "horizonte_12_meses": resumir_horizonte(supuestos, 12),
        "horizonte_24_meses": resumir_horizonte(supuestos, 24),
    }
    ruta_resumen.write_text(
        json.dumps(resultado, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def main() -> None:
    """Genera los artefactos de negocio usando el escenario inicial."""
    supuestos = SupuestosROI()
    exportar_resultados(supuestos)
    print(json.dumps({
        "12_meses": resumir_horizonte(supuestos, 12),
        "24_meses": resumir_horizonte(supuestos, 24),
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
