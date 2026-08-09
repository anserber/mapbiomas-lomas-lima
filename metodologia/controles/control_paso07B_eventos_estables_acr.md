# Control del Paso 7B — eventos estables de clase 70

**Fecha:** 2026-07-28  
**Unidad:** cinco ámbitos del ACR Sistema de Lomas de Lima  
**Periodo:** 1985–2024  
**Estado:** aprobado con corrección de visualización

## Controles estructurales

- Años: 40.
- Ámbitos: 5.
- Ventana de 3 años: eventos evaluables entre 1988 y 2022.
- Ventana de 5 años: eventos evaluables entre 1990 y 2020.
- Máximo de pérdidas o recuperaciones por píxel:
  - ventana 3: 2;
  - ventana 5: 1.

Los años posteriores al último año evaluable quedan censurados a la derecha y
no se interpretan como ausencia de cambio estable.

## Rupturas cartográficas conocidas

| Ámbito | Ruptura | Área total (ha) | Intersección W3 (ha) | Intersección W5 (ha) |
|---|---|---:|---:|---:|
| Ancón | 2000–2001, 70→68 | 532.734795 | 531.245731 | 509.260250 |
| Carabayllo 2 | 2014–2015, 70→13/68 | 10.733564 | 10.733564 | 10.733564 |

La intersección es menor que el área total de la ruptura de Ancón porque la
regla exige que cada píxel cumpla también todos los años anteriores y
posteriores de la ventana. La diferencia no constituye un error geométrico.

Estas superficies se excluyen de las pérdidas filtradas y se conservan como
limitaciones metodológicas documentadas en el Paso 6.

## Sensibilidad observada en Ancón

- Recuperación W3: 983.843859 ha.
- Recuperación W5: 619.156888 ha.
- Recuperación adicional aceptada solo por W3: 364.686971 ha.
- W5 conserva aproximadamente 62.9 % de la superficie detectada con W3.

La mayor extensión verde de W3 es coherente con su menor exigencia temporal.
No demuestra por sí sola recuperación ecológica.

## Decisión

El Paso 7B queda aprobado. Las reglas de 3 y 5 años funcionan y las dos
rupturas cartográficas fueron identificadas correctamente. El error
`Mapy is not defined` ocurrió después de imprimir los resultados y afectó
solamente la capa visual de rupturas; se corrigió a `Map.addLayer`.

No se denominarán todavía “pérdida” o “recuperación ecológica”. En el Paso 7C
se conciliará el año de cada evento con las transiciones oficiales y se
evaluará la sensibilidad W3–W5 antes de producir resultados definitivos.

## Evidencias visuales

```text
05_analisis_temporal/evidencia/paso07B_recuperacion_w3_ancon.png
05_analisis_temporal/evidencia/paso07B_recuperacion_w5_ancon.png
```

## Script

```text
04_extraccion_series/01_scripts/paso07B_piloto_eventos_estables_acr.js
```
