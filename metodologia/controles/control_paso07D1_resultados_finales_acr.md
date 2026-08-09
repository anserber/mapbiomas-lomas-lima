# Control del Paso 7D1 — resultados finales ACR

**Fecha:** 2026-07-28  
**Estado:** PASS  
**Producto:** `paso07D1_resultados_finales_acr_1985_2024.csv`

## Validación del archivo descargado

- Filas: 5.
- Columnas: 40.
- Ámbitos únicos: Amancaes, Villa María, Carabayllo 2, Ancón y Carabayllo 1.
- Campos obligatorios vacíos: 0.
- Diferencia máxima entre pérdida W5 y suma de destinos:
  `7.1054e-15 ha`.
- Diferencia máxima entre recuperación W5 y suma de orígenes:
  `7.1054e-15 ha`.

Los residuos son numéricamente irrelevantes.

## Controles reproducidos

| Ámbito | Pérdida W5 filtrada (ha-evento) | Ruptura conocida (ha) |
|---|---:|---:|
| Amancaes | 4.963223 | 0 |
| Villa María | 38.154384 | 0 |
| Carabayllo 2 | 37.411829 | 10.733564 |
| Ancón | 2153.081923 | 532.734795 |
| Carabayllo 1 | 0.013391 | 0 |

### Qué significa «ruptura conocida»

En este control, una **ruptura conocida** es una discontinuidad temporal de la
clasificación de MapBiomas documentada en el Paso 6. No representa un recorte
del polígono, un enclave territorial ni una superficie retirada del ACR.

- **Ancón — 532.734795 ha:** píxeles que cambiaron conjuntamente de clase
  `70` (Loma costera) a clase `68` en la transición 2000–2001. El cambio
  permaneció como clase 68 en los años siguientes y no mostró una pérdida de
  vegetación equivalente en el control con mosaicos/NDVI. Por ello se trata
  como una ruptura o intercambio cartográfico `70→68`, no como 532.73 ha de
  pérdida ecológica.
- **Carabayllo 2 — 10.733564 ha:** píxeles que cambiaron de clase `70` a
  clases `13` y `68` en 2014–2015. La señal fue estable, sin retorno a clase
  70, pero el control visual/NDVI no sustentó denominarla pérdida ecológica.
  Esta superficie tampoco corresponde al enclave rectangular de SEDAPAL.

El **enclave rectangular de SEDAPAL** es una cuestión geométrica distinta:
está fuera del ACR y fue excluido de los anillos de periferia externa. No
interviene en la superficie de ruptura conocida reportada para el interior de
Carabayllo 2.

Las categorías de destino conciliaron con los controles 7C y 7C3. El archivo
queda habilitado como producto final del interior de los ámbitos ACR.

## Ruta

```text
05_analisis_temporal/02_final/
paso07D1_resultados_finales_acr_1985_2024.csv
```
