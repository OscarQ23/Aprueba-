# Registro de decisiones

Una entrada por cada decisión técnica relevante: qué problema resuelve, qué alternativas se descartaron y por qué.

Plantilla:

```
## Decisión NNN: <título>
Fecha: AAAA-MM-DD · Estado: propuesta | aceptada | reemplazada
Contexto: ¿Qué problema obliga a decidir?
Alternativas: A) ... B) ... C) ...
Decisión: Se elige ... porque ... (argumentos y mediciones)
Consecuencias: ventajas, costos y riesgos asumidos.
```

---

## Decisión 001: Lending Club como fuente de datos

Fecha: 2026-10-25 · Estado: aceptada

**Contexto:** el proyecto necesita datos abiertos de riesgo crediticio, con volumen suficiente para justificar Dask y PySpark, y sin datos personales.

**Alternativas:** A) Credit Card Fraud de ULB (Kaggle). B) PaySim (fraude sintético en billetera móvil). C) Lending Club, préstamos aceptados 2007–2018.

**Decisión:** se elige C. Tiene 2,260,701 préstamos y 151 columnas con variables legibles (ingreso, deuda sobre ingreso, plazo, grado), lo que permite explicar cada decisión del modelo al usuario. A se descartó porque sus variables son componentes PCA sin significado. B se descartó porque es sintético y el fraude se detecta casi trivialmente con los saldos.

**Consecuencias:** hay que excluir las columnas que solo se conocen después del desembolso (pagos, recuperaciones) para evitar fuga de información. La población es de EE.UU., lo que limita la generalización a Centroamérica.

## Decisión 002: MySQL además de MongoDB

Fecha: 2026-10-25 · Estado: aceptada

**Contexto:** la guía exige MongoDB. El equipo quiere también MySQL.

**Alternativas:** A) Solo MongoDB para todo. B) MySQL para los indicadores agregados y MongoDB para la bitácora de solicitudes.

**Decisión:** se elige B. Los indicadores de mora por cosecha tienen estructura fija y se consultan con SQL; la bitácora guarda cada solicitud como documento JSON con motivos de longitud variable. Cada base guarda lo que mejor sabe guardar. El docente aceptó MySQL en clase siempre que se justifique.

**Consecuencias:** dos servicios de base de datos que levantar en el entorno de desarrollo.

## Decisión 003: descomprimir el `.gz` antes de leer con Dask

Fecha: 2026-10-30 · Estado: aceptada

**Contexto:** el dataset llega como `accepted_2007_to_2018Q4.csv.gz` (392 MB). Un archivo gzip no se puede leer por pedazos: hay que descomprimirlo desde el principio.

**Alternativas:** A) Leer el `.gz` directo con Dask (`blocksize=None`). B) Descomprimirlo una vez y leer el CSV con Dask en particiones de 64 MB.

**Decisión:** se elige B. Con A, Dask crea una sola partición y trabaja como Pandas, sin paralelismo. Con B, el CSV de unos 1.6 GB se divide en unas 25 particiones, que se reparten entre los núcleos de la laptop. La descompresión se hace una sola vez y queda en `data/interim/`.

**Consecuencias:** se necesitan unos 1.6 GB más de disco. El CSV descomprimido no se versiona.

## Decisión 004: el modelo no usa el grado ni la tasa de interés de Lending Club

Fecha: 2026-10-30 · Estado: aceptada

**Contexto:** `grade`, `sub_grade`, `int_rate` e `installment` los calcula Lending Club con su propio modelo de riesgo. Una financiera que adopte Aprueba+ no tendría esas columnas.

**Alternativas:** A) Usarlas como variables. B) Usar solo datos de la solicitud y del buró, y dejar el grado como línea base.

**Decisión:** se elige B. Así medimos si con datos que cualquier financiera tiene (ingreso, DTI, FICO, historial) se iguala o supera la regla por grado.

**Consecuencias:** la AUC puede quedar por debajo de la de un modelo que copie el grado; es un resultado honesto y se reporta tal cual.

## Decisión 005: red neuronal con `MLPClassifier` de scikit-learn

Fecha: 2026-10-30 · Estado: aceptada

**Contexto:** la guía pide una arquitectura de aprendizaje profundo coherente con los datos; para datos tabulares basta un MLP.

**Alternativas:** A) Keras/TensorFlow. B) `MLPClassifier` de scikit-learn.

**Decisión:** se elige B. Trae early stopping, regularización L2 (`alpha`) y la curva de pérdida por época, y usa el mismo `Pipeline` que los demás modelos. TensorFlow pesa cientos de MB y suele dar problemas de instalación en Windows.

**Consecuencias:** no hay dropout (no existe en `MLPClassifier`); la regularización se hace con `alpha` y early stopping.

## Decisión 006: el umbral de corte se elige por dinero

Fecha: 2026-10-30 · Estado: aceptada

**Contexto:** con 20 % de impagos, la exactitud engaña y el umbral 0.5 casi nunca marca a nadie como riesgoso.

**Alternativas:** A) Umbral 0.5. B) Umbral que maximiza F1. C) Umbral que maximiza el resultado económico real de la cartera aprobada.

**Decisión:** se elige C. Para cada umbral se simula "aprobar si la probabilidad es menor" sobre el conjunto de prueba y se suma lo que realmente dejó cada préstamo (intereses y capital recuperado menos lo desembolsado). La API aprueba por debajo de ese umbral, rechaza desde el umbral + 0.10 y manda a revisión lo que queda en medio.

**Consecuencias:** el resultado económico usa columnas posteriores al desembolso, pero solo para evaluar la política, nunca como variables del modelo.

## Decisión 007: clientes sin historial van a revisión manual

Fecha: 2026-10-30 · Estado: aceptada

**Contexto:** en el dataset todos los préstamos tienen score FICO (mínimo 625) y al menos 3 años de historial crediticio.

**Decisión:** si una solicitud llega sin FICO, sin antigüedad o con menos de 3 años de historial, la API no calcula probabilidad y responde "revisar" con el motivo. El modelo no debe opinar sobre perfiles que nunca vio.

**Consecuencias:** limitación declarada en el README; queda como trabajo futuro el uso de datos alternativos.

## Decisión 008: ejecución local de Spark en Windows sin `winutils.exe`

Fecha: 2026-10-30 · Estado: aceptada

**Contexto:** PySpark 3.5.3 funciona con JDK 17 para leer y calcular en Windows, pero el escritor local de Hadoop exige `winutils.exe`. Además, la ruta del proyecto contiene espacios y los scripts `.cmd` de PySpark no localizan correctamente el entorno virtual.

**Alternativas:** A) Mover o renombrar el proyecto. B) Descargar un `winutils.exe` de terceros. C) Crear temporalmente una unidad sin espacios y exportar el resultado agregado con Python después del cálculo Spark.

**Decisión:** se elige C. Los scripts crean temporalmente `P:` apuntando al proyecto. Todas las agrupaciones y ventanas se ejecutan en Spark; después se hace `collect` de las pocas filas mensuales agregadas y se escribe el CSV con la biblioteca estándar. No se incorpora un binario Hadoop no oficial solo para escribir un archivo pequeño.

**Consecuencias:** los scripts de Windows deben ejecutarse con permiso para crear la unidad virtual y para que Python se comunique con la JVM por `127.0.0.1`. La advertencia sobre `winutils.exe` aparece al iniciar Spark, pero no impide el flujo implementado. En Linux o en un clúster Spark no se necesita esta solución.
