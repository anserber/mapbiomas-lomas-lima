# Dictamen — Ruptura de inicio de serie y regímenes de sensor

**Fecha:** 2026-08-05
**Estado:** CERRADO
**Alcance:** cinco ámbitos del ACR Sistema de Lomas de Lima y tres anillos
disueltos del sistema
**Controles que lo sustentan:** 6E4, 6E5 y 6E6-B

> **Corrección del 6 de agosto de 2026.** Las desviaciones estándar publicadas
> inicialmente en este documento (133,9 ha en el régimen I y 128,8 ha en Ancón)
> se calcularon incluyendo el residual de 1986, que necesita a 1985 como año
> vecino. Al adoptarse la decisión de excluir 1985 de todo cálculo, el residual
> de 1986 deja de ser calculable y el régimen I pasa a abarcar 1987-1999. Las
> cifras vigentes son las de las tablas siguientes. El cambio refuerza el
> hallazgo en lugar de debilitarlo: el régimen I resulta mucho más estable de lo
> estimado, de modo que la inestabilidad no procede de la antigüedad de la serie
> sino de la mezcla de sensores del régimen II.

## Decisión ejecutiva

1. **El año 1985 queda excluido de todo cálculo de cambio y de línea base.** La
   serie se reporta 1986–2024.
2. **`siempre 70` se mantiene sin modificación.** Se demostró que el indicador
   es insensible a la exclusión de 1985.
3. **Se incorpora a la metodología la tabla de tres regímenes de sensor** como
   limitación cuantificada de la serie.
4. **Se declara que solo el tramo 2014–2024 sostiene lecturas interanuales.**

## Fundamento

### 1985 es una ruptura cartográfica de inicio de serie

Los cuatro criterios del protocolo de control se cumplen sobre el candidato de
1 242.401 ha de Ancón:

| Criterio | Resultado |
|---|---|
| Sincronía | Ingreso completo en 1986, valor idéntico a doce decimales durante 1986–1990 |
| Retorno | 100 % de persistencia a 1990; 0 % de persistencia a 2024 |
| Espectral | NDVI −0.41 % y EVI2 −0.30 % entre 1985 y 1986, mientras el área pasa de 0 a 1 242 ha |
| Insumo | 9 escenas y 56.7 % de nubes en 1985 frente a 27 en 1986 y 57 en 1988, con satélite, versión y regiones idénticos |

El origen del candidato procede en un **99.725 %** de la clase 68, complemento
directo del clasificador binario loma/no-loma descrito en el ATBD.

1985 es además el peor año de los 38 comparables en las tres métricas de insumo
a la vez. El déficit medido sobre el ACR completo es de **−29.3 %** respecto de
la meseta 1986–1990, y la línea base del área de estudio varía **+31.9 %** entre
el primer y el segundo año de la serie.

### La causa general propuesta fue descartada

La hipótesis de que el número de escenas explicara la inestabilidad interanual
a lo largo de los 40 años no resistió la comprobación: Pearson −0.226, Spearman
−0.104, y +0.053 al excluir 1986. Los demás años de insumo pobre no producen
anomalías comparables. El resultado negativo se conserva y se reporta.

### El factor que sí discrimina es el régimen de sensor

| Régimen | Periodo | DE del residual, ACR | Máximo |
|---|---|---:|---:|
| L5 solo | 1987–1999 | 35.7 ha | 98.4 ha |
| Mezcla L5/L7/lx | 2000–2013 | 129.2 ha | 286.8 ha |
| **L8 solo** | **2014–2022** | **10.8 ha** | **20.1 ha** |

El régimen II, el de mezcla de sensores, es **3,6 veces** más volátil que
Landsat 5 solo y **doce veces** más que Landsat 8 solo. En Ancón el patrón es
equivalente: 36,0 → 126,6 → 11,4 ha. La inestabilidad no procede de la
antigüedad de la serie sino de la heterogeneidad del sensor.

La ruptura 2000–2001, documentada con anterioridad, pertenece a un bloque de
inestabilidad 2000–2005 coincidente con la incorporación de Landsat 7.

### Los indicadores de persistencia son robustos

El control 6E6-B midió el efecto de pasar de la ventana de 40 años a la de 39:

- `siempre 70`: variación **0.000 ha en las ocho unidades**. No existe un solo
  píxel que haya sido clase 70 durante 1986–2024 y no en 1985.
- `alguna vez 70`: **−30.209 ha en el ACR (−0.46 %)** y **−111.049 ha en los
  anillos (−2.34 %)**, correspondientes a píxeles clasificados como clase 70
  únicamente en 1985. Es una depuración.

La reducción de Ancón, −18.941693 ha, coincide a doce decimales con el valor de
salida medido de forma independiente por el control 6E4.

## Reglas de interpretación que se incorporan

1. El intercambio `68↔70` no es cambio de cobertura: es el detector binario de
   loma activándose o desactivándose. La clase 68 no sobrescribe a la clase 70
   en la jerarquía de integración; es su complemento.
2. Ninguna afirmación de cambio puede tomar 1985 como referencia.
3. Ninguna lectura interanual anterior a 2014 es comparable con otra sin
   declarar el régimen de sensor correspondiente.
4. La persistencia multianual y los eventos con ventana W5 son los únicos
   indicadores del proyecto que atraviesan sin alteración las discontinuidades
   documentadas del insumo. Esta propiedad está medida, no supuesta.
5. El cambio de versión de mosaico en 2023, de la versión 4 a la 5, se declara
   como discontinuidad de insumo dentro de la ventana de vigilancia reciente
   censurada. No produce quiebre visible en la salida: el residual de 2023 es de
   +6.3 ha.

## Rupturas conocidas — lista actualizada

| Identificador | Unidad | Periodo | Magnitud | Naturaleza |
|---|---|---|---:|---|
| **RUPTURA_INICIO_SERIE_68_70** | **Ancón y sistema** | **1985–1986** | **1 242.401 ha en Ancón; +31.9 % en el ACR** | **Insumo deficiente del primer año** |
| Ancón 2000–2001 | Ancón | 2000–2001 | 532.735 ha | Cambio de asignación temática 70→68 |
| CV-042 | Carabayllo 2 | 2014–2015 | 10.734 ha | Ruptura estable 70→13/68 |

La primera entrada es nueva y es la de mayor magnitud de las tres.

## Hallazgos de auditoría que quedan resueltos

| Hallazgo | Estado |
|---|---|
| **A1** — Discrepancia de áreas de anillos entre el dictamen del Paso 10 y la tabla maestra | **Resuelto.** No son dos definiciones sino tres: vectorial 22 859.206 ha, de grilla 22 846.929 ha y clasificada 22 839.847 ha. La diferencia entre las dos últimas es `sin_dato_ha` = 7.082 ha. Se declaran las tres en el diccionario y se adopta la de grilla como denominador de las tasas |
| **A2** — Campo `tasa_presion_urbana_indicativa_por_1000ha` que suma señales no sumables | **Resuelto.** Se retira de la tabla pública v2. La v1 conserva el registro |
| **A4** — Salto 1985–1986 no declarado como ruptura | **Resuelto.** Declarado con evidencia de cuatro criterios y línea base trasladada a 1986 |
| **M1** — Identidad exacta entre `area_70_2024_ha` y `area_siempre70_ha` en Ancón y Carabayllo 1 | **Resuelto.** El control 6E4 demostró 0 % de persistencia a 2024 de los píxeles ingresados en 1986, de modo que el conjunto de 2024 está contenido en el de 1985. No es un error de cálculo |

## Aporte a MapBiomas Perú

El conjunto de los tres controles constituye una auditoría temporal localizada
y reproducible de la clase beta `70 — Loma costera` en un área protegida
concreta. Entrega:

- un punto de ruptura de inicio de serie identificado, cuantificado y explicado
  por el insumo;
- una caracterización de la estabilidad de la clase por régimen de sensor, con
  volatilidad medida;
- una hipótesis alternativa descartada de forma explícita;
- código reproducible aplicable a otras lomas costeras y a futuras colecciones.

No se afirma que exista una deficiencia del producto. Se documenta el
comportamiento observado de una clase declarada beta por sus propios autores,
en las condiciones concretas de un área de estudio.

## Trazabilidad

```text
04_extraccion_series/01_scripts/paso06E4_ancon_68_70_1985_1990.js
04_extraccion_series/01_scripts/paso06E5_auditoria_insumo_landsat_1985_2024.js
04_extraccion_series/01_scripts/paso06E6_sensibilidad_ventana_1986_2024.js
04_extraccion_series/01_scripts/paso06E6B_sensibilidad_ventana_1986_2024.js

05_analisis_temporal/evidencia/control_paso06E4_ancon_68_70_1985_1990.md
05_analisis_temporal/evidencia/control_paso06E5_insumo_landsat_1985_2024.md
05_analisis_temporal/evidencia/control_paso06E6B_sensibilidad_ventana_1986_2024.md
05_analisis_temporal/evidencia/paso06E4_ancon_mosaico_1985_1986.png
05_analisis_temporal/evidencia/paso06E4_ancon_ndvi_1985_1986.png

09_integracion_resultados/02_final/tabla_maestra_resultados_publicos_v2.csv
08_cierre_metodologico/02_final/adenda_metodologica_v1.1_ruptura_1985.md
```
