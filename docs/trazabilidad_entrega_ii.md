# Trazabilidad de la Entrega II

Estado revisado el 30 de octubre de 2026 contra los criterios de aceptación del backlog de la propuesta.

## Resumen

| Historia | Estado | Evidencia principal |
| --- | --- | --- |
| HU-01 — Ingesta Dask | Completa | `src/ingesta/ingesta_dask.py`, muestra y tiempos |
| HU-02 — Cosechas y MySQL | Completa | ventana Spark, 353 filas SQL e idempotencia |
| HU-03 — MongoDB y S3 | Completa | pruebas con `mongomock` y `moto` |
| HU-08 — Design Thinking y ROI | Completa en contenido | Entrevistas, síntesis, ROI y backlog actualizados |

## Criterios comprobados

### HU-01

- Tipos explícitos, bloques de 64 MB y filtrado de préstamos terminados.
- Parquet procesado y muestra versionada de 1,000 filas.
- Comparación Dask/Pandas registrada en `reports/tiempos_ingesta.json`.

### HU-02

- PySpark local con función de ventana acumulada por grado.
- Transformaciones y acciones identificadas en el código y la documentación.
- Tabla SQL con clave primaria `(cosecha, grado)`.
- Primera carga: 353 filas y 353 claves distintas.
- Segunda carga: el total permaneció en 353, demostrando idempotencia.
- Comparación de responsabilidades Spark/Dask documentada.

La instancia disponible fue MariaDB 10.4.32 de XAMPP, compatible con MySQL. La repetición contra Oracle MySQL 8 es opcional salvo que la rúbrica exija expresamente ese producto.

### HU-03

- MongoDB: Pydantic, `insert_one`, índice por fecha y consulta `$gt`.
- Pruebas MongoDB sin servidor real mediante `mongomock`.
- S3: `upload_file`, `download_file`, variables de entorno, `moto` y error 403.

### HU-08

- ROI y flujo de caja reproducibles a 12 y 24 meses.
- Supuestos escritos y marcados como ilustrativos.
- Guiones y plantilla ética de entrevistas preparados.
- Registro de decisiones y continuidad actualizado.

## Tareas sustantivas pendientes: 0

Los criterios funcionales y documentales del backlog de la Entrega II están cubiertos.

## Pendientes administrativos

- Resolver permisos de GitHub y publicar los commits locales.
- Repetir la prueba en Oracle MySQL 8 solo si la rúbrica no acepta MariaDB compatible.

## Bloqueo de publicación: 1

El commit `615a875` está en la rama local `entregable-ii`, pero GitHub rechazó el push porque la cuenta `aerivz` no tiene acceso de escritura a `OscarQ23/Aprueba-`. Esto no es una tarea funcional de la Entrega II, pero sí debe resolverse para entregar el trabajo remoto.
