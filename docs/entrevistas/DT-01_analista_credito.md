# Entrevista DT-01 — Analista de crédito

## Estado y metadatos

- Estado: contenido recibido; metadatos pendientes de confirmar
- Fecha de la entrevista: no proporcionada
- Rol confirmado por el usuario: analista de crédito
- Entrevistador: no proporcionado
- Duración: no proporcionada
- Consentimiento para usar notas anonimizadas: no informado
- Empresa: no identificada
- Datos personales de clientes: no incluidos

## Transcripción estructurada

### 1. ¿Cómo llega una solicitud de crédito y qué revisa primero?

La solicitud llega al sistema o a la aplicación con datos personales, empleo, ingresos declarados, monto solicitado —hasta USD 25,000— y autorización para consultar el buró.

El analista primero verifica que los datos básicos sean coherentes y que la identificación sea válida. Después consulta el buró para revisar moras activas, comportamiento con otras obligaciones y número de consultas recientes. Varias consultas en un periodo corto pueden indicar una búsqueda urgente de liquidez.

Finalmente compara los ingresos netos con el monto solicitado para determinar si el cliente tendría capacidad de pago.

### 2. ¿Qué información suele faltar o generar más dudas?

- **Trabajador independiente sin documentación:** declara ingresos, pero no existen estados de cuenta, declaraciones o depósitos bancarios que permitan comprobarlos.
- **Diferencias entre formulario y documentos:** el ingreso declarado no coincide con la constancia salarial o comprobante de pago, por lo que se requiere llamar a la empresa o pedir aclaraciones.
- **Historial corto:** una persona con una tarjeta de límite bajo o un plan de telefonía solicita entre USD 15,000 y USD 20,000, sin historial suficiente para estimar su comportamiento ante una cuota grande.

### 3. ¿Cuánto tarda una decisión sencilla y una compleja?

- **Solicitud sencilla:** entre 15 y 20 minutos cuando el buró es bueno, el empleo es estable, los ingresos coinciden y el monto es moderado.
- **Solicitud compleja:** puede consumir media jornada o quedar pendiente hasta el día siguiente cuando se deben revisar estados de cuenta, llamar a referencias, analizar alertas o solicitar documentos adicionales.

### 4. ¿En qué casos debe escalar la decisión?

El analista escala al jefe o al comité cuando:

- el monto supera su límite de autorización, por ejemplo, solicita USD 22,000 y el analista puede aprobar hasta USD 10,000;
- el DTI está cerca del límite y se necesita justificar una excepción;
- el score es bajo o intermedio, pero existe un fiador o garantía que podría compensar el riesgo;
- una regla automática rechaza el caso, pero el cliente presenta evidencia de que una mora fue un error bancario ya corregido.

### 5. ¿Qué explicación necesita comunicar al cliente?

La comunicación no debe mencionar algoritmos, modelos concretos ni scores internos. Debe utilizar razones de negocio claras y respetuosas, como endeudamiento elevado o atrasos recientes que superan la política vigente.

La explicación debe informar el motivo sin revelar cómo manipular las reglas internas.

### 6. ¿Qué resulta más costoso: aprobar un cliente que no pagará o rechazar uno bueno?

Desde la operación diaria, aprobar a un mal pagador es más costoso. Un préstamo de USD 18,000 que deja de pagarse a los tres meses genera revisión de cartera vencida, cobranza, posibles gastos legales y eventual castigo contable. Recuperar esa pérdida mediante intereses de clientes sanos toma mucho tiempo.

El analista reconoce que no se debe rechazar a todo el mundo porque la empresa también necesita colocar créditos, pero prioriza comprobar que el solicitante tiene capacidad real de pago.

### 7. ¿Qué tendría que mostrar Aprueba+ para que confíe en su recomendación?

La herramienta debería mostrar:

1. recomendación clara: `APROBAR`, `REVISAR` o `RECHAZAR`;
2. puntaje o probabilidad de riesgo y tres motivos principales;
3. documentos faltantes o discrepancias resaltados inmediatamente;
4. registro de que el analista revisó el caso y de las validaciones realizadas.

El analista rechaza una herramienta que funcione como una caja negra sin razones comprensibles.

### 8. ¿Cómo debería integrarse la herramienta en su trabajo diario?

Debe integrarse al core o CRM utilizado para abrir expedientes. El analista no quiere copiar salarios, identificaciones o montos hacia otra plataforma.

Al seleccionar “Evaluar solicitud”, el proceso debería ejecutarse en segundo plano y devolver la recomendación en la misma pantalla. Los casos enviados a revisión deben entrar automáticamente en una bandeja ordenada por llegada o monto.

### 9. ¿En qué situaciones no permitiría una decisión automática?

- El buró está fuera de servicio o no devolvió información.
- Existen documentos posiblemente alterados o diferencias de identidad.
- El monto está entre USD 15,000 y USD 25,000 y el perfil se encuentra en una zona gris.
- El solicitante es un trabajador independiente informal cuyo ingreso requiere análisis adicional.

En esos casos, la salida obligatoria debe ser revisión humana.

### 10. ¿Qué indicador usaría para evaluar si la herramienta funciona?

- **Tiempo ahorrado:** reducir casos fáciles de aproximadamente 20 minutos a segundos.
- **Resultado de los casos revisados:** comparar las decisiones manuales posteriores con el pago o la mora observada.
- **Falsos rechazos:** identificar clientes buenos rechazados por reglas demasiado estrictas y potencialmente enviados a la competencia.

## Hallazgos respaldados por la entrevista

| Hallazgo | Evidencia | Implicación para Aprueba+ |
| --- | --- | --- |
| El mayor trabajo manual está en verificar documentos e ingresos | Estados de cuenta, llamadas y aclaraciones | La validación de entrada debe ocurrir antes de puntuar |
| El historial corto dificulta evaluar montos altos | Perfiles con productos pequeños solicitan hasta USD 20,000 | Mantener revisión manual fuera del dominio conocido |
| Las decisiones sencillas consumen entre 15 y 20 minutos | Revisión de buró, empleo e ingresos | La automatización puede medirse en tiempo ahorrado |
| La autoridad depende del monto | Ejemplo de límite individual de USD 10,000 | La decisión debe respetar niveles de autorización |
| El analista necesita razones y alertas visibles | Solicita tres motivos y discrepancias marcadas | Los códigos de razón pasan a ser necesidad funcional |
| El sistema debe integrarse al flujo existente | Rechazo explícito al copiar y pegar | La API es el mecanismo de integración adecuado |
| Los falsos rechazos importan en la operación | Clientes buenos pueden ir a la competencia | Medir tasa de aprobación y falsos rechazos |

## Supuestos del proyecto afectados

### Confirmados

- Tres salidas: aprobar, revisar y rechazar.
- Revisión obligatoria cuando falta buró, hay fraude, el monto es alto o el ingreso no puede comprobarse.
- Integración mediante API en lugar de una aplicación aislada.
- Necesidad de una bitácora auditable de la revisión.
- El tiempo operativo es un indicador de éxito relevante.

### Cuestionados o ampliados

- La propuesta excluía los motivos de cada decisión, pero el analista los considera indispensables para utilizar la herramienta.
- El indicador de API menor a 300 ms no mide por sí solo el ahorro operativo; debe acompañarse con tiempo total por solicitud.
- Deben registrarse también la decisión final del analista y el resultado posterior para evaluar los casos enviados a revisión.

### Nuevos datos para validar

- Monto máximo del producto: USD 25,000.
- Ejemplo de límite de autorización del analista: USD 10,000.
- Zona gris para montos entre USD 15,000 y USD 25,000.
- Tiempo manual sencillo: entre 15 y 20 minutos.

Estos valores corresponden a la experiencia del participante y deben contrastarse con la política formal de la institución.
