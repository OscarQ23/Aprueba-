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
