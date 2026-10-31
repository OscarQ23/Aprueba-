# MongoDB y S3 simulado

HU-03 mantiene dos responsabilidades separadas:

- MongoDB registra cada decisión de la API como un documento validado.
- S3 conserva los artefactos del modelo fuera del código y bajo una clave versionada.

## Configuración

Copiar `.env.example` como `.env` y reemplazar los valores únicamente en el archivo local. `.env` está excluido de Git.

La aplicación reconoce:

- `MONGODB_URI`, `MONGODB_DB` y `MONGODB_COLECCION`.
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` y `AWS_REGION`.
- `S3_BUCKET_MODELOS` y, para servicios compatibles, `S3_ENDPOINT_URL`.

## Bitácora de predicciones

`src/almacenamiento/mongodb_predicciones.py` contiene:

- `RegistroPrediccion`, el esquema Pydantic que rechaza campos desconocidos, probabilidades fuera de `[0, 1]` y decisiones no válidas;
- `crear_indice_fecha`, que crea `idx_predicciones_fecha`;
- `registrar_prediccion`, que valida antes de llamar a `insert_one`;
- `consultar_predicciones_desde`, que usa `{"fecha": {"$gt": desde}}` y devuelve resultados en orden cronológico.

MongoDB guarda las fechas como UTC sin información de zona, que es la convención del controlador. Las fechas con zona se convierten a UTC antes de insertarlas o consultarlas.

## Modelos en S3

`src/almacenamiento/s3_modelos.py` usa `upload_file` y `download_file`. Una versión como `v1.2.0` y un archivo `modelo.joblib` producen la clave:

```text
modelos/v1.2.0/modelo.joblib
```

El código no crea el bucket automáticamente: la infraestructura debe prepararlo. Un error 403 se convierte en `PermissionError` con un mensaje que orienta a revisar credenciales y permisos.

## Pruebas sin servicios reales

```powershell
& '.\.venv\Scripts\python.exe' -m pytest tests/test_mongodb_predicciones.py tests/test_s3_modelos.py -q
```

Las pruebas usan `mongomock` y `moto`; no requieren MongoDB, AWS ni acceso a Internet durante su ejecución.
