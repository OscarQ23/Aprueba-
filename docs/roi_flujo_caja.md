# ROI y flujo de caja

## Estado de esta estimación

Los números actuales forman un **escenario ilustrativo v0.1**. No proceden de una financiera ni deben presentarse como resultados observados. Su propósito es dejar una fórmula reproducible que el equipo actualizará después de validar los supuestos con usuarios del negocio.

El cálculo vive en `src/analisis/roi.py`. Se regenera con:

```powershell
& '.\.venv\Scripts\python.exe' -m src.analisis.roi
```

## Supuestos iniciales

| Supuesto | Valor inicial | Debe validarse con |
| --- | ---: | --- |
| Solicitudes al mes | 300 | Gerente de riesgo |
| Tasa de aprobación | 60 % | Gerente de riesgo |
| Monto promedio | USD 1,000 | Datos de cartera |
| Tasa de impago sin modelo | 20 % | Datos históricos |
| Tasa de impago con modelo | 16 % | Prueba retrospectiva |
| Pérdida dado el impago | 70 % | Recuperaciones históricas |
| Inversión inicial | USD 15,000 | Tecnología y finanzas |
| Operación mensual | USD 1,000 | Tecnología y finanzas |

El beneficio mensual se define como la pérdida esperada evitada:

```text
préstamos aprobados × reducción de impago × monto promedio × pérdida dado el impago
```

El escenario mantiene constante la tasa de aprobación. Por tanto, supone que el modelo reemplaza clientes malos por clientes buenos dentro del mismo volumen aprobado. Si la política cambia la tasa de aprobación, deberá añadirse el margen perdido o ganado por clientes buenos.

## Resultado ilustrativo

| Horizonte | Beneficio bruto | Costo total | Flujo neto | ROI | Recuperación |
| --- | ---: | ---: | ---: | ---: | ---: |
| 12 meses | USD 60,480 | USD 27,000 | USD 33,480 | 124.0 % | Mes 4 |
| 24 meses | USD 120,960 | USD 39,000 | USD 81,960 | 210.2 % | Mes 4 |

Los artefactos generados son `reports/flujo_caja_24_meses.csv` y `reports/roi_resumen.json`. El flujo de 24 meses contiene también el corte del mes 12.

## Limitaciones que deben exponerse

- La reducción de impago todavía no proviene del modelo entrenado.
- No se incluyen impuestos, costo de capital ni valor temporal del dinero.
- No se modela el margen de los préstamos pagados ni el costo de falsos rechazos.
- Los valores están expresados en USD solo por coherencia con el dataset de Lending Club.
- Debe añadirse un análisis de sensibilidad después de obtener supuestos del negocio.
