# PySpark frente a Dask

## Responsabilidad de cada motor

Dask se usa para la ingesta: lee el CSV grande en particiones, aplica las transformaciones compartidas y escribe un Parquet limpio. PySpark se usa después para calcular la mora por cosecha y grado, incluido un acumulado cronológico mediante una función de ventana.

No se eligieron como motores intercambiables en todo el flujo. Cada uno resuelve una tarea acotada:

| Criterio | Dask | PySpark local |
| --- | --- | --- |
| Uso en Aprueba+ | Limpieza y CSV → Parquet | Indicadores por cosecha y grado |
| Modelo de ejecución | Grafo de tareas en procesos/hilos Python | Motor JVM con DataFrames SQL |
| Ventanas analíticas | Posibles, menos naturales entre particiones | `Window.partitionBy().orderBy()` nativa |
| Arranque | Ligero | Más costoso por la JVM |
| Entorno | Solo Python | Python, JDK y PySpark |
| Escalabilidad futura | Buena en una laptop y clúster Dask | Natural hacia un clúster Spark |

## Mediciones disponibles

La ingesta completa heredada reporta 1,347,734 préstamos terminados:

- Dask: 26 particiones, 26.3 segundos.
- Pandas: 28.9 segundos y aproximadamente 1,599 MB para el DataFrame crudo.

Estos tiempos proceden de `reports/tiempos_ingesta.json`. La medición comparable de Spark sobre el Parquet completo queda pendiente hasta disponer del dataset procesado en esta computadora. No es correcto comparar el tiempo de Spark sobre la muestra de 1,000 filas con la ingesta completa de Dask.

## Ejecución reproducible en Windows

El proyecto se encuentra en una ruta con espacios. Los scripts de PySpark para Windows no manejan correctamente esa ruta al localizar el entorno virtual. Los scripts del repositorio crean temporalmente la unidad `P:` apuntando a la raíz del proyecto y la eliminan al terminar si ellos la crearon.

Pruebas de Spark:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/test_spark.ps1
```

Análisis sobre la muestra:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/ejecutar_cosechas_spark.ps1 --entrada P:\data\muestra\muestra_prestamos.csv --salida P:\reports\mora_cosechas_spark.csv
```

Para persistir en MySQL, configurar `.env` y agregar `--mysql`. El resultado agregado se guarda en `mora_cosechas`, cuya clave primaria compuesta es `(cosecha, grado)`.

## Transformaciones y acciones

En `src/analisis/mora_cosechas_spark.py` se señalan explícitamente:

- transformaciones perezosas: `select`, `filter`, `groupBy`, agregaciones y columnas de ventana;
- acción: `collect` del resultado ya agregado antes de escribir un CSV o enviarlo a MySQL.

El `collect` no opera sobre los préstamos individuales, sino sobre unas pocas filas por combinación de mes y grado. El CSV final se escribe con la biblioteca estándar de Python porque el escritor local de Hadoop requiere `winutils.exe` en Windows; no se incorporó ese binario no oficial solo para exportar un resultado pequeño.
