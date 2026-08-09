# Control temporal de Ancón, ingreso 68→70 en 1985–1986

**Estado:** revisado; **ruptura cartográfica de inicio de serie confirmada**
**Unidad:** Lomas de Ancón
**Candidato:** clase distinta de 70 en 1985 → clase 70 en 1986
**Área:** **1 242.401324 ha**
**Fecha:** 2026-08-05
**Script:** `04_extraccion_series/01_scripts/paso06E4_ancon_68_70_1985_1990.js`

## Motivo del control

El ranking de saltos interanuales (`ranking_saltos_acr_por_ambito.csv`) sitúa el
periodo 1985–1986 de Ancón como **rank 1**, con +1 223.460 ha netas. Ese salto
es 2.3 veces mayor que la mayor ruptura documentada hasta ahora (Ancón
2000–2001, 532.735 ha) y no figuraba en la lista de rupturas conocidas de la
metodología v1.0.

Se aplicó el mismo protocolo de los controles `6E3` (Ancón 2000–2001) y `6F2`
(CV-042, Carabayllo 2 2014–2015), con un cuarto criterio añadido: la auditoría
del insumo Landsat.

## Control de integridad contra el Paso 6

| Campo | Calculado | Esperado | Diferencia |
|---|---:|---:|---:|
| Entrada 68→70 (ha) | 1 242.401324 | 1 242.400 | +0.001324 |
| Salida 70 (ha) | 18.941693 | 18.941 | +0.000693 |
| Balance neto (ha) | 1 223.459632 | 1 223.460 | −0.000368 |
| Clase 70 total 1985 (ha) | 3 087.924742 | 3 087.925 | −0.000258 |
| Clase 70 total 1986 (ha) | 4 311.384374 | 4 311.385 | −0.000626 |

El control reproduce `resumen_transiciones_acr_paso06.csv` con error de
milésimas de hectárea.

## Origen del candidato en 1985

| Clase de origen | Nombre | ha | % del candidato |
|---:|---|---:|---:|
| 68 | Otra área natural sin vegetación | 1 238.985397 | **99.725** |
| 13 | Otra formación no boscosa | 3.153137 | 0.254 |
| 66 | Matorral | 0.262790 | 0.021 |
| 12, 29, 25, 24 | — | 0.000000 | 0.000 |

El ingreso procede casi íntegramente de la clase 68, que es el complemento
directo del clasificador binario loma/no-loma descrito en el ATBD de la clase
70.

## Criterio 1 — Sincronía

Superficie del candidato en clase 70, año por año:

| Año | ha |
|---:|---:|
| 1985 | 0.000000000000 |
| 1986 | 1 242.401324317064 |
| 1987 | 1 242.401324317064 |
| 1988 | 1 242.401324317064 |
| 1989 | 1 242.401324317064 |
| 1990 | 1 242.401324317064 |

El valor es **idéntico a doce decimales durante cinco años consecutivos**: cero
píxeles de variación en 1 242 ha.

En el mismo intervalo, el resto de Ancón sí varía: 4 311.4 → 4 553.8 → 4 780.2
→ 4 806.4 → 4 928.2 ha. El bloque permanece congelado mientras su entorno
fluctúa. Ese comportamiento es compatible con la aplicación de un filtro
temporal o de GapFill, no con la dinámica de un ecosistema dependiente de
niebla.

## Criterio 2 — Retorno

- Persistencia como clase 70 durante 1987–1990: **100 %**.
- Reversión antes de 1990: **0 ha**.
- Persistencia como clase 70 hasta 2024: **0 %**.

Ninguna de las 1 242.401 ha sigue siendo clase 70 en 2024. El bloque ingresa
completo en 1986, permanece invariante hasta 1990 y desaparece antes del final
de la serie.

Como consecuencia derivada, queda explicada la identidad exacta entre
`area_70_2024_ha` y `area_siempre70_ha` en Ancón: si ningún píxel que ingresó
en 1986 sobrevive a 2024, el conjunto de 2024 está contenido en el de 1985.

## Criterio 3 — Señal espectral

Valores medios del candidato, mosaicos oficiales, escala nativa:

| Año | `ndvi_median` | `evi2_median` |
|---:|---:|---:|
| 1985 | 10 753.892874 | 10 380.519097 |
| 1986 | 10 710.253313 | 10 349.194731 |
| 1987 | 10 722.495185 | 10 347.511638 |
| 1988 | 10 704.208191 | 10 344.206811 |
| 1989 | 10 753.005382 | 10 361.889171 |
| 1990 | 10 664.624522 | 10 331.026182 |

Variación 1985→1986: NDVI **−0.41 %**, EVI2 **−0.30 %**.

La superficie clasificada como clase 70 pasa de 0 a 1 242 ha mientras sus
propios índices de vegetación descienden. El control visual comparado confirmó
que las capas NDVI de 1985 y 1986 no presentan diferencia apreciable.

Este resultado es simétrico al del control 6E3: allí el NDVI aumentó 1.7 %
mientras 532.735 ha salían de la clase 70. En ambas direcciones la etiqueta se
desplaza sin contrapartida espectral.

## Criterio 4 — Auditoría del insumo Landsat

| Año | Escenas totales | Por tesela | Nubosidad media |
|---:|---:|---|---:|
| **1985** | **9** | 2, 3, 4 | **56.7 %** |
| 1986 | 27 | 4, 7, 16 | 46.7 % |
| 1987 | 54 | 9, 14, 31 | 51.7 % |
| 1988 | 57 | 7, 9, 41 | 51.7 % |
| 1989 | 37 | 7, 7, 23 | 43.3 % |
| 1990 | 49 | 8, 13, 28 | 51.7 % |

Satélite (`l5`), versión de mosaico (`4`) y regiones (703, 704, 705) son
idénticos en los seis años. La única variable que cambia es el número de
observaciones útiles: 1985 dispone de un tercio de las escenas de 1986 y un
sexto de las de 1988, con la nubosidad más alta de la ventana.

Mecanismo compatible con el ATBD de la clase 70: con nueve escenas y 56.7 % de
nubes, el `qualityMosaic` sobre EVI2 dispone de muy pocas observaciones para
seleccionar; los compuestos de época seca y húmeda de 1985 resultan ruidosos;
el Random Forest no alcanza el umbral de probabilidad del 40 % y la clase 70
queda subdetectada, cayendo el píxel a la clase 68.

## Decisión metodológica

Los cuatro criterios se cumplen. `1985–1986` se clasifica como:

```text
RUPTURA_INICIO_SERIE_68_70
```

Interpretación: discontinuidad cartográfica atribuible a la pobreza del mosaico
del primer año de la serie. No es evidencia de recuperación ni de expansión
ecológica de la loma.

Uso permitido:

- documentar una limitación metodológica del inicio de la serie;
- excluir 1985 de los cálculos de cambio y de línea base;
- justificar el uso de persistencia multianual frente a lecturas anuales;
- aportar retroalimentación localizada a MapBiomas Perú sobre la clase beta 70.

No debe presentarse como:

- recuperación de cobertura de loma entre 1985 y 1986;
- ganancia ecológica;
- error de la geometría oficial del ACR.

## Alcance del hallazgo

El salto no se limita a Ancón. Comparación 1985→1986 en los cinco ámbitos,
según `serie_indicadores_acr_1985_2024.csv`:

| Ámbito | 1985 (ha) | 1986 (ha) | Variación |
|---|---:|---:|---:|
| Amancaes | 200.8 | 202.7 | +1.0 % |
| Ancón | 3 087.9 | 4 311.4 | **+39.6 %** |
| Carabayllo 1 | 76.9 | 79.9 | +3.9 % |
| Carabayllo 2 | 135.0 | 191.6 | **+41.9 %** |
| Villa María | 488.0 | 476.7 | −2.3 % |
| **Total ACR** | **3 988.6** | **5 262.2** | **+31.9 %** |

La línea base del área de estudio completa varía 31.9 % entre el primer y el
segundo año de la serie.

## Continuación

El alcance de la ruptura y su generalidad a lo largo de los 40 años se
examinaron en:

```text
05_analisis_temporal/evidencia/control_paso06E5_insumo_landsat_1985_2024.md
```

La sensibilidad de los indicadores de persistencia a la exclusión de 1985 se
examinó en:

```text
05_analisis_temporal/evidencia/
control_paso06E6B_sensibilidad_ventana_1986_2024.md
```

## Evidencia visual conservada

```text
05_analisis_temporal/evidencia/paso06E4_ancon_mosaico_1985_1986.png
05_analisis_temporal/evidencia/paso06E4_ancon_ndvi_1985_1986.png
```
