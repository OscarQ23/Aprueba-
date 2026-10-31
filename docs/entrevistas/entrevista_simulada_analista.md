# Entrevista simulada — Analista de crédito

> **Estado: simulación para preparación.** No corresponde a una entrevista realizada con una persona real y no debe presentarse como evidencia de campo. Las respuestas deben validarse o reemplazarse durante una conversación con un analista de crédito.

## Ficha de la sesión

- Código: `SIM-DT-01`
- Perfil representado: analista de crédito de una financiera de consumo
- Región de referencia: Centroamérica
- Modalidad: simulación escrita
- Objetivo: anticipar necesidades, refinar el guion y detectar supuestos que deben validarse
- Datos personales o empresariales utilizados: ninguno

## Introducción sugerida

Gracias por participar. Queremos entender cómo se evalúan actualmente las solicitudes de crédito y qué información necesitaría un analista para utilizar una recomendación automatizada. No solicitaremos nombres de clientes, expedientes, políticas confidenciales ni datos identificables de la empresa. La conversación durará aproximadamente 20 minutos.

## Entrevista

### 1. ¿Cómo llega una solicitud de crédito y qué revisa primero?

**Respuesta simulada:** La solicitud llega con los datos personales, empleo, ingresos, monto solicitado y autorización para consultar el buró. Primero verifico que los documentos coincidan y que no falte información. Después reviso el score, el nivel de endeudamiento, la estabilidad laboral y el historial de pagos. Si hay inconsistencias, detengo el análisis y pido una aclaración.

### 2. ¿Qué información suele faltar o generar más dudas?

**Respuesta simulada:** Lo más común es que el ingreso declarado no coincida con los documentos o que una persona con actividad informal no pueda demostrar ingresos estables. También genera dudas un historial crediticio muy corto, varias consultas recientes o referencias laborales difíciles de confirmar.

### 3. ¿Cuánto tarda una decisión sencilla y una compleja?

**Respuesta simulada:** Una solicitud completa y de bajo riesgo puede tomar entre 15 y 25 minutos. Una solicitud con documentos faltantes, poco historial o señales contradictorias puede quedar pendiente durante varias horas o hasta el día siguiente.

### 4. ¿En qué casos debe escalar la decisión?

**Respuesta simulada:** Escalo cuando el monto supera mi límite de autorización, cuando el endeudamiento está cerca del máximo permitido, cuando hay atrasos anteriores o cuando el cliente tiene capacidad de pago, pero el score no es suficiente. También escalo casos donde una regla indica rechazo, pero existe información adicional que podría justificar una excepción.

### 5. ¿Qué explicación necesita comunicar al cliente?

**Respuesta simulada:** No basta con decir que el sistema rechazó la solicitud. Necesito explicar los factores generales, por ejemplo, endeudamiento alto, historial insuficiente o demasiadas consultas recientes. La explicación debe ser breve, respetuosa y no revelar reglas internas que puedan manipularse.

### 6. ¿Qué resulta más costoso: aprobar un cliente que no pagará o rechazar uno bueno?

**Respuesta simulada:** Aprobar un cliente que cae en mora suele tener un costo inmediato mayor porque se pierde capital y tiempo de cobranza. Sin embargo, rechazar demasiados clientes buenos reduce ventas y puede afectar la reputación. La decisión debe equilibrar ambas pérdidas; no conviene usar una política que solamente minimice la mora.

### 7. ¿Qué tendría que mostrar Aprueba+ para que confíe en su recomendación?

**Respuesta simulada:** Necesitaría ver la probabilidad de impago, la decisión sugerida y dos o tres factores principales. También debe mostrar si falta información y permitir enviar el caso a revisión manual. Para confiar en el sistema, tendría que saber que fue probado con datos históricos y que las decisiones quedan registradas para auditoría.

### 8. ¿Cómo debería integrarse la herramienta en su trabajo diario?

**Respuesta simulada:** Lo ideal es que esté integrada al sistema donde ya reviso las solicitudes. No quiero copiar datos entre pantallas. Los casos claros deberían resolverse rápido y los casos de revisión deberían aparecer en una bandeja ordenada por prioridad, con la información que necesita ver el comité.

### 9. ¿En qué situaciones no permitiría una decisión automática?

**Respuesta simulada:** No la permitiría cuando falta el score, hay muy poco historial, los documentos no coinciden, existe una alerta de fraude o el monto requiere autorización superior. En esos casos la herramienta debería decir “revisar”, no intentar adivinar.

### 10. ¿Qué indicador usaría para evaluar si la herramienta funciona?

**Respuesta simulada:** Mediría el tiempo promedio de respuesta, la tasa de aprobación, la mora de las nuevas cosechas y cuántas decisiones se envían a revisión. También compararía las recomendaciones del sistema con las decisiones finales del comité y revisaría los falsos rechazos.

## Hallazgos hipotéticos que deben validarse

| Hallazgo hipotético | Impacto en Aprueba+ | Pregunta de validación real |
| --- | --- | --- |
| Los casos simples consumen entre 15 y 25 minutos | La API puede reducir tiempo operativo | ¿Cuál es el tiempo medido actualmente? |
| Ingresos inconsistentes e historial corto generan la mayoría de dudas | Se necesitan validaciones y revisión manual | ¿Qué porcentaje de solicitudes presenta estos problemas? |
| Una probabilidad sin explicación no genera confianza | Mostrar factores principales puede ser necesario | ¿Qué nivel de explicación exige el analista? |
| El costo de falsos rechazos también importa | El umbral debe considerar ganancia, no solo mora | ¿Cómo estima la empresa el ingreso perdido? |
| Los perfiles fuera de distribución no deben decidirse automáticamente | Mantener la salida “revisar” | ¿Qué reglas exactas obligan a revisión? |

## Implicaciones preliminares para el backlog

Estas implicaciones son propuestas derivadas de la simulación y no deben aceptarse hasta validarlas:

1. Mantener tres resultados: `aprobar`, `revisar` y `rechazar`.
2. Validar información faltante antes de calcular una probabilidad.
3. Registrar cada predicción y la decisión final para auditoría.
4. Considerar motivos principales o códigos de razón como trabajo futuro, aunque inicialmente estaban fuera del alcance.
5. Medir tiempo de respuesta, tasa de aprobación, mora por cosecha y porcentaje de revisión manual.

## Cómo convertirla en evidencia real

1. Entregar el guion a una persona que trabaje o haya trabajado como analista de crédito.
2. Registrar fecha, duración, rol y consentimiento para usar notas anonimizadas.
3. Sustituir cada respuesta simulada por una paráfrasis fiel de la conversación.
4. Marcar cada hallazgo como confirmado, refutado o pendiente.
5. Guardar la entrevista real en otro archivo con código `DT-01`; conservar esta simulación únicamente como material de preparación.
