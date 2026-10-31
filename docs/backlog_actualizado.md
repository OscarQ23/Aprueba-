# Backlog actualizado después de las entrevistas

Este documento registra cambios al backlog original sin borrar la propuesta aprobada.

## Cambios aceptados para el MVP

| Historia | Cambio de criterio de aceptación | Evidencia |
| --- | --- | --- |
| HU-03 | La bitácora conserva versión del modelo, probabilidad, decisión y motivos; la decisión final del analista se añadirá al integrar la API | DT-01 y DT-02 solicitan auditoría |
| HU-05 | Antes de puntuar, validar información mínima y devolver `revisar` cuando no exista buró, historial o ingreso verificable | Ambos perfiles prohíben automatizar casos incompletos |
| HU-05 | La respuesta incluye códigos de razón de negocio para reglas y revisión manual | Ambos perfiles rechazan una caja negra |
| HU-06 | La simulación permite parametrizar LGD y usa 82.5 % como escenario preliminar | DT-02 reporta recuperación de 15–20 % |
| HU-07 | Documentar tasa de automatización, falsos rechazos y Gini junto con AUC, recall y F1 | Indicadores solicitados en entrevistas |
| HU-08 | Incorporar DT-01, DT-02 y síntesis; actualizar ROI y decisiones | Cierre de Design Thinking |

## Criterios que permanecen

- API con `/v1/health` y `/v1/predict`.
- Salidas aprobar, revisar y rechazar.
- MongoDB como bitácora y S3 simulado como almacén del modelo.
- Umbral elegido por resultado económico.
- Pruebas sin depender de servicios reales.

## Trabajo futuro, fuera del MVP

| Candidato | Motivo de aplazamiento |
| --- | --- |
| Valores SHAP y tres factores del modelo por solicitud | Añade dependencia y complejidad; primero debe estabilizarse el modelo |
| Bandeja gráfica de casos manuales | La propuesta excluye interfaz; la API entregará los datos necesarios |
| PSI automatizado y alertas de deriva | Requiere datos de producción posteriores al despliegue |
| FPD y Ever 30/60 | Requieren maduración de cosechas reales |
| Reglas OFAC, PEP y antifraude reales | Requieren fuentes externas y políticas institucionales |

## Parámetros por validar, no codificar como constantes

- DTI general de 45 % y excepciones hasta 50 %.
- Scores de 620–720 como franja gris y score superior a 780 para excepciones.
- Montos de USD 10,000, USD 15,000 y USD 25,000.
- Historial mínimo de doce meses frente al mínimo inicial de tres años.

Estos valores se documentan como evidencia de entrevistas. Una financiera usuaria deberá configurarlos conforme a su política y población.
