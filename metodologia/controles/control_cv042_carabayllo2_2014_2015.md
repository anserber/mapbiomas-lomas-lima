# Control de CV-042 — Lomas de Carabayllo 2, 2014–2015

**Estado:** PASS  
**Fecha:** 2026-07-28  
**Unidad:** interior del ámbito Lomas de Carabayllo 2  
**Clases:** 70 = Loma costera; 13 = Otra formación no boscosa; 68 = Otra área natural sin vegetación

## Resultado

| Componente | Área (ha) |
|---|---:|
| 70→13 | 7.582925 |
| 70→68 | 3.150639 |
| Total CV-042 | 10.733564 |

Los píxeles candidatos fueron clase 70 durante 2012–2014 y ninguno regresó
a clase 70 entre 2016 y 2024. En 2024, `2.954547 ha` estaban en clase 13,
`7.691463 ha` en clase 68 y `0.087554 ha` en otra clase.

La permanencia fuera de clase 70 fue del `100 %`. Sin embargo, solo
`40.936 %` conservó exactamente la misma clase de destino durante todo
2016–2024, porque los píxeles intercambiaron principalmente entre las clases
naturales 13 y 68.

## Control espectral y visual

El NDVI medio del candidato fue:

| Año | NDVI medio almacenado por el mosaico |
|---|---:|
| 2012 | 10530.620 |
| 2013 | 10949.393 |
| 2014 | 11213.770 |
| 2015 | 11161.580 |
| 2016 | 11432.147 |
| 2017 | 11628.872 |
| 2018 | 11091.794 |

Entre 2014 y 2015 la variación fue de aproximadamente `-0.465 %`, seguida
por valores superiores en 2016 y 2017. El control visual mostró una tonalidad
verde relativamente uniforme en 2015 y no evidenció una transformación física
equivalente a la desaparición de `10.733564 ha` de vegetación.

Capturas preservadas:

```text
05_analisis_temporal/evidencia/cv042_carabayllo2_mosaico_2014_2015.png
05_analisis_temporal/evidencia/cv042_carabayllo2_ndvi_2015.png
```

## Decisión metodológica

`CV-042` se clasifica como:

```text
RUPTURA_70_13_68
```

Interpretación: ruptura cartográfica estable de la clase 70 hacia las clases
naturales 13 y 68. Es evidencia de una discontinuidad o cambio de decisión de
clasificación, no evidencia suficiente de pérdida ecológica.

Uso permitido:

- documentar una limitación metodológica de la serie;
- justificar filtros de persistencia y control espectral;
- excluir `CV-042` de los totales de impacto ecológico confirmado.

No debe presentarse como:

- pérdida comprobada de loma;
- degradación causada por actividad humana;
- desaparición de vegetación entre 2014 y 2015.

## Fuente reproducible

```text
04_extraccion_series/01_scripts/
paso06F2_control_cv042_carabayllo2_2014_2015.js
```
