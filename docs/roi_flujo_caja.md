# ROI y flujo de caja

## Estado de esta estimación

Los números actuales forman un **escenario preliminar v0.2**. La pérdida dado el impago se actualizó con la recuperación de 15 % a 20 % reportada en DT-02; se usa el punto medio de 17.5 %, equivalente a una LGD de 82.5 %. Los demás valores siguen siendo ilustrativos y no deben presentarse como datos observados de una financiera.

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
| Pérdida dado el impago | 82.5 % | Punto medio de recuperación 15–20 % en DT-02; validar con cartera |
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
| 12 meses | USD 71,280 | USD 27,000 | USD 44,280 | 164.0 % | Mes 4 |
| 24 meses | USD 142,560 | USD 39,000 | USD 103,560 | 265.5 % | Mes 4 |

Los artefactos generados son `reports/flujo_caja_24_meses.csv` y `reports/roi_resumen.json`. El flujo de 24 meses contiene también el corte del mes 12.

## Limitaciones que deben exponerse

- La reducción de impago todavía no proviene del modelo entrenado.
- La recuperación de 15–20 % procede de una entrevista y no de datos de cartera auditados.
- Los montos de USD 15,000–25,000 mencionados en las entrevistas son límites o ejemplos, no un monto promedio; por eso no sustituyen todavía el supuesto conservador de USD 1,000.
- No se incluyen impuestos, costo de capital ni valor temporal del dinero.
- No se modela el margen de los préstamos pagados ni el costo de falsos rechazos.
- Los valores están expresados en USD solo por coherencia con el dataset de Lending Club.
- Debe añadirse un análisis de sensibilidad después de obtener supuestos del negocio.
