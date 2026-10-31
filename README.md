# Aprueba+

**Aprueba más clientes buenos, pierde menos con los malos.**

Motor de decisión de crédito que estima la probabilidad de impago de una solicitud y sugiere aprobar, revisar o rechazar, con sus motivos principales.

> Proyecto Integrador — Bootcamp de Python para Ciencia de Datos, Módulo 4 (Big Data y MLOps).
> Estado: en construcción (Entrega II).

---

## 1. Problema y contexto de negocio

En una financiera de consumo, el analista de originación decide cada solicitud con reglas fijas y su propio criterio: la respuesta es lenta, inconsistente y cada impago es capital perdido.

En los datos que usamos, uno de cada cinco préstamos terminados se castigó (19.96 %), con 2,676 millones de USD de capital sin recuperar. Aun en el grado de riesgo C, el 22 % de los préstamos terminó castigado: la regla por grado no alcanza.

## 2. Solución y resultados clave

_Pendiente (Hito III): métricas del mejor modelo frente a la línea base, con gráficos._

## 3. Arquitectura

_Pendiente: diagrama y justificación de cada componente._

| Etapa | Tecnología |
| --- | --- |
| Ingesta y limpieza | Dask |
| Análisis de cosechas | PySpark (modo local) |
| Indicadores para el comité | MySQL |
| Bitácora de solicitudes | MongoDB |
| Almacén de artefactos | S3 simulado (moto) |
| Modelos | scikit-learn (`MLPClassifier` incluido) |
| Servicio | FastAPI |
| Contenedor | Docker |

### Estado de la Entrega II

| Historia | Estado comprobado |
| --- | --- |
| HU-01 — Ingesta Dask | Implementada; métricas heredadas y 1,000 filas de muestra |
| HU-02 — Cosechas PySpark/MySQL | Validada con 353 filas en MariaDB/MySQL de XAMPP; carga idempotente |
| HU-03 — MongoDB/S3 | Implementada y probada con `mongomock` y `moto` |
| HU-08 — Design Thinking y ROI | DT-01 y DT-02 sintetizadas; ROI y backlog actualizados |

## 4. Datos

- **Fuente:** [All Lending Club loan data](https://www.kaggle.com/datasets/wordsforthewise/lending-club) (Kaggle), préstamos aceptados de 2007 a 2018.
- **Tamaño:** 2,260,701 préstamos y 151 columnas (`accepted_2007_to_2018Q4.csv.gz`, 392 MB).
- **Licencia:** [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/) (dominio público).
- **Privacidad:** el dataset no trae nombres ni identificaciones; el código postal viene truncado a tres dígitos.

Los datos crudos **no se versionan**. Descarga el archivo desde Kaggle y colócalo en `data/raw/`.

## 5. Instalación y ejecución

```bash
git clone https://github.com/OscarQ23/Aprueba-.git
cd Aprueba-
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux / macOS
pip install -r requirements.txt
pytest
```

_Pendiente (Hito III): `docker build` y `docker run` de la API._

## 6. Uso de la API

_Pendiente (Hito III): ejemplo de petición y respuesta JSON; documentación en `/docs`._

## 7. Decisiones y trazabilidad

Cada decisión técnica se registra en [`docs/decisiones.md`](docs/decisiones.md).

El estado operativo, las validaciones y el siguiente paso para continuar la Entrega II se mantienen en [`docs/CONTINUIDAD_ENTREGA_II.md`](docs/CONTINUIDAD_ENTREGA_II.md).

Para evitar duplicar tareas, consultar [`docs/TRABAJO_REALIZADO_ENTREGA_II.md`](docs/TRABAJO_REALIZADO_ENTREGA_II.md) antes de iniciar cambios.

_Pendiente: tabla que vincula cada requisito de la guía con su archivo._

## 8. Limitaciones, riesgos éticos y trabajo futuro

_Pendiente._

## 9. Equipo

| Integrante | Rol |
| --- | --- |
| Oliver Ramírez | Coordinación del proyecto (Scrum Master) |
| Dafne Sol | Narrativa de datos (Product Owner) |
| Rolando Anaya | Ingeniería de datos |
| Luis Huezo | Ingeniería MLOps |
| Alvaro Rivas | Ciencia de datos |
| Oscar Quintanilla | Calidad y documentación |

## 10. Licencia, uso de IA y forma de citar

- Código bajo licencia [MIT](LICENSE).
- Uso de asistentes de IA: _pendiente de declarar (herramienta y para qué tarea)._

## Estructura del repositorio

Basada en [Cookiecutter Data Science](https://cookiecutter-data-science.drivendata.org/).

```
├── data/
│   ├── raw/          # Datos crudos (no versionados)
│   ├── interim/      # Datos intermedios (no versionados)
│   ├── processed/    # Datos listos para modelar (no versionados)
│   ├── external/     # Datos de terceros (no versionados)
│   └── muestra/      # Muestra mínima para pruebas (sí versionada)
├── docs/             # Documentación MkDocs y registro de decisiones
├── models/           # Artefactos pequeños de modelos
├── notebooks/        # Exploración y experimentos (.ipynb)
├── references/       # Diccionario de datos y material de apoyo
├── reports/figures/  # Gráficos para el README y la exposición
├── src/
│   ├── ingesta/         # Dask y PySpark
│   ├── almacenamiento/  # MySQL, MongoDB y S3 simulado
│   ├── modelos/         # Clases POO, ML y DL
│   ├── api/             # FastAPI
│   └── utils/
└── tests/            # Pruebas pytest
```
