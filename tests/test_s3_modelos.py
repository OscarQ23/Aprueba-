"""Pruebas del almacén de modelos con S3 simulado por moto."""

from pathlib import Path
from unittest.mock import Mock

import boto3
import pytest
from botocore.exceptions import ClientError
from moto import mock_aws

from src.almacenamiento.s3_modelos import descargar_modelo, subir_modelo


@mock_aws
def test_sube_y_descarga_modelo_versionado(tmp_path: Path):
    cliente = boto3.client(
        "s3",
        region_name="us-east-1",
        aws_access_key_id="prueba",
        aws_secret_access_key="prueba",
    )
    cliente.create_bucket(Bucket="bucket-prueba")
    origen = tmp_path / "modelo.joblib"
    origen.write_bytes(b"modelo de prueba")

    clave = subir_modelo(origen, "v1.2.0", cliente=cliente, bucket="bucket-prueba")
    destino = descargar_modelo(
        clave,
        tmp_path / "descargas" / "modelo.joblib",
        cliente=cliente,
        bucket="bucket-prueba",
    )

    assert clave == "modelos/v1.2.0/modelo.joblib"
    assert destino.read_bytes() == b"modelo de prueba"


def test_error_403_se_convierte_en_mensaje_accionable(tmp_path: Path):
    origen = tmp_path / "modelo.joblib"
    origen.write_bytes(b"modelo")
    error = ClientError(
        {
            "Error": {"Code": "403", "Message": "Forbidden"},
            "ResponseMetadata": {"HTTPStatusCode": 403},
        },
        "UploadFile",
    )
    cliente = Mock()
    cliente.upload_file.side_effect = error

    with pytest.raises(PermissionError, match="credenciales y permisos"):
        subir_modelo(origen, "v1", cliente=cliente, bucket="bucket-prueba")
