# Continuidad de trabajo — Entrega II

Este documento permite que otra persona o IA retome el proyecto sin reconstruir el contexto. Debe actualizarse después de cada bloque de trabajo con hechos comprobados, decisiones, archivos modificados, validaciones y el siguiente paso exacto.

## 1. Objetivo de la Entrega II

Completar y documentar el primer incremento funcional de Aprueba+ correspondiente al Sprint 1:

- HU-01: ingesta reproducible del dataset con Dask y salida Parquet.
- HU-02: análisis de mora por cosecha y grado con PySpark, con salida preparada para MySQL.
- HU-03: bitácora de predicciones en MongoDB y almacén de modelos en S3 simulado.
- HU-08: evidencia de Design Thinking, supuestos de ROI y flujo de caja, y bitácora de hallazgos y decisiones.

El alcance definitivo debe contrastarse con la guía o rúbrica oficial cuando esté disponible en el repositorio.

## 2. Estado del repositorio al iniciar

- Fecha de revisión: 2026-10-30.
- Repositorio oficial: `https://github.com/OscarQ23/Aprueba-.git`.
- Rama de trabajo existente: `entregable-ii`.
- Commit inicial de esta sesión: `4675d27` (`Ingesta con Dask: CSV de Lending Club a Parquet limpio`).
- El directorio local estaba vacío salvo por un repositorio Git sin commits; se vinculó con el repositorio oficial y se descargó la rama `entregable-ii`.
- No existe `.codegraph/`; para explorar el código se usaron las herramientas normales del repositorio.

## 3. Inventario comprobado

### Implementado

- Estructura tipo Cookiecutter Data Science.
- Configuración centralizada en `src/config.py`.
- Ingesta en `src/ingesta/ingesta_dask.py`:
  - descompresión del CSV gzip;
  - lectura Dask con tipos explícitos y bloques de 64 MB;
  - filtrado de préstamos terminados;
  - escritura a Parquet;
  - comparación de tiempo con Pandas;
  - generación de una muestra reproducible.
- Transformaciones compartidas en `src/utils/transformaciones.py`.
- Pruebas unitarias de estructura y transformaciones.
- Muestra versionada de 1,000 préstamos en `data/muestra/muestra_prestamos.csv`.
- Registro de siete decisiones técnicas en `docs/decisiones.md`.

### Resultados heredados registrados

El archivo `reports/tiempos_ingesta.json` reporta:

| Motor | Filas | Tiempo | Dato adicional |
| --- | ---: | ---: | --- |
| Dask | 1,347,734 | 26.3 s | 26 particiones |
| Pandas | 1,347,734 | 28.9 s | 1,599 MB del DataFrame crudo |

Estos valores fueron leídos del repositorio; todavía no se reprodujeron en esta computadora porque el dataset completo no está versionado.

### Pendiente o no comprobado

- HU-02, HU-03 y HU-08 no tienen implementación visible todavía.
- No se encontró la guía o rúbrica oficial dentro del repositorio.
- La ingesta completa no puede reproducirse hasta disponer del CSV original de Lending Club.
- No se ha validado la ingesta contra el dataset completo en esta computadora.
- El README todavía muestra el proyecto como “Hito I” y contiene referencias antiguas a Keras.

## 4. Criterios técnicos que deben preservarse

- No usar variables posteriores al desembolso como entrada del modelo.
- `grade`, `sub_grade`, `int_rate` e `installment` no deben entrar al modelo; el grado se conserva como línea base y para análisis.
- Las columnas de resultado económico pueden usarse para evaluar políticas, nunca como predictores.
- Los perfiles sin suficiente historial crediticio deben enviarse a revisión manual.
- No versionar el dataset completo, credenciales, artefactos pesados ni archivos `.env`.
- Mantener pruebas independientes de servicios reales mediante mocks o simuladores.

## 5. Plan operativo sugerido

1. Preparar un entorno virtual e instalar las dependencias necesarias para ejecutar las pruebas existentes.
2. Corregir cualquier fallo de la base heredada antes de añadir componentes.
3. Implementar HU-02 con una ruta que también pueda probarse sobre `data/muestra/`.
4. Implementar HU-03 separando MongoDB y S3 en módulos pequeños y probables.
5. Crear los artefactos documentales de HU-08 con supuestos explícitos, sin inventar entrevistas.
6. Actualizar README, decisiones, trazabilidad de requisitos y esta bitácora.
7. Ejecutar pruebas y documentar exactamente qué se verificó y qué queda condicionado a servicios o datos externos.

## 6. Registro cronológico

### Sesión 2026-10-30 — Preparación

**Solicitud del usuario:** trabajar la fase o Entrega II y mantener un Markdown para que otra IA pueda continuar.

**Acciones realizadas:**

1. Se inspeccionó el directorio local y se confirmó que solo contenía `.git` sin commits.
2. Se verificó el repositorio indicado en la propuesta.
3. Se vinculó `origin`, se descargaron las ramas remotas y se activó `entregable-ii`.
4. Se revisaron README, documentación, código, pruebas, requisitos, muestra y métricas de ingesta.
5. Se intentó ejecutar `pytest -q`; el comando no existe en el entorno actual.
6. Se creó este documento de continuidad.

**Archivos modificados en esta sesión:**

- `docs/CONTINUIDAD_ENTREGA_II.md` — creado.

**Continuación de la sesión:**

7. Se encontró que `python` en `PATH` apuntaba a `C:\Program Files\Inkscape\bin\python.exe` (Python 3.12.9), un intérprete inadecuado para el proyecto.
8. Se localizó la instalación normal en `C:\Users\alvar\AppData\Local\Programs\Python\Python312\python.exe` (Python 3.12.8).
9. Se creó `.venv` con esa instalación. `ensurepip` falló inicialmente porque el sandbox no permitía escribir en la carpeta temporal global; se resolvió usando `.tmp` dentro del proyecto como `TEMP` y `TMP` durante el comando.
10. Se instalaron en `.venv` las dependencias mínimas `pytest==8.3.3`, `pandas==2.2.3` y `numpy==1.26.4`.
11. Se ejecutó `& '.\.venv\Scripts\python.exe' -m pytest -q` con resultado `11 passed in 0.96s`.

**Entorno local validado:**

- Intérprete del proyecto: `.venv\Scripts\python.exe`.
- Versión: Python 3.12.8.
- No confiar en el comando desnudo `python` en esta computadora: puede resolver al Python de Inkscape.
- Para operaciones que usan archivos temporales dentro del sandbox, crear `.tmp` y asignar temporalmente `TEMP` y `TMP` a esa ruta.

**Próximo paso exacto:**

Revisar Java y PySpark; instalar las dependencias de HU-02 si faltan. Implementar el análisis de mora por cosecha y grado sobre la muestra versionada, con una función de ventana explícita, salida determinista y pruebas.

### Sesión 2026-10-30 — HU-03 MongoDB y S3 simulado

**Estado de entrada:** la base heredada tenía 11 pruebas aprobadas. No existía implementación en `src/almacenamiento/`. Se comprobó que Java no está instalado y que PySpark tampoco está presente, por lo que HU-02 no podía ejecutarse localmente en este momento.

**Acciones realizadas:**

1. Se cambió el orden de trabajo para avanzar HU-03 mientras se resuelve el requisito de Java de HU-02.
2. Se instalaron en `.venv` las versiones ya fijadas en `requirements.txt`: Pydantic, PyMongo, boto3, moto y mongomock.
3. Se implementó la bitácora MongoDB con validación Pydantic, `insert_one`, índice por fecha y consulta `$gt`.
4. Se implementó el almacén S3 con `upload_file`, `download_file`, claves por versión, variables de entorno y manejo explícito de 403.
5. Se añadieron pruebas aisladas con `mongomock`, `moto` y un cliente simulado para el error 403.
6. El primer intento de las nuevas pruebas produjo `14 passed, 2 errors`: los dos errores ocurrieron en la preparación de `tmp_path` por la carpeta temporal global bloqueada, no en el código de HU-03.
7. Se añadió `pytest.ini` con `--basetemp=.tmp/pytest` y `.tmp/` a `.gitignore`.
8. Se añadió `.env.example` sin secretos y documentación en `docs/almacenamiento.md`.
9. En revisión se detectó que `datetime.UTC` y la unión `A | B` no son compatibles con Python 3.9, versión mínima declarada por el proyecto; se sustituyeron por `timezone.utc` y `typing.Union`.

**Archivos modificados:**

- `.env.example`
- `.gitignore`
- `pytest.ini`
- `README.md`
- `mkdocs.yml`
- `src/config.py`
- `src/almacenamiento/mongodb_predicciones.py`
- `src/almacenamiento/s3_modelos.py`
- `tests/test_mongodb_predicciones.py`
- `tests/test_s3_modelos.py`
- `docs/almacenamiento.md`
- `docs/CONTINUIDAD_ENTREGA_II.md`

**Validaciones ejecutadas y resultado:**

- Suite completa: `16 passed, 4 warnings in 2.46s`.
- Las advertencias provienen de `botocore` por el uso interno de `datetime.utcnow()`; no afectan la lógica del proyecto.
- Las pruebas no contactaron MongoDB ni AWS reales.

**Bloqueos o supuestos pendientes:**

- HU-02 sigue bloqueada para ejecución local porque el comando `java` no existe.
- HU-03 todavía no está integrada a la futura API; esta integración corresponde a la historia de la API.
- El bucket S3 debe existir antes de usar los módulos contra infraestructura real.

**Próximo paso exacto:**

Revisar los cambios de HU-03 y volver a ejecutar la suite. Después decidir entre: instalar/configurar un JDK para HU-02 o avanzar los artefactos verificables de HU-08 sin inventar resultados de entrevistas.

### Sesión 2026-10-30 — HU-08 ROI y preparación de entrevistas

**Estado de entrada:** HU-03 estaba implementada y la suite completa tenía 16 pruebas aprobadas. HU-02 seguía sin poder ejecutarse por ausencia de Java.

**Acciones realizadas:**

1. Se creó `src/analisis/roi.py`, un modelo configurable de ROI y flujo de caja que no depende de hojas de cálculo manuales.
2. Se definió un escenario ilustrativo v0.1 con todos los supuestos visibles y validaciones de rango.
3. Se generaron `reports/flujo_caja_24_meses.csv` y `reports/roi_resumen.json` con cortes a 12 y 24 meses.
4. Se documentaron fórmula, supuestos, resultados y limitaciones en `docs/roi_flujo_caja.md`.
5. Se creó `docs/design_thinking.md` con guiones para analista y gerente de riesgo, una plantilla de evidencia y la advertencia explícita de que aún no se han registrado entrevistas.
6. Se añadieron cuatro pruebas del cálculo y exportación del ROI.
7. Se buscaron instalaciones de Java en ubicaciones comunes de Java, Eclipse Adoptium, Microsoft JDK, Amazon Corretto y `.jdks`; no se encontró ninguna.

**Archivos modificados:**

- `src/analisis/__init__.py`
- `src/analisis/roi.py`
- `tests/test_roi.py`
- `docs/roi_flujo_caja.md`
- `docs/design_thinking.md`
- `reports/flujo_caja_24_meses.csv`
- `reports/roi_resumen.json`
- `mkdocs.yml`
- `docs/CONTINUIDAD_ENTREGA_II.md`

**Validaciones ejecutadas y resultado:**

- Generación del informe: correcta; flujo neto ilustrativo de USD 33,480 a 12 meses y USD 81,960 a 24 meses.
- Suite completa: `20 passed, 4 warnings in 3.06s`.
- Comprobación de sintaxis: los 11 archivos Python que existían al cierre de HU-03 se analizaron correctamente con la gramática de Python 3.9. Después se añadió `src/analisis/roi.py`; debe incluirse en la siguiente comprobación antes de cerrar cambios.
- Validación final de la sesión: `20 passed, 4 warnings in 2.27s`; los 13 archivos de `src/` son compatibles con la gramática de Python 3.9 y `git diff --check` no reportó errores.

**Bloqueos o supuestos pendientes:**

- Los valores del ROI son ilustrativos y deben reemplazarse con evidencia del negocio y resultados del modelo.
- Las entrevistas requieren participantes humanos; no deben rellenarse con contenido generado.
- HU-02 necesita un JDK compatible con PySpark 3.5.3. No hay uno instalado ni localizable en las rutas comunes revisadas.

**Próximo paso exacto:**

Obtener autorización para instalar o usar un JDK local, instalar PySpark en `.venv` y ejecutar una sesión Spark mínima. Después implementar HU-02 sobre `data/muestra/muestra_prestamos.csv`, añadir pruebas y documentar la comparación Spark frente a Dask.

### Sesión 2026-10-30 — HU-02 PySpark, cosechas y MySQL

**Estado de entrada:** el usuario autorizó instalar y configurar Java. HU-02 no tenía código y no existía un JDK en el equipo.

**Acciones realizadas:**

1. Winget confirmó e instaló Eclipse Temurin JDK `17.0.20.1` en `C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot`.
2. Se instalaron `pyspark==3.5.3` y `mysql-connector-python==9.1.0` en `.venv`.
3. La primera sesión Spark se bloqueó al usar la carpeta temporal global restringida; se corrigió configurando `TEMP` y `TMP` dentro de `.tmp`.
4. PySpark no manejó correctamente la ruta del proyecto con espacios. Se creó temporalmente la unidad `P:` apuntando a la raíz y se añadieron scripts PowerShell que automatizan esa configuración.
5. Se comprobó Spark 3.5.3 con JDK 17 mediante un cálculo JVM: suma de 1 a 5 igual a 15.
6. Se implementó `src/analisis/mora_cosechas_spark.py` con lectura CSV/Parquet, agregación por cosecha y grado, función de ventana acumulada, exportación CSV y persistencia MySQL opcional.
7. La tabla `mora_cosechas` usa clave primaria compuesta `(cosecha, grado)` y un `upsert` idempotente.
8. El primer diseño de prueba creó el DataFrame desde una lista Python; los ejecutores fallaron por la ruta virtual. Se cambió la prueba para leer un CSV, que es el mismo recorrido usado por producción.
9. La integración reveló que `inferSchema` convertía `YYYY-MM` a fecha. Se eliminó la inferencia y se añadieron conversiones explícitas por nombre de columna.
10. El escritor CSV de Hadoop falló por ausencia de `winutils.exe`. Se decidió no descargar un binario no oficial: Spark calcula y colecta únicamente el resultado agregado; Python escribe el CSV final.
11. Se documentó la comparación de responsabilidades y mediciones de Spark/Dask en `docs/spark_vs_dask.md`.
12. Se ejecutó el análisis sobre `data/muestra/muestra_prestamos.csv`: 353 combinaciones cosecha–grado en 14.75 segundos, guardadas en `reports/mora_cosechas_spark.csv`.

**Archivos modificados:**

- `.env.example`
- `src/config.py`
- `src/analisis/mora_cosechas_spark.py`
- `tests/test_mora_cosechas_spark.py`
- `scripts/test_spark.ps1`
- `scripts/ejecutar_cosechas_spark.ps1`
- `docs/spark_vs_dask.md`
- `docs/decisiones.md`
- `reports/mora_cosechas_spark.csv`
- `README.md`
- `mkdocs.yml`
- `docs/CONTINUIDAD_ENTREGA_II.md`

**Validaciones ejecutadas y resultado:**

- Integración dedicada de Spark: `3 passed in 11.77s`.
- Prueba final desde un estado sin unidad `P:`: `3 passed in 16.08s`; el script creó y retiró la unidad temporal correctamente.
- Suite normal: `22 passed, 1 skipped, 4 warnings in 2.68s`. La prueba omitida es la integración Spark, que se ejecuta por separado mediante `scripts/test_spark.ps1`.
- Reporte de muestra: 353 filas; `tasa_mora` dentro del rango `[0, 1]`.
- `git diff --check`: sin errores.

**Bloqueos o supuestos pendientes:**

- No hay servidor MySQL real en esta sesión. El DDL, la clave primaria, el `upsert` y la transacción están probados con mocks; falta una prueba contra una instancia real o contenedor.
- La medición Spark de 14.75 segundos corresponde a la muestra de 1,000 filas y no debe compararse con los 26.3 segundos de Dask sobre 1,347,734 filas.
- La ejecución sobre el Parquet completo requiere que el dataset procesado esté disponible localmente.
- Spark muestra una advertencia por ausencia de `winutils.exe`, pero el flujo elegido no depende de ese ejecutable.

**Próximo paso exacto:**

Levantar o identificar una instancia MySQL de prueba, ejecutar HU-02 con `--mysql` y comprobar las 353 filas mediante una consulta SQL. Después completar las entrevistas reales de HU-08 y reemplazar los supuestos ilustrativos del ROI.

## 7. Plantilla para próximas actualizaciones

Copiar este bloque al final del registro cronológico:

```markdown
### Sesión AAAA-MM-DD — <objetivo>

**Estado de entrada:**

**Acciones realizadas:**

**Decisiones y motivo:**

**Archivos modificados:**

**Validaciones ejecutadas y resultado:**

**Bloqueos o supuestos pendientes:**

**Próximo paso exacto:**
```
