# Sensibilidad de los indicadores de persistencia a la exclusión de 1985

**Estado:** revisado; **predicciones confirmadas**
**Unidades:** cinco ámbitos del ACR y tres anillos disueltos del sistema
**Fecha:** 2026-08-05
**Script:** `04_extraccion_series/01_scripts/paso06E6B_sensibilidad_ventana_1986_2024.js`

## Motivo

Los controles 6E4 y 6E5 establecieron que 1985 es un año de insumo deficiente
con subdetección medida de −29.3 % de la clase 70 en el ACR, y se decidió
excluirlo de todo cálculo de cambio.

Los indicadores `siempre 70` y `alguna vez 70` se definen sobre la ventana
completa 1985–2024. Corresponde medir cuánto cambian al pasar a la ventana
1986–2024, antes de decidir si se actualizan los productos públicos.

## Predicciones registradas antes de ejecutar

Ambas quedaron escritas en el encabezado y en el bloque `F` del script antes de
su primera ejecución válida.

- **P1.** `siempre70_delta_ha` en `acr|ancon` debe ser 0.000, porque las
  1 242.401 ha que 1985 no detectó tienen 0 % de persistencia hasta 2024 según
  el control 6E4.
- **P2.** El delta total del ACR debe quedar por debajo de 60 ha, es decir menos
  del 1.8 % sobre 3 542.972 ha.

## Nota sobre la ejecución

La primera versión del script (`paso06E6`) falló con el mensaje
`Collection.loadTable: Asset ... does not exist or doesn't allow this operation`.
El asset sí existe: los pasos 6E4 y 6E5 lo leyeron correctamente. La causa fue
la mezcla mediante `merge()` de dos colecciones procedentes de assets distintos
y con esquemas de propiedades distintos, materializada dentro de
`reduceRegions`. La versión `paso06E6B` sustituye la mezcla por dos reducciones
independientes y adopta el patrón ya probado en `paso07D2`. Ambos scripts se
conservan.

## Control de integridad

| Campo | Calculado | Esperado | Diferencia |
|---|---:|---:|---:|
| Área de grilla del ACR (ha) | 13 468.752892 | 13 468.753 | −0.000108 |
| Clase 70 en 1985 (ha) | 3 988.584794 | 3 988.6 | −0.015 |
| Clase 70 en 1986 (ha) | 5 262.234122 | 5 262.2 | +0.034 |
| Clase 70 en 2024 (ha) | 3 547.649913 | 3 547.650 | −0.000087 |
| `siempre 70` 40 años (ha) | 3 542.971973 | 3 542.972 | −0.000027 |
| `alguna vez 70` 40 años (ha) | 6 587.570084 | 6 587.570 | +0.000084 |

Los seis controles reproducen la tabla maestra.

## Resultado 1 — `siempre 70` no cambia

`siempre70_delta_ha` es **0.000 en las ocho unidades**. El campo
`ganados_por_excluir_1985_ha`, que contabiliza los píxeles clase 70 en todos los
años de 1986 a 2024 pero no en 1985, es **0.000 en todas ellas**.

P1 se confirma de forma exacta. P2 se supera: el cambio no es inferior a 60 ha,
es **nulo**.

Interpretación: **no existe un solo píxel que haya sido clase 70 durante los 39
años de 1986 a 2024 y no lo haya sido en 1985.** El núcleo persistente ya estaba
correctamente detectado en 1985, pese a tratarse del peor mosaico de la serie.

Es coherente con el mecanismo del ATBD: el núcleo persistente presenta la señal
espectral más fuerte e inequívoca y supera el umbral de probabilidad del 40 %
incluso con nueve escenas y 56.7 % de nubes. El déficit de 1985 se concentra
íntegramente en el margen inestable de la clase, es decir en los píxeles que
oscilan de todos modos.

**Consecuencia:** `siempre 70` = 3 542.972 ha para el ACR es robusto frente a la
discontinuidad documentada del inicio de serie. No procede modificarlo.

## Resultado 2 — `alguna vez 70` sí cambia, a la baja

| Unidad | 1985–2024 (ha) | 1986–2024 (ha) | Δ (ha) |
|---|---:|---:|---:|
| acr\|amancaes | 209.535560 | 209.535560 | 0.000000 |
| acr\|ancon | 5 564.792192 | 5 545.850499 | **−18.941693** |
| acr\|carabayllo_1 | 79.915899 | 79.915899 | 0.000000 |
| acr\|carabayllo_2 | 193.505358 | 193.505358 | 0.000000 |
| acr\|villa_maria | 539.821076 | 528.553537 | −11.267538 |
| **Total ACR** | **6 587.570084** | **6 557.360853** | **−30.209231** |
| sistema\|0_500 | 1 588.679298 | 1 550.584709 | −38.094589 |
| sistema\|500_1000 | 1 120.587724 | 1 107.558192 | −13.029532 |
| sistema\|1000_2000 | 2 043.546665 | 1 983.621793 | −59.924872 |
| **Total anillos** | **4 752.813687** | **4 641.764694** | **−111.048993** |

Variación relativa: **−0.46 %** en el ACR y **−2.34 %** en los anillos.

### Control cruzado independiente

La reducción de Ancón, **−18.941693 ha**, coincide a doce decimales con el campo
`salida_70_1985_1986` medido por el control 6E4 (18.941692625979584). Dos
scripts con lógicas distintas producen el mismo valor.

Son los píxeles clasificados como clase 70 en 1985 y nunca más. Es decir, 1985
presenta el comportamiento completo de un clasificador con insumo insuficiente:
omite 1 242 ha de señal real en Ancón e introduce 19 ha que no se repiten en
ningún año posterior.

La reducción de `alguna vez 70` al excluir 1985 constituye por tanto una
**depuración**, no una pérdida de información.

### Gradiente entre núcleo y periferia

El efecto relativo es cinco veces mayor en los anillos que en el ACR. Es
consistente con la naturaleza del margen desértico, donde la señal de la clase
70 es más débil y la clasificación más sensible al ruido del insumo.

## Resultado 3 — Tres definiciones de área

El script devolvió 22 839.847 ha de superficie para los anillos, frente a
22 846.929 ha de la tabla maestra. La diferencia se verificó contra
`serie_indicadores_anillos_periferia_externa_1985_2024.csv` y corresponde
exactamente al campo `sin_dato_ha`.

| Anillo | Vectorial | Grilla | Clasificada | Sin dato |
|---|---:|---:|---:|---:|
| 0–500 m | 5 265.401 | 5 262.371 | 5 262.371 | 0.000 |
| 500–1 000 m | 5 519.223 | 5 516.048 | 5 514.000 | 2.048 |
| 1 000–2 000 m | 12 074.583 | 12 068.511 | 12 063.476 | 5.035 |
| **Total** | **22 859.206** | **22 846.929** | **22 839.847** | **7.082** |

Existen tres definiciones de superficie, las tres presentes en los datos del
proyecto:

- **vectorial** (`area_ref_ha`): superficie del polígono;
- **de grilla** (`area_pixeles_ha`): superficie de los píxeles MapBiomas;
- **clasificada** (`clasificada_ha`): grilla menos los píxeles sin dato.

El dictamen del Paso 10 publicó la vectorial (22 859.206 ha) y la tabla maestra
la de grilla (22 846.929 ha), sin declarar la diferencia. En los cinco ámbitos
del ACR `sin_dato_ha` es 0.000 y las tres coinciden, motivo por el cual los
controles del ACR cuadraron de forma exacta y los de los anillos no.

Queda resuelto el hallazgo A1 de la auditoría.

## Decisión metodológica

1. **`siempre 70` se mantiene con la ventana 1985–2024** y valor 3 542.972 ha
   para el ACR. El resultado nulo del delta se reporta como evidencia de
   robustez del indicador, no como ausencia de comprobación.
2. **`alguna vez 70` se reporta con la ventana 1986–2024** como valor primario, y
   con la ventana 1985–2024 como sensibilidad. Ambas columnas se conservan en la
   tabla maestra v2.
3. **Se declara la línea base 1986** para todos los cálculos de cambio. El campo
   `area_70_1986_ha` se incorpora a la tabla maestra v2.
4. **Se declaran las tres definiciones de superficie** en el diccionario. La
   superficie de grilla se mantiene como denominador de todas las tasas
   publicadas, por consistencia dimensional con los numeradores en hectáreas de
   píxel.
5. El campo `tasa_presion_urbana_indicativa_por_1000ha` se retira de la tabla
   pública, conforme al hallazgo A2 de la auditoría. La versión v1 conserva el
   registro histórico.

## Productos derivados

```text
09_integracion_resultados/02_final/tabla_maestra_resultados_publicos_v2.csv
08_cierre_metodologico/02_final/adenda_metodologica_v1.1_ruptura_1985.md
05_analisis_temporal/evidencia/dictamen_ruptura_1985_y_regimenes_sensor.md
```
