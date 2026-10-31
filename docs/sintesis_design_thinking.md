# Síntesis de Design Thinking

## Fuentes

- `DT-01`: analista de crédito, perspectiva operativa de originación.
- `DT-02`: gerente de riesgos, perspectiva de política, pérdida y gobierno del modelo.

Las entrevistas están anonimizadas. Los valores numéricos reportados describen la experiencia de los participantes y no se consideran políticas universales ni estadísticas de cartera.

## Coincidencias principales

| Necesidad coincidente | Analista | Gerente | Decisión de producto |
| --- | --- | --- | --- |
| Tres posibles resultados | Aprobar, revisar o rechazar | Aprobación automática, revisión manual o rechazo | Mantener las tres decisiones en la API |
| Revisión humana para casos inciertos | Buró caído, fraude, monto alto e ingreso informal | Buró incompleto, antifraude, franja gris e ingresos no documentados | Ejecutar reglas de elegibilidad antes del modelo |
| Explicación comprensible | Tres motivos y alertas visibles | Códigos de razón y factores determinantes | Añadir códigos de razón de negocio mínimos |
| Integración sin copiar datos | Core o CRM del analista | API integrada al sistema de originación | Mantener FastAPI como interfaz de integración |
| Auditoría | Registro de lo validado por el analista | Datos, versión del modelo y dictamen | Registrar versión, entrada, salida y decisión final |
| El impago es más costoso | Trabajo de cobranza y castigo | Recuperación estimada de 15–20 % | Elegir umbral mediante pérdida esperada |

## Diferencias complementarias

### Perspectiva del analista

- Prioriza la calidad documental, la rapidez y la organización de casos pendientes.
- Opera bajo límites de autorización por monto.
- Necesita saber qué documento falta y por qué un caso se escaló.
- Evalúa la herramienta mediante tiempo ahorrado, acierto en revisiones y falsos rechazos.

### Perspectiva del gerente

- Define límites de DTI, excepciones, franjas de score y niveles de aprobación.
- Evalúa pérdida esperada y estabilidad de la cartera.
- Solicita Gini, mora temprana, PSI y trazabilidad de versiones.
- Distingue automatización, revisión manual y gobierno del modelo.

Las perspectivas no se contradicen: el gerente configura y monitorea la política; el analista ejecuta el proceso y gestiona excepciones.

## Recorrido objetivo de la solicitud

1. El core envía la solicitud a Aprueba+ mediante API.
2. Se valida presencia, formato y coherencia básica de los campos.
3. Se ejecutan reglas previas: buró disponible, identidad, antifraude, historial mínimo y capacidad para evaluar el ingreso.
4. Los casos fuera del dominio se envían a `REVISAR` con códigos de razón.
5. Los casos evaluables reciben probabilidad de impago y decisión según el umbral económico.
6. La respuesta incluye versión del modelo, razones de negocio y datos de auditoría.
7. Los casos manuales entran en la bandeja del analista.
8. La decisión final y el resultado posterior alimentan el monitoreo.

## Necesidades priorizadas

| Prioridad | Necesidad | Respuesta en el proyecto |
| --- | --- | --- |
| Alta | Evitar decisiones automáticas sin información confiable | Reglas de revisión manual y validación Pydantic |
| Alta | Integración rápida y sin copiar datos | FastAPI con respuesta síncrona |
| Alta | Auditoría de cada dictamen | MongoDB con fecha y versión del modelo |
| Alta | Punto de corte orientado a pérdida | Simulación económica por umbral |
| Media | Motivos comprensibles | Códigos de razón basados en reglas en el MVP |
| Media | Medir automatización y falsos rechazos | Métricas para documentación y trabajo futuro |
| Baja para el MVP | Explicabilidad SHAP completa | Pospuesta hasta estabilizar el modelo |
| Baja para el MVP | Monitoreo PSI y mora temprana en producción | Trabajo futuro por falta de cartera desplegada |

## Cambios derivados

1. La exclusión original de “motivos de cada decisión” se modifica: el MVP debe devolver códigos de razón para reglas y casos de revisión. SHAP completo sigue fuera del alcance inmediato.
2. El umbral económico usará una LGD preliminar de 82.5 %, punto medio de la recuperación reportada de 15–20 %.
3. Los límites mencionados —DTI, montos y score— se tratarán como parámetros de política por validar, no como constantes universales.
4. La bitácora deberá permitir incorporar la decisión final del analista cuando la API se integre al flujo completo.
5. AUC y recall permanecen como métricas del proyecto; Gini, falsos rechazos, automatización, mora temprana y PSI se añaden a la documentación de evaluación y monitoreo.

## Resultado de la fase de empatía

El concepto Aprueba+ queda validado como apoyo a decisiones, no como reemplazo absoluto del analista. La automatización aporta valor en casos claros y repetitivos; los casos con información incompleta, posible fraude, historial insuficiente o montos altos deben conservar intervención humana.
