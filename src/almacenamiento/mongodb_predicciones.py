"""Persistencia de la bitácora de predicciones en MongoDB.

Las funciones reciben una colección por parámetro para que la lógica pueda
probarse con ``mongomock`` sin levantar un servidor real.
"""

from datetime import datetime, timezone
from typing import Literal, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pymongo import ASCENDING, DESCENDING, MongoClient
from pymongo.collection import Collection

from src import config


def _fecha_utc_sin_zona(fecha: datetime) -> datetime:
    """Normaliza una fecha al formato UTC sin zona usado por MongoDB."""
    if fecha.tzinfo is None:
        return fecha
    return fecha.astimezone(timezone.utc).replace(tzinfo=None)


class RegistroPrediccion(BaseModel):
    """Documento validado antes de escribirse en la bitácora."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    solicitud_id: str = Field(min_length=1)
    fecha: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
    probabilidad_impago: float = Field(ge=0.0, le=1.0)
    decision: Literal["aprobar", "revisar", "rechazar"]
    motivos: list[str] = Field(default_factory=list)
    version_modelo: str = Field(min_length=1)

    @field_validator("fecha")
    @classmethod
    def normalizar_fecha(cls, fecha: datetime) -> datetime:
        """Convierte fechas con zona a UTC antes de persistirlas."""
        return _fecha_utc_sin_zona(fecha)


def obtener_coleccion() -> Collection:
    """Crea la colección configurada mediante variables de entorno.

    Variables opcionales: ``MONGODB_URI``, ``MONGODB_DB`` y
    ``MONGODB_COLECCION``. La conexión real se establece de forma perezosa.
    """
    cliente = MongoClient(config.MONGODB_URI)
    return cliente[config.MONGODB_DB][config.MONGODB_COLECCION]


def crear_indice_fecha(coleccion: Collection) -> str:
    """Crea el índice descendente usado para consultar predicciones recientes."""
    return coleccion.create_index(
        [("fecha", DESCENDING)],
        name="idx_predicciones_fecha",
    )


def registrar_prediccion(
    coleccion: Collection,
    registro: Union[RegistroPrediccion, dict],
) -> str:
    """Valida e inserta una predicción y devuelve su identificador."""
    documento = RegistroPrediccion.model_validate(registro).model_dump(mode="python")
    resultado = coleccion.insert_one(documento)
    return str(resultado.inserted_id)


def consultar_predicciones_desde(
    coleccion: Collection,
    desde: datetime,
    limite: int = 100,
) -> list[dict]:
    """Consulta documentos posteriores a ``desde`` mediante el operador ``$gt``."""
    if limite < 1:
        raise ValueError("limite debe ser al menos 1")
    cursor = (
        coleccion.find({"fecha": {"$gt": _fecha_utc_sin_zona(desde)}})
        .sort("fecha", ASCENDING)
        .limit(limite)
    )
    return list(cursor)
