"""Prueba mínima: confirma que los paquetes de ``src`` se pueden importar."""

import importlib

import pytest


@pytest.mark.parametrize(
    "modulo",
    ["src.ingesta", "src.almacenamiento", "src.modelos", "src.api", "src.utils"],
)
def test_paquetes_importables(modulo):
    """Cada sub-paquete de ``src`` debe importarse sin errores."""
    assert importlib.import_module(modulo) is not None
