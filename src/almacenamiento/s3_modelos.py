"""Almacén versionado de modelos mediante la interfaz compatible con S3."""

import os
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

from src import config


def crear_cliente_s3():
    """Crea un cliente S3 usando credenciales y endpoint del entorno.

    Boto3 lee ``AWS_ACCESS_KEY_ID`` y ``AWS_SECRET_ACCESS_KEY`` directamente.
    ``S3_ENDPOINT_URL`` permite apuntar a un servicio compatible con S3.
    """
    return boto3.client(
        "s3",
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        endpoint_url=os.getenv("S3_ENDPOINT_URL") or None,
    )


def _es_error_403(error: ClientError) -> bool:
    codigo = str(error.response.get("Error", {}).get("Code", ""))
    estado = error.response.get("ResponseMetadata", {}).get("HTTPStatusCode")
    return codigo in {"403", "AccessDenied"} or estado == 403


def _traducir_error_403(error: ClientError, operacion: str) -> None:
    if _es_error_403(error):
        raise PermissionError(
            f"S3 rechazó {operacion} (403). Revisa las credenciales y permisos del bucket."
        ) from error


def construir_clave(version: str, nombre_archivo: str) -> str:
    """Construye una clave estable como ``modelos/v1/modelo.joblib``."""
    version_limpia = version.strip().strip("/")
    nombre_limpio = Path(nombre_archivo).name
    if not version_limpia or not nombre_limpio:
        raise ValueError("version y nombre_archivo no pueden estar vacíos")
    return f"modelos/{version_limpia}/{nombre_limpio}"


def subir_modelo(
    ruta: Path,
    version: str,
    cliente=None,
    bucket: str = config.S3_BUCKET_MODELOS,
) -> str:
    """Sube un artefacto con ``upload_file`` y devuelve su clave versionada."""
    ruta = Path(ruta)
    if not ruta.is_file():
        raise FileNotFoundError(f"No existe el modelo: {ruta}")
    cliente = cliente or crear_cliente_s3()
    clave = construir_clave(version, ruta.name)
    try:
        cliente.upload_file(str(ruta), bucket, clave)
    except ClientError as error:
        _traducir_error_403(error, "la subida del modelo")
        raise
    return clave


def descargar_modelo(
    clave: str,
    destino: Path,
    cliente=None,
    bucket: str = config.S3_BUCKET_MODELOS,
) -> Path:
    """Descarga un artefacto con ``download_file`` y devuelve su ruta local."""
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    cliente = cliente or crear_cliente_s3()
    try:
        cliente.download_file(bucket, clave, str(destino))
    except ClientError as error:
        _traducir_error_403(error, "la descarga del modelo")
        raise
    return destino
