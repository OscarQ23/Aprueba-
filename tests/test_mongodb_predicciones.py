"""Pruebas de la bitácora MongoDB sin servidor real."""

from datetime import datetime

import mongomock
import pytest
from pydantic import ValidationError

from src.almacenamiento.mongodb_predicciones import (
    consultar_predicciones_desde,
    crear_indice_fecha,
    registrar_prediccion,
)


@pytest.fixture
def coleccion():
    return mongomock.MongoClient().aprueba.predicciones


def registro(fecha: datetime, solicitud_id: str, probabilidad: float = 0.2) -> dict:
    return {
        "solicitud_id": solicitud_id,
        "fecha": fecha,
        "probabilidad_impago": probabilidad,
        "decision": "aprobar",
        "motivos": ["historial estable"],
        "version_modelo": "v1",
    }


def test_crea_indice_por_fecha(coleccion):
    nombre = crear_indice_fecha(coleccion)
    assert nombre == "idx_predicciones_fecha"
    assert "fecha" in coleccion.index_information()[nombre]["key"][0]


def test_valida_con_pydantic_antes_de_insertar(coleccion):
    with pytest.raises(ValidationError):
        registrar_prediccion(
            coleccion,
            registro(datetime(2026, 10, 30), "sol-1", probabilidad=1.5),
        )
    assert coleccion.count_documents({}) == 0


def test_inserta_y_consulta_con_gt_en_orden_cronologico(coleccion):
    registrar_prediccion(coleccion, registro(datetime(2026, 10, 29), "anterior"))
    registrar_prediccion(coleccion, registro(datetime(2026, 10, 31), "posterior-1"))
    registrar_prediccion(coleccion, registro(datetime(2026, 11, 1), "posterior-2"))

    encontrados = consultar_predicciones_desde(coleccion, datetime(2026, 10, 30))

    assert [item["solicitud_id"] for item in encontrados] == ["posterior-1", "posterior-2"]
