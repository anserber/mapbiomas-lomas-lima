# Adenda metodológica v1.1 — Ruptura de inicio de serie y regímenes de sensor

**Fecha:** 2026-08-05
**Estado:** vigente
**Modifica:** `metodologia_final_lomas_mapbiomas.md` (v1.0, 2026-08-01)
**Sustento:** controles 6E4, 6E5 y 6E6-B, y
`05_analisis_temporal/evidencia/dictamen_ruptura_1985_y_regimenes_sensor.md`

La metodología v1.0 no se sobrescribe. Esta adenda enumera las secciones
afectadas y el texto que las sustituye o complementa.

---

> **Corrección del 6 de agosto de 2026.** Las desviaciones estándar publicadas
> inicialmente en este documento (133,9 ha en el régimen I y 128,8 ha en Ancón)
> se calcularon incluyendo el residual de 1986, que necesita a 1985 como año
> vecino. Al adoptarse la decisión de excluir 1985 de todo cálculo, el residual
> de 1986 deja de ser calculable y el régimen I pasa a abarcar 1987-1999. Las
> cifras vigentes son las de las tablas siguientes. El régimen I resulta más
> estable de lo estimado y la mayor volatilidad se concentra en el régimen II;
> el diseño no permite atribuirla a una causa única.

## Modifica la sección 5 — Indicadores de estado de la clase 70

### Ventana temporal de los indicadores

Se distingue entre dos ventanas:

| Indicador | Ventana primaria | Justificación |
|---|---|---|
| Frecuencia, racha máxima, `siempre 70` | **1985–2024** (40 años) | El control 6E6-B midió una variación de 0.000 ha en las ocho unidades al excluir 1985. El indicador es insensible a la ruptura de inicio de serie |
| `alguna vez clase 70` | **1986–2024** (39 años) | Excluir 1985 elimina los píxeles clasificados como clase 70 únicamente en ese año, que no se repiten en ningún año posterior |
| Cualquier cálculo de cambio, tasa o línea base | **1986–2024** | 1985 subdetecta −29,3 % de la clase 70 del ACR |

El valor del indicador «alguna vez clase 70», calculado para la ventana
1985–2024, se conserva en la tabla maestra v2 como análisis de sensibilidad.

### Adición al final de la sección 5

> El año 1985 no se utiliza como referencia en las comparaciones temporales. El
> mosaico oficial de ese año se construyó, para el ACR, con 17 escenas Landsat y
> una nubosidad media del 58 %; estos valores corresponden, respectivamente, al
> menor número de escenas y a la mayor nubosidad media entre los 38 años con
> datos comparables. La superficie clasificada como clase 70 resultó un 29,3 %
> inferior a la meseta observada entre 1986 y 1990. Por ello, se adoptó 1986
> como línea base del estudio.

---

## Modificación de la sección 6.4 — Intercambios naturales y rupturas conocidas

La lista de rupturas conocidas pasa de dos a tres entradas:

| Identificador | Unidad | Periodo | Magnitud | Naturaleza |
|---|---|---|---:|---|
| **RUPTURA_INICIO_SERIE_68_70** | Ancón y sistema | 1985–1986 | 1 242.401 ha en Ancón; +31.9 % en el ACR | Insumo deficiente del primer año de la serie |
| RUPTURA_70_68_ANCON | Ancón | 2000–2001 | 532.735 ha | Cambio estable de asignación temática |
| RUPTURA_70_13_68 (CV-042) | Carabayllo 2 | 2014–2015 | 10.734 ha | Ruptura estable hacia clases naturales |

La primera es la de mayor magnitud de las tres y afecta a la línea base del
conjunto del área de estudio, no solo a un ámbito.

### Precisión sobre el mecanismo de los intercambios 68↔70

Se sustituye la formulación de la v1.0 por la siguiente, sustentada en el ATBD
y en el control 6E4:

> La clasificación de la clase 70 es anual, supervisada y **binaria**
> (loma / no loma), mediante Random Forest de 60 árboles, entrenado contra la
> cartografía MINAM 2023 y con umbral de probabilidad del 40 %. Cuando el
> clasificador no alcanza ese umbral, el píxel adopta la clase del mapa regional
> de base, que en el Desierto Costero es 68 — Otra área natural sin vegetación,
> o 13 — Otra formación no boscosa.
>
> En la jerarquía de integración, la clase 70 tiene prioridad 18 y la clase 68
> prioridad 25: la clase 68 **no puede sobrescribir** a la clase 70. Por tanto,
> una transición `70→68` no representa la conversión del píxel a otra cobertura,
> sino la desactivación del detector de loma en ese píxel y año.
>
> El control 6E4 verificó este mecanismo: el 99.725 % del ingreso de 1986 en
> Ancón procede de la clase 68, y la transición ocurre sin contrapartida
> espectral, con NDVI y EVI2 en descenso.

---

## Añade la sección 5.4 — Regímenes de sensor y comparabilidad interanual

La composición de satélites de los mosaicos oficiales cambia a lo largo de la
serie. El control 6E5 midió la volatilidad de la clase 70 en cada régimen,
mediante el residual local

```text
residual(t) = area70(t) - [ area70(t-1) + area70(t+1) ] / 2
```

### ACR completo

| Régimen | Periodo | Satélites | DE del residual | \|residual\| medio | Máximo |
|---|---|---|---:|---:|---:|
| I | 1987–1999 | L5 | 35.7 ha | 25.9 ha | 98.4 ha |
| II | 2000–2013 | L5, L7, lx | 129.2 ha | 91.5 ha | 286.8 ha |
| III | 2014–2022 | L8 | **10.8 ha** | **7.8 ha** | **20.1 ha** |

### Ancón

| Régimen | DE del residual | Máximo |
|---|---:|---:|
| I | 36.0 ha | 100.1 ha |
| II | 126.6 ha | 272.3 ha |
| III | **11.4 ha** | **26.1 ha** |

### Reglas derivadas

1. **El régimen III (2014–2022) presenta la menor volatilidad medida.** En
   comparación con este régimen, el régimen I es 3,3 veces más volátil y el
   régimen II cerca de 12 veces más volátil. Los años 2023–2024 se analizan por
   separado debido al cambio de versión del mosaico.
2. Ninguna comparación entre años de regímenes distintos se presenta sin
   declarar esa condición.
3. El régimen II concentra las mayores anomalías de la serie: los cinco
   residuales absolutos más altos de Ancón corresponden a 2000, 2001, 2003,
   2002 y 2005.
4. Esta limitación **justifica de forma cuantificada** el uso de persistencia
   multianual y de eventos con ventana W5 en lugar de lecturas anuales. La
   propiedad está medida, no supuesta.

### Hipótesis descartada

Se probó y se descartó la hipótesis de que el número de escenas disponibles
explicara la inestabilidad interanual a lo largo de la serie: Pearson −0.226,
Spearman −0.104 y +0.053 al excluir 1986. El resultado negativo se reporta.

### Cambio de versión de mosaico en 2023

De 1985 a 2022 los mosaicos son de versión 4. En 2023 y 2024 pasan a versión 5
con etiqueta de satélite `ly`, y el conteo de escenas responde a otra
convención, por lo que no es comparable con el de los años anteriores. El
residual de 2023 es de +6.3 ha, de modo que el cambio **no produce un quiebre
visible en la salida**. Se declara como discontinuidad de insumo dentro de la
ventana de vigilancia reciente censurada (2021–2024).

---

## Modifica la sección 2.2 — Periferia

Se declaran tres definiciones de superficie, presentes las tres en los datos del
proyecto:

| Definición | Campo | Anillos disueltos |
|---|---|---:|
| Vectorial | `area_ref_vectorial_ha` | 22 859.206 ha |
| De grilla | `area_grilla_ha` | 22 846.929 ha |
| Clasificada | `area_clasificada_ha` | 22 839.847 ha |

La diferencia entre las dos últimas es `sin_dato_ha` = 7.082 ha, concentrada en
los anillos de 500–1 000 m (2.048 ha) y 1 000–2 000 m (5.035 ha). En los cinco
ámbitos del ACR, `sin_dato_ha` es 0,000; por ello coinciden el área de grilla y
el área clasificada. La superficie vectorial se informa por separado.

> **Regla:** todas las tasas publicadas emplean la **superficie de grilla** como
> denominador, por consistencia dimensional con numeradores expresados en
> hectáreas de píxel. Las otras dos definiciones se publican en la tabla maestra
> para permitir la reconciliación.

Corrige el dictamen del Paso 10, que publicó la superficie vectorial de los
anillos sin declarar la unidad empleada.

---

## Modifica la sección 9 — Regla de interpretación y priorización

Se retira de los productos públicos el campo
`tasa_presion_urbana_indicativa_por_1000ha`, que sumaba la tasa W5 confirmada y
la tasa de censura reciente.

Motivo: las dos señales tienen estatus epistémico y niveles de confianza
distintos —E2 con confianza ALTA y E3 con confianza MEDIA—, por lo que no deben
sumarse ni presentarse como una única medida de presión urbana. Un campo
publicado circula sin su diccionario. La suma es
reproducible a partir de las dos columnas que permanecen publicadas, de modo
que su retirada no elimina información.

La versión v1 de la tabla maestra conserva el registro histórico del campo.

---

## Resumen de cambios en los productos públicos

Los identificadores F01 y F02 corresponden a códigos internos de los productos
durante el desarrollo y se conservan para enlazar esta adenda con los archivos
del repositorio.

| Producto | Cambio |
|---|---|
| `tabla_maestra_resultados_publicos_v2.csv` | Añade `area_ref_vectorial_ha`, `area_clasificada_ha`, `sin_dato_ha`, `area_70_1986_ha`, `area_70_1986_pct`, `area_alguna_vez70_1986_2024_ha` y `siempre70_delta_por_excluir_1985_ha`. Retira `tasa_presion_urbana_indicativa_por_1000ha` |
| `area_siempre70_ha` | **Sin cambio.** 3 542.972 ha en el ACR |
| `area_alguna_vez70` | Valor primario 6 557.361 ha (1986–2024); sensibilidad 6 587.570 ha (1985–2024) |
| Figura F01 | Se dibuja 1986–2024. El punto de 1985 se representa abierto y anotado como ruptura de inicio de serie |
| Figura F02 | Sin cambio en `siempre 70`. Se añade la nota de robustez |
| Dictamen del Paso 10 | Se corrige la fila de superficie de anillos y se declara la unidad |
