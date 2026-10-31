# Entrevista DT-02 — Gerente de riesgos

## Estado y metadatos

- Estado: contenido recibido; metadatos pendientes de confirmar
- Fecha de la entrevista: no proporcionada
- Rol confirmado por contexto y corrección del usuario: gerente de riesgos
- Entrevistador: no proporcionado
- Duración: no proporcionada
- Consentimiento para usar notas anonimizadas: no informado
- Empresa: no identificada
- Datos personales de clientes: no incluidos

## Transcripción estructurada

### 1. ¿Cómo llega una solicitud de crédito y qué revisa primero?

La solicitud entra por canal digital o sucursal con identificación, comprobantes de ingresos, estabilidad laboral o comercial, datos de contacto y autorización explícita para consultar el buró de crédito.

El orden de revisión es:

1. **Reglas de exclusión:** edad mínima de 21 años, listas restrictivas —OFAC, PEP y PLAFT— y autenticidad del documento de identidad.
2. **Buró de crédito:** días de mora actual y número de consultas recientes. Para montos mayores de USD 10,000 se exige cero días de mora durante los últimos seis meses.
3. **Relación cuota/ingreso:** ingresos netos verificados frente a gastos fijos, cuotas vigentes y nueva cuota. El DTI global no debe superar el 45 %.

### 2. ¿Qué información suele faltar o generar más dudas?

- **Inconsistencias de ingresos:** diferencias entre el ingreso bruto declarado y los depósitos bancarios, especialmente en trabajadores independientes o por honorarios.
- **Historiales delgados:** menos de doce meses de experiencia crediticia formal o únicamente créditos pequeños de telefonía y casas comerciales. Esto dificulta proyectar el comportamiento para montos entre USD 15,000 y USD 25,000.
- **Deuda no declarada:** obligaciones con cooperativas, prestamistas locales o casas comerciales que no están consolidadas en el buró tradicional.

### 3. ¿Cuánto tarda una decisión sencilla y una compleja?

- **Green Track / Red Track:** menos de 30 segundos cuando la decisión es automatizada. Si requiere validación documental de un analista junior, entre 10 y 15 minutos.
- **Yellow Track:** entre 2 y 6 horas; puede alcanzar 24 horas cuando requiere confirmación laboral, verificación comercial o visita de campo para trabajadores independientes.

### 4. ¿En qué casos debe escalar la decisión?

La decisión se escala al comité de crédito o a la gerencia de riesgos cuando ocurre alguno de estos casos:

- solicitud superior a USD 15,000 situada en la franja media del score;
- DTI entre 45 % y 50 % acompañado de score superior a 780 o garantía líquida complementaria;
- más del 40 % del ingreso procede de comisiones o bonos y el monto solicitado supera USD 10,000;
- menos de un año en el empleo actual, aunque exista continuidad comprobable en el mismo sector.

### 5. ¿Qué explicación necesita comunicar al cliente?

El motor debe generar códigos de razón de negocio parametrizados, sin revelar la fórmula interna ni el algoritmo. Ejemplos permitidos:

- “Su nivel de endeudamiento actual respecto a sus ingresos supera el límite permitido por la política institucional”.
- “Historial crediticio insuficiente o reciente en instituciones financieras”.
- “Registro de atrasos recientes en sus compromisos de pago en el sistema financiero”.

### 6. ¿Qué resulta más costoso: aprobar un cliente que no pagará o rechazar uno bueno?

En préstamos personales sin garantía real de hasta USD 25,000, aprobar a un cliente que no paga tiene un costo sustancialmente mayor.

Para un crédito de USD 20,000 con mora temprana, la recuperación estimada se sitúa entre 15 % y 20 %. Según la respuesta, se necesitarían entre 8 y 12 créditos sanos del mismo monto, a tasas de 18 % a 24 %, para recuperar el capital perdido.

Rechazar a un cliente bueno implica perder su margen financiero neto. Por ello, el punto de corte debe priorizar el control de la pérdida esperada sin reducir excesivamente la tasa de aprobación objetivo.

### 7. ¿Qué tendría que mostrar Aprueba+ para que confíe en su recomendación?

La pantalla del analista debería mostrar:

- decisión: `APROBADO_AUTOMATICO`, `REVISION_MANUAL` o `RECHAZADO_AUTOMATICO`;
- score final estandarizado, por ejemplo de 0 a 1,000 puntos;
- probabilidad de impago a doce meses;
- tres factores determinantes principales mediante explicabilidad o valores SHAP;
- cálculo de capacidad de pago con ingreso aceptado y deudas detectadas;
- registro de la versión del modelo y de los datos utilizados para emitir la decisión.

### 8. ¿Cómo debería integrarse la herramienta en su trabajo diario?

Mediante una API REST síncrona integrada al core financiero, CRM o sistema de originación. No debería existir una herramienta aislada que obligue al analista a copiar datos.

Cuando la API devuelva `REVISION_MANUAL`, el sistema central debería asignar el caso a una bandeja según monto y perfil de riesgo, mostrando el informe de Aprueba+ con la solicitud.

### 9. ¿En qué situaciones no permitiría una decisión automática?

- El buró está fuera de servicio o devuelve información incompleta.
- El sistema antifraude detecta diferencias de identidad o posible suplantación.
- El monto supera USD 15,000 y el score está en una franja intermedia, por ejemplo entre 620 y 720 puntos.
- Los ingresos no cuentan con respaldo bancario verificable.

En esos casos el sistema debe responder `REVISION_MANUAL`, no aprobar ni rechazar automáticamente.

### 10. ¿Qué indicador usaría para evaluar si la herramienta funciona?

- **Gini:** objetivo superior a 0.45 sobre la población evaluada.
- **Mora temprana:** First Payment Default y Ever 30/60 durante los primeros tres a seis meses.
- **Automatización:** tasa de aprobación automática frente a porcentaje enviado a revisión manual.
- **PSI:** Population Stability Index para detectar cambios de población y necesidad de recalibración.

## Hallazgos respaldados por la entrevista

| Hallazgo | Evidencia | Implicación para Aprueba+ |
| --- | --- | --- |
| La decisión comienza con reglas de exclusión | Edad, listas restrictivas e identidad | Las reglas duras deben ejecutarse antes del modelo |
| El DTI es central y tiene zonas de excepción | Límite general de 45 % y revisión hasta 50 % | La API debe calcular DTI y separar reglas de score |
| Los historiales delgados quedan fuera del dominio confiable | Menos de doce meses dificulta la predicción | Mantener salida de revisión manual |
| Una probabilidad sin razones no es suficiente | Se solicitan códigos y tres factores principales | Reconsiderar la exclusión inicial de explicabilidad |
| Los casos complejos deben enviarse a una cola | Yellow Track de 2 a 24 horas | La integración futura necesita asignación y prioridad |
| El costo del impago domina, pero no puede ignorarse la aprobación | Recuperación estimada de 15 % a 20 % | Calibrar el umbral por pérdida esperada y margen |
| La supervisión debe cubrir discriminación y deriva | Gini, FPD, Ever 30/60 y PSI | Añadir métricas de monitoreo al trabajo futuro |

## Supuestos del proyecto afectados

### Confirmados

- Son necesarias tres decisiones: aprobar, revisar y rechazar.
- Los clientes sin historial suficiente deben ir a revisión manual.
- El punto de corte debe elegirse por costo económico, no por 0.5.
- Las predicciones deben guardar versión del modelo y datos de auditoría.
- La herramienta debe integrarse mediante API, no como aplicación aislada.

### Cuestionados o ampliados

- La propuesta excluía los motivos de cada decisión. La entrevista pide códigos de razón y tres factores principales; esta capacidad debería incorporarse al alcance futuro o, si el tiempo lo permite, a una versión mínima.
- La métrica objetivo AUC debería complementarse con Gini, calibración, mora temprana y estabilidad poblacional.
- El límite de historial mínimo de tres años definido inicialmente es más estricto que los doce meses mencionados en la entrevista. Debe resolverse con los datos y la política del gerente de riesgo.

### Nuevos datos para validar

- DTI máximo general: 45 %.
- Excepciones de DTI: entre 45 % y 50 % con score alto o garantía.
- Recuperación estimada en consumo sin garantía: 15 % a 20 %.
- Gini mínimo esperado: 0.45.
- Umbrales de monto de USD 10,000 y USD 15,000.

Estos valores proceden de una entrevista y no deben convertirse en reglas universales sin validación adicional.
