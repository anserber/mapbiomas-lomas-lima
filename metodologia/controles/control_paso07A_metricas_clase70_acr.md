# Control del Paso 7A — métricas de clase 70 en los cinco ámbitos

**Estado:** PASS  
**Fecha:** 2026-07-28  
**Periodo:** 1985–2024  
**Años:** 40  
**Ámbitos:** 5

## Control de rangos

| Métrica | Mínimo | Máximo permitido | Máximo observado |
|---|---:|---:|---:|
| Frecuencia de clase 70 | 0 | 40 | 40 |
| Racha máxima de clase 70 | 0 | 40 | 40 |
| Cambios de estado | — | 39 | 4 |
| Reversiones aisladas | — | 38 | 2 |

Todos los rangos son válidos.

## Resultados por ámbito

| Ámbito | Área de grilla (ha) | Alguna vez clase 70 (ha) | Siempre clase 70 (ha) | Con reversión aislada (ha) | Ruido sobre área alguna vez 70 (%) | Frecuencia media (años) | Racha máxima media (años) |
|---|---:|---:|---:|---:|---:|---:|---:|
| Amancaes | 253.785134 | 209.535560 | 194.140489 | 0.581917 | 0.2777 | 38.7838 | 38.7644 |
| Villa María | 627.639162 | 539.821076 | 452.450931 | 3.638621 | 0.6740 | 36.7898 | 36.7668 |
| Carabayllo 2 | 198.159521 | 193.505358 | 134.073503 | 0.218721 | 0.1130 | 35.5191 | 35.5044 |
| Ancón | 12160.354061 | 5564.792192 | 2685.364319 | 3.372529 | 0.0606 | 28.0527 | 28.0527 |
| Carabayllo 1 | 228.815014 | 79.915899 | 76.942731 | 0 | 0 | 39.9203 | 39.9203 |

## Interpretación

El ruido por reversiones inmediatas es bajo en los cinco ámbitos: su máximo es
`0.674 %` del área que alguna vez fue clase 70. Esto no elimina otras fuentes
de incertidumbre, pero indica que los patrones `70→no70→70` y
`no70→70→no70` no dominan la serie.

En Ancón, aproximadamente:

```text
12 160.354061 ha - 5 564.792192 ha = 6 595.561870 ha
```

nunca fueron clase 70 durante 1985–2024. Por eso el mapa muestra una amplia
superficie blanca dentro del límite del ACR. El blanco significa frecuencia
cero, no ausencia de datos ni pérdida de loma.

El ámbito legal o administrativo no debe confundirse con la extensión
cartografiada de la cobertura de loma.

## Decisión

La Fase 7A queda aprobada. Se autoriza construir eventos estables con ventanas
de 3 y 5 años en la Fase 7B.

## Evidencias

```text
05_analisis_temporal/evidencia/paso07A_frecuencia_villa_maria.png
05_analisis_temporal/evidencia/paso07A_frecuencia_ancon.png
```

Script reproducible:

```text
04_extraccion_series/01_scripts/paso07A_piloto_metricas_clase70_acr.js
```
