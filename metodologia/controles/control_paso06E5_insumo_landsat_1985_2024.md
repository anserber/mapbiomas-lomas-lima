# Auditoría del insumo Landsat de los mosaicos oficiales, 1985–2024

**Estado:** revisado; **hipótesis general refutada, hallazgo alternativo confirmado**
**Ámbito:** cinco ámbitos del ACR Sistema de Lomas de Lima
**Fecha:** 2026-08-05
**Script:** `04_extraccion_series/01_scripts/paso06E5_auditoria_insumo_landsat_1985_2024.js`

> **Corrección del 6 de agosto de 2026.** Las desviaciones estándar publicadas
> inicialmente en este documento (133,9 ha en el régimen I y 128,8 ha en Ancón)
> se calcularon incluyendo el residual de 1986, que necesita a 1985 como año
> vecino. Al adoptarse la decisión de excluir 1985 de todo cálculo, el residual
> de 1986 deja de ser calculable y el régimen I pasa a abarcar 1987-1999. Las
> cifras vigentes son las de las tablas siguientes. El cambio refuerza el
> hallazgo en lugar de debilitarlo: el régimen I resulta mucho más estable de lo
> estimado, de modo que la inestabilidad no procede de la antigüedad de la serie
> sino de la mezcla de sensores del régimen II.

## Hipótesis contrastada

El control 6E4 demostró que la ruptura 1985–1986 de Ancón se explica por la
pobreza del mosaico del primer año. De ahí surgió la hipótesis general:

> Los años con menos observaciones útiles producen subdetección de la clase
> beta 70 y saltos artificiales al año siguiente, a lo largo de toda la serie.

## Diseño

Auditoría de metadatos, sin `reduceRegion` y sin recalcular ninguna superficie.
Las superficies anuales proceden de `serie_indicadores_acr_1985_2024.csv`, ya
validada. El cruce se realizó fuera de GEE.

Colecciones auditadas:

```text
1985-2021  projects/nexgenmap/MapBiomas2/LANDSAT/PANAMAZON/mosaics-2
2022-2024  projects/mapbiomas-raisg/MOSAICOS/mosaics-2
```

Cobertura verificada: 200 imágenes, 40 años sin huecos, regiones 703, 704, 705.

Indicador de anomalía empleado: **residual local**, definido como

```text
residual(t) = area70(t) - [ area70(t-1) + area70(t+1) ] / 2
```

Elimina la tendencia de largo plazo y aísla la desviación de cada año respecto
de sus vecinos inmediatos.

## Resultado 1 — La hipótesis general no se sostiene

Correlación entre insumo y residual local, años 1986–2022, versión 4 de mosaico:

| Prueba | Valor |
|---|---:|
| Pearson (escenas, residual) | −0.226 |
| Spearman (escenas, residual) | −0.104 |
| Pearson (nubosidad, residual) | +0.026 |
| Pearson (escenas, residual) sin 1986 | +0.053 |

**El número de escenas no explica la inestabilidad interanual de la clase 70.**

Los demás años de insumo pobre lo confirman: 1998 (49 escenas) tiene residual
−16.6 ha, 1994 (58 escenas) −1.3 ha y 1989 (61 escenas) −49.1 ha. Ninguno
produce una anomalía comparable.

Este resultado negativo se conserva y se reporta. La explicación más plausible
fue probada y no resistió la comprobación.

## Resultado 2 — 1985 es un caso extremo aislado

Posición de 1985 entre los 38 años comparables (versión 4 de mosaico):

| Métrica | 1985 | Media 1986–2022 | Posición |
|---|---:|---:|---|
| Escenas totales | **17** | 89 | **peor de 38** |
| Escenas en la tesela más pobre | **2** | ~7 | **peor de 38** |
| Nubosidad media | **58 %** | ~44 % | **peor de 38** |

Es el peor año de la serie en las tres métricas simultáneamente.

Consecuencia medida sobre el ACR completo:

```text
Clase 70 en 1985                =  3 988.6 ha
Promedio 1986-1990              =  5 639.2 ha
Déficit de 1985                 =    -29.3 %
```

1985 no es un año más ruidoso dentro de la misma distribución: es un valor
atípico que subdetecta cerca de un tercio de la clase 70 del área de estudio.

## Resultado 3 — Régimen de sensor

Al no encontrarse señal en el conteo de escenas, los residuales se agruparon
según la composición de satélites del mosaico.

### ACR completo

| Régimen | Periodo | DE del residual | \|residual\| medio | Máximo |
|---|---|---:|---:|---:|
| L5 solo | 1987–1999 | 35.7 ha | 25.9 ha | 98.4 ha |
| Mezcla L5/L7/lx | 2000–2013 | 129.2 ha | 91.5 ha | 286.8 ha |
| **L8 solo** | **2014–2022** | **10.8 ha** | **7.8 ha** | **20.1 ha** |

### Ancón

| Régimen | DE del residual | Máximo |
|---|---:|---:|
| L5 solo | 36.0 ha | 100.1 ha |
| Mezcla L5/L7/lx | 126.6 ha | 272.3 ha |
| **L8 solo** | **11.4 ha** | **26.1 ha** |

**El régimen de mezcla de sensores es 3,6 veces más volátil que Landsat 5
solo y doce veces más que Landsat 8 solo.** La inestabilidad no procede de la
antigüedad de la serie sino de la heterogeneidad del sensor.

Los cinco mayores residuales de Ancón se concentran íntegramente en el
régimen II:

| Año | Residual | Satélites |
|---:|---:|---|
| 2000 | +272.3 ha | l5, l7, lx |
| 2001 | −244.3 ha | l5, l7, lx |
| 2003 | −177.1 ha | l5, l7, lx |
| 2002 | +161.6 ha | l7, lx |
| 2005 | +136.7 ha | l5, lx |

La ruptura 2000–2001, ya documentada en `control_temporal_ancon_70_68_1998_2004.md`,
no es un evento aislado: pertenece a un bloque de inestabilidad 2000–2005 que
coincide con la incorporación de Landsat 7 y con cambios anuales en la
composición del mosaico. El año 2002 es el único sin Landsat 5 en ese tramo y
produce un residual de +161.6 ha.

Por contraste, entre 2016 y 2018 la clase 70 del ACR vale 3 699.7, 3 700.2 y
3 700.5 ha: menos de una hectárea de variación en tres años.

## Resultado 4 — Cambio de versión de mosaico en 2023

| Periodo | Versión | Etiqueta de satélite | Escenas totales |
|---|---|---|---:|
| 1985–2022 | 4 | l5 / l7 / lx / l8 / l9 | 17 a 138 |
| **2023–2024** | **5** | **ly** | **515 y 236** |

El conteo de escenas de 2023–2024 responde a otra convención y **no es
comparable** con el de los años anteriores. La nubosidad media declarada en
2023 (82 %) tampoco lo es.

El residual de 2023 es de solo +6.3 ha, de modo que el cambio de versión **no
produce un quiebre visible en la salida** de la clase 70. Se documenta como
discontinuidad de insumo declarada, no como ruptura cartográfica.

Relevancia: el cambio de versión cae dentro de la ventana de vigilancia
reciente censurada (2021–2023), por lo que debe figurar entre las limitaciones
declaradas de esa variable.

## Decisión metodológica

1. Se descarta la hipótesis general de que el número de escenas explique la
   inestabilidad de la clase 70. El resultado negativo se reporta.
2. Se confirma 1985 como año de insumo deficiente, con subdetección medida de
   −29.3 % en el ACR.
3. Se incorpora a la metodología la **tabla de tres regímenes de sensor** con su
   volatilidad medida, como limitación cuantificada de la serie.
4. Se declara que **solo el tramo 2014–2024 sostiene lecturas interanuales**;
   antes de 2014 la volatilidad es de un orden de magnitud superior.
5. Se declara el cambio de versión de mosaico en 2023 como discontinuidad de
   insumo dentro de la ventana de censura reciente.

## Implicación para el diseño del estudio

El núcleo metodológico del proyecto se apoya en persistencia multianual y en
eventos con ventana W5. Ninguno de los dos indicadores se lee año a año.

Este control convierte esa elección, hasta ahora justificada por el carácter
estacional de las lomas, en una decisión respaldada por una medición: la
volatilidad interanual de la clase beta 70 varía entre 129 y 11 ha según el
régimen de sensor, de modo que ninguna lectura anual es comparable a lo largo
de los 40 años de la serie.

## Aporte a MapBiomas Perú

El resultado constituye retroalimentación localizada y reproducible sobre la
estabilidad temporal de la clase beta 70 en un área protegida concreta, con
identificación de los tramos de la serie que requieren cautela y del
comportamiento del producto ante cambios de sensor.
