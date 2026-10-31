"""Configuración compartida: rutas del proyecto, columnas y tipos de datos.

Todas las rutas se construyen a partir de la ubicación de este archivo, así el
código funciona igual sin importar desde qué carpeta se ejecute.
"""

import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]


def cargar_env(ruta: Path = RAIZ / ".env") -> None:
    """Carga las variables del archivo ``.env`` local sin pisar las que ya existen.

    Args:
        ruta: Archivo ``.env`` (no se sube a GitHub; ver ``.env.example``).
    """
    if not ruta.exists():
        return
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if linea and not linea.startswith("#") and "=" in linea:
            clave, valor = linea.split("=", 1)
            os.environ.setdefault(clave.strip(), valor.strip())


cargar_env()

DATA_RAW = RAIZ / "data" / "raw"
DATA_INTERIM = RAIZ / "data" / "interim"
DATA_PROCESSED = RAIZ / "data" / "processed"
DATA_MUESTRA = RAIZ / "data" / "muestra"
MODELOS = RAIZ / "models"
REPORTES = RAIZ / "reports"
FIGURAS = REPORTES / "figures"

ARCHIVO_GZ = DATA_RAW / "accepted_2007_to_2018Q4.csv.gz"
ARCHIVO_CSV = DATA_INTERIM / "accepted_2007_to_2018Q4.csv"
PARQUET_PRESTAMOS = DATA_PROCESSED / "prestamos_terminados.parquet"
ARCHIVO_MODELO = MODELOS / "modelo_aprueba.joblib"

# Servicios. Los valores locales no contienen secretos; producción debe
# sobrescribirlos mediante variables de entorno.
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB = os.getenv("MONGODB_DB", "aprueba")
MONGODB_COLECCION = os.getenv("MONGODB_COLECCION", "predicciones")
S3_BUCKET_MODELOS = os.getenv("S3_BUCKET_MODELOS", "aprueba-modelos")
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "aprueba")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "aprueba")

# Estados finales: solo de estos préstamos sabemos cómo terminaron.
ESTADOS_BUENOS = ["Fully Paid", "Does not meet the credit policy. Status:Fully Paid"]
ESTADOS_MALOS = [
    "Charged Off",
    "Default",
    "Does not meet the credit policy. Status:Charged Off",
]

# Columnas conocidas AL MOMENTO DE LA SOLICITUD (sirven para el modelo).
COLUMNAS_SOLICITUD = {
    "loan_amnt": "float64",
    "term": "object",
    "int_rate": "float64",
    "installment": "float64",
    "grade": "object",
    "emp_length": "object",
    "home_ownership": "object",
    "annual_inc": "float64",
    "verification_status": "object",
    "purpose": "object",
    "dti": "float64",
    "fico_range_low": "float64",
    "earliest_cr_line": "object",
    "inq_last_6mths": "float64",
    "revol_util": "float64",
    "delinq_2yrs": "float64",
    "pub_rec_bankruptcies": "float64",
    "open_acc": "float64",
    "issue_d": "object",
}

# Columnas POSTERIORES al desembolso: nunca entran al modelo (fuga de datos).
# Solo se usan para medir el resultado económico de cada préstamo.
COLUMNAS_RESULTADO = {
    "loan_status": "object",
    "funded_amnt": "float64",
    "total_rec_prncp": "float64",
    "total_rec_int": "float64",
    "recoveries": "float64",
}

DTYPES = {**COLUMNAS_SOLICITUD, **COLUMNAS_RESULTADO}

# Variables que usa el modelo (todas conocidas al pedir el crédito).
VARIABLES_NUMERICAS = [
    "loan_amnt",
    "annual_inc",
    "dti",
    "fico_range_low",
    "antiguedad_credito_anios",
    "inq_last_6mths",
    "revol_util",
    "delinq_2yrs",
    "pub_rec_bankruptcies",
    "open_acc",
    "plazo_meses",
    "anios_empleo",
]
VARIABLES_CATEGORICAS = ["home_ownership", "verification_status", "purpose"]
VARIABLE_OBJETIVO = "es_malo"

# Mínimo de historial que el modelo vio en los datos (ver docs/decisiones.md).
ANTIGUEDAD_MINIMA_ANIOS = 3.0
