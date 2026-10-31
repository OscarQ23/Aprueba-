# Trabajo realizado — Entrega II

Este documento informa al equipo qué trabajo ya está implementado y validado en la rama `entregable-ii`, para evitar duplicarlo. Antes de iniciar una tarea relacionada, revisar los archivos y evidencias indicados aquí.

## Resumen ejecutivo

Las historias HU-01, HU-02, HU-03 y HU-08 están cubiertas funcional y documentalmente. La suite normal registra `23 passed, 1 skipped`; la prueba omitida corresponde a Spark y se ejecuta mediante su script dedicado.

La rama `entregable-ii` está publicada y sincronizada con el remoto hasta el commit `709653e`. El hash local y `origin/entregable-ii` fue verificado directamente.

## Trabajo completado

### HU-01 — Ingesta con Dask

Ya existe:

- descompresión controlada del CSV gzip;
- lectura con tipos explícitos y bloques de 64 MB;
- filtrado de préstamos terminados;
- variables derivadas y limpieza compartida;
- salida Parquet;
- comparación Dask frente a Pandas;
- muestra reproducible de 1,000 filas.

Archivos principales:

- `src/ingesta/ingesta_dask.py`
- `src/utils/transformaciones.py`
- `src/config.py`
- `data/muestra/muestra_prestamos.csv`
- `reports/tiempos_ingesta.json`

Resultado registrado: 1,347,734 préstamos terminados, 26 particiones y 26.3 segundos con Dask.

### HU-02 — PySpark y persistencia SQL

Ya existe:

- análisis de mora por cosecha y grado;
- función de ventana acumulada por grado;
- transformaciones y acciones identificadas en el código;
- exportación CSV agregada;
- tabla `mora_cosechas` con clave primaria `(cosecha, grado)`;
- `upsert` por lotes de 100 filas;
- scripts PowerShell para resolver la ruta de Windows con espacios;
- comparación documentada de Spark y Dask.

Archivos principales:

- `src/analisis/mora_cosechas_spark.py`
- `scripts/ejecutar_cosechas_spark.ps1`
- `scripts/test_spark.ps1`
- `tests/test_mora_cosechas_spark.py`
- `reports/mora_cosechas_spark.csv`
- `docs/spark_vs_dask.md`

Validación real en MariaDB/MySQL de XAMPP:

- 353 filas y 353 claves distintas;
- tasa de mora dentro de `[0, 1]`;
- segunda carga mantuvo 353 filas, sin duplicados;
- escritura idempotente confirmada.

### HU-03 — MongoDB y S3 simulado

Ya existe:

- esquema Pydantic para validar predicciones;
- inserción `insert_one`;
- índice por fecha;
- consulta con `$gt`;
- pruebas con `mongomock`;
- carga y descarga de modelos mediante `upload_file` y `download_file`;
- claves versionadas en S3;
- manejo explícito de error 403;
- pruebas con `moto` sin utilizar una cuenta real.

Archivos principales:

- `src/almacenamiento/mongodb_predicciones.py`
- `src/almacenamiento/s3_modelos.py`
- `tests/test_mongodb_predicciones.py`
- `tests/test_s3_modelos.py`
- `docs/almacenamiento.md`
- `.env.example`

### HU-08 — Design Thinking y ROI

Ya existe:

- entrevista DT-01 con analista de crédito;
- entrevista DT-02 con gerente de riesgos;
- fecha: 26 de octubre de 2026;
- entrevistadora: Dafne Sol;
- duración: 60 minutos por entrevista;
- consentimiento para notas anonimizadas: aceptado;
- síntesis comparativa de ambos perfiles;
- backlog actualizado según hallazgos;
- decisiones técnicas 009 y 010;
- modelo reproducible de ROI a 12 y 24 meses;
- flujo de caja y resumen JSON regenerados.

Archivos principales:

- `docs/entrevistas/DT-01_analista_credito.md`
- `docs/entrevistas/DT-02_gerente_riesgos.md`
- `docs/sintesis_design_thinking.md`
- `docs/backlog_actualizado.md`
- `docs/roi_flujo_caja.md`
- `src/analisis/roi.py`
- `reports/flujo_caja_24_meses.csv`
- `reports/roi_resumen.json`

Escenario ROI v0.2:

| Horizonte | Beneficio bruto | Costo total | Flujo neto | ROI |
| --- | ---: | ---: | ---: | ---: |
| 12 meses | USD 71,280 | USD 27,000 | USD 44,280 | 164.0 % |
| 24 meses | USD 142,560 | USD 39,000 | USD 103,560 | 265.5 % |

La LGD de 82.5 % usa el punto medio de la recuperación de 15–20 % reportada en DT-02. Los demás valores continúan como supuestos preliminares.

## Decisiones ya tomadas

No repetir estas discusiones sin evidencia nueva:

1. El modelo no usa grado ni tasa de Lending Club como predictores.
2. El umbral se elige por pérdida económica, no por 0.5.
3. Los perfiles sin historial suficiente van a revisión manual.
4. MongoDB conserva la bitácora; MySQL conserva indicadores agregados.
5. `MLPClassifier` sustituye TensorFlow para la red neuronal tabular.
6. En Windows, Spark usa una unidad temporal `P:` y no depende de `winutils.exe` para escribir el reporte agregado.
7. El MVP incorpora códigos de razón para reglas; SHAP completo queda como trabajo futuro.
8. Los límites de DTI, score y monto mencionados en entrevistas son configurables y no reglas universales.

Ver detalles en `docs/decisiones.md`.

## Pruebas y comandos

Suite normal:

```powershell
& '.\.venv\Scripts\python.exe' -m pytest -q
```

Resultado más reciente:

```text
23 passed, 1 skipped
```

Integración Spark:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/test_spark.ps1
```

Regenerar ROI:

```powershell
& '.\.venv\Scripts\python.exe' -m src.analisis.roi
```

## Qué no debe duplicarse

- No crear otra ingesta Dask ni otra muestra de pruebas.
- No implementar nuevamente la ventana Spark de cosechas.
- No crear una segunda tabla SQL para los mismos indicadores.
- No crear módulos alternativos para MongoDB o S3.
- No repetir las entrevistas DT-01 y DT-02.
- No crear otro cálculo de ROI sin revisar el modelo existente.
- No incorporar TensorFlow; la decisión aceptada es `MLPClassifier`.
- No codificar como constantes universales los umbrales mencionados en entrevistas.

Si se requiere modificar cualquiera de estas partes, actualizar primero `docs/decisiones.md` y este documento.

## Pendientes reales

### Publicación

- Los cuatro commits funcionales y documentales de la Entrega II ya están publicados.
- Este resumen y sus enlaces en README/MkDocs se publican juntos en un commit documental; consultar `git log -1` para identificarlo.

### Condicional

- Repetir la validación SQL en Oracle MySQL 8 únicamente si la rúbrica no acepta MariaDB de XAMPP.

### Siguiente entrega

Las tareas de modelos, API, Docker y documentación final corresponden a la Entrega III; revisar `docs/backlog_actualizado.md` antes de iniciarlas.

## Commits previos publicados en `entregable-ii`

```text
615a875 feat(entrega-ii): completar HU-02, HU-03 y ROI
a38b39f fix(mysql): escribir indicadores por lotes
4689732 feat(negocio): sintetizar entrevistas y ROI
709653e docs(entrevistas): completar metadatos
```

Antes de incorporar este resumen, se verificó que `origin/entregable-ii` apuntaba a `709653e`.

## Documentos de continuidad

- `docs/CONTINUIDAD_ENTREGA_II.md`: bitácora técnica detallada y cronológica.
- `docs/trazabilidad_entrega_ii.md`: criterios de aceptación y evidencia.
- `docs/backlog_actualizado.md`: cambios derivados de las entrevistas.
- `docs/decisiones.md`: decisiones técnicas aceptadas.
