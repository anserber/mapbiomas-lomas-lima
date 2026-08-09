# Validación de las fases 6A–6C

**Fecha:** 28 de julio de 2026  
**Estado general:** PASS  
**Alcance:** auditoría del asset, inventario interanual y selección de periodos  

## Fase 6A — Asset de transiciones

| Control | Resultado |
|---|---:|
| Acceso | Correcto |
| Bandas | 60 |
| Transiciones anuales consecutivas | 39 |
| Bandas multianuales o especiales | 21 |
| Primera banda | `transitions_1985_1986` |
| Última banda | `transitions_2010_2024` |
| Tipo | `signed int16` |
| CRS | EPSG:4326 |
| Escala nominal | 30 m |
| Ámbitos ACR | 5 |

## Fase 6B — Inventario temporal

| Conjunto | Filas de entrada | Cambios interanuales |
|---|---:|---:|
| ACR | 200 | 195 |
| Anillos | 720 | 702 |
| KBA | 40 | 39 |

Controles:

- periodo 1985–2024 completo;
- años convertidos a enteros;
- solo se compararon años consecutivos;
- se conservaron los granos espaciales separados;
- los cambios exactamente iguales a cero se excluyeron de los rankings;
- pruebas del cálculo interanual aprobadas.

## Fase 6C — Selección

Se conservaron 17 periodos candidatos y se seleccionaron:

```text
12 periodos anuales
3 periodos multianuales
15 bandas de transición
```

La selección equilibra:

- saltos de loma;
- crecimiento urbano;
- anomalías iniciales;
- el periodo 2009–2010 bajo advertencia;
- ACR, anillos y KBA;
- cierre reciente de la serie;
- balances de largo plazo.

## Limitación

Los rankings describen magnitud de cambios de clasificación. No constituyen
prueba de pérdida ecológica, recuperación, degradación ni causalidad. La
codificación del asset y las áreas por transición deben verificarse antes de
interpretar los resultados.

## Dictamen

Las fases 6A–6C están aprobadas. Se autoriza ejecutar la Fase 6D1 para comprobar
la fórmula de codificación de las transiciones oficiales.

## Fase 6D1 — Codificación

Periodos comprobados:

```text
1985–1986
2009–2010
2023–2024
```

Resultado:

```text
Área evaluada por periodo: 13 468.752893 ha
Área diferente: 0 ha
Diferencia: 0 %
Codificación coincide: 1 en los tres periodos
```

La fórmula queda confirmada:

```text
código de transición = clase inicial × 100 + clase final
```

Ejemplos observados:

```text
7070  loma costera → loma costera
7024  loma costera → infraestructura urbana
2470  infraestructura urbana → loma costera
7013  loma costera → otra formación no boscosa
7068  loma costera → otra área natural sin vegetación
```

**Dictamen 6D1:** PASS.

## Fase 6D2 — Piloto de transiciones ACR

Bandas comprobadas:

```text
transitions_1985_1986
transitions_2023_2024
transitions_1985_2024
```

Resultados:

```text
Ámbitos: 5
Bandas: 3
Filas: 115
Códigos de transición distintos: 22
Clases no documentadas: 0
Filas con los 11 campos analíticos completos: 115
Área total por banda: 13 468.752893 ha
```

El primer registro contiene las 11 propiedades previstas:

```text
area_ha
banda
from_class
from_documentada
id_ambito
nombre
to_class
to_documentada
transition_code
year_end
year_start
```

`system:index` es un identificador añadido automáticamente por Earth Engine y
no forma parte del esquema analítico.

**Dictamen 6D2:** PASS. Se autoriza la extracción de las 15 bandas
seleccionadas en tres bloques controlados de cinco bandas.

## Fase 6D3 — Extracción de transiciones ACR

| Bloque | Bandas | Filas | Esquema completo | Clases no documentadas | Estado | Task ID |
|---|---:|---:|---:|---:|---|---|
| 1 | 5 | 159 | 159 | 0 | Completed | `WYQBVP7AGVNJLXG77JTOPHTJ` |
| 2 | 5 | 182 | 182 | 0 | Completed | `7YIVLYJ2VSRHYRCYCUB3JTWZ` |
| 3 | 5 | 218 | 218 | 0 | Completed | `R6UBT6A2U7VTZMWCYEFI4GGC` |

Controles comunes:

```text
Ámbitos por bloque: 5
Área total por banda: 13 468.752893 ha
Intentos por tarea: 1
```

Los tres bloques abarcan las 15 bandas seleccionadas y suman 559 filas antes
de la consolidación.

### Consolidación y auditoría

Los tres CSV originales se conservaron sin modificaciones en:

```text
05_analisis_temporal/00_raw/transiciones_acr/
```

Producto consolidado:

```text
05_analisis_temporal/01_intermediate/
transiciones_acr_15_periodos_consolidado.csv
```

Resultados de control:

| Control | Resultado |
|---|---:|
| Filas | 559 |
| Columnas | 11 |
| Bandas | 15 |
| Ámbitos | 5 |
| Códigos distintos | 27 |
| Duplicados exactos | 0 |
| Duplicados de `id_ambito × banda × transition_code` | 0 |
| Errores en la fórmula del código | 0 |
| Inconsistencias entre banda y años | 0 |
| Nombres discordantes | 0 |
| Clases no documentadas | 0 |
| Áreas no positivas o no finitas | 0 |
| Bandas sin los cinco ámbitos | 0 |

El área agregada de cada banda es `13 468.752893 ha`. La diferencia absoluta
máxima entre las 15 sumas es menor que `0.000001 ha`, por lo que solo existe
residuo numérico de punto flotante.

La auditoría reproducible se encuentra en:

```text
05_analisis_temporal/00_scripts/
consolidar_y_validar_transiciones_acr_d3.py

05_analisis_temporal/evidencia/
control_transiciones_acr_d3.json
```

SHA-256 del consolidado:

```text
cd7d0d2fd5debe742510b60991b8b382368d83460cabbdbb672e446785a1349e
```

**Dictamen final 6D3:** PASS. El consolidado es apto para el análisis de
transiciones. Los códigos todavía describen cambios de clasificación y no
deben interpretarse por sí solos como pérdida, recuperación o causalidad
ecológica.

## Fase 6D4 — Control preliminar de cobertura en anillos

El bloque 1 contiene las 18 unidades esperadas: 15 anillos por ámbito y 3
anillos del sistema. Las cinco bandas cubren todas las unidades y no presentan
clases no documentadas.

Se detectó una máscara constante del asset de transiciones:

| Nivel | Área de grilla (ha) | Área enmascarada (ha) | Área enmascarada (%) |
|---|---:|---:|---:|
| Anillos por ámbito | 23 115.749484 | 7.082233 | 0.030638 |
| Sistema disuelto | 22 857.646141 | 7.082233 | 0.030984 |

La diferencia se repite, dentro del residuo numérico, en las cinco bandas del
bloque. Por tanto, corresponde a una máscara espacial estable del asset y no a
pérdida variable de registros durante la reducción.

Regla metodológica:

1. conservar la máscara oficial;
2. no convertir los píxeles enmascarados en clase 0;
3. calcular porcentajes de transiciones sobre el área efectivamente cubierta;
4. reportar por separado la cobertura respecto al área total de la grilla;
5. no sumar los anillos por ámbito para representar el sistema, debido a sus
   solapamientos.

**Dictamen preliminar 6D4:** PAUSADO. La cobertura del asset es aceptable, pero
la auditoría del 28 de julio de 2026 confirmó que el anillo `0_500` incorpora
por completo el enclave interno excluido de Lomas de Carabayllo 2
(`10.710224 ha`). Antes de aprobar 6D4 debe decidirse si el análisis principal
representará proximidad a todos los límites legales o solo periferia externa.
La recomendación vigente es separar el enclave y utilizar periferia externa
para la comparación principal. Véase:

```text
02_zonas_influencia/evidencia/paso_03/
auditoria_enclave_carabayllo2_20260728.md
```

**Actualización del 28 de julio de 2026:** los assets corregidos de periferia
externa y el enclave separado superaron el control métrico y topológico en
GEE. La fase permanece pausada únicamente hasta reemplazar las series
históricas de anillos generadas con los assets anteriores.

## Revalidación de la fase 6D3

Los tres CSV del ACR se volvieron a descargar y se compararon con las copias
canónicas conservadas en:

```text
05_analisis_temporal/00_raw/transiciones_acr/
```

Los hashes SHA-256 coinciden archivo por archivo:

```text
0174c26578d0caad79188a9565b7818d8a37f63806c9d23af6b97f63c04a3d4a
serie_transiciones_acr_bloque_1_de_3.csv

5aa358b393a198960df1bbaca8fbdee30977ddb63ba4e4cf4a089550bf6ae2cb
serie_transiciones_acr_bloque_2_de_3.csv

825611aecc5082e17b182b47107b5c57187de0e7a9150f85dd1efe00e09603a5
serie_transiciones_acr_bloque_3_de_3.csv
```

La auditoría independiente confirmó:

| Control | Resultado |
|---|---:|
| Filas | 559 |
| Bandas | 15 |
| Ámbitos | 5 |
| Combinaciones ámbito–banda | 75 de 75 |
| Duplicados ámbito–banda–transición | 0 |
| Errores de identidad | 0 |
| Errores de periodo | 0 |
| Errores de codificación | 0 |
| Clases no documentadas | 0 |
| Áreas inválidas | 0 |
| Ámbitos con cobertura inestable | 0 |

La comparación con el consolidado canónico produjo las mismas 559 claves y
una diferencia máxima de área de `0 ha`. La única diferencia textual fue la
capitalización de los booleanos (`true` frente a `True`), sin efecto analítico.

**Dictamen de revalidación 6D3:** PASS. Se mantiene como producto canónico:

```text
05_analisis_temporal/01_intermediate/
transiciones_acr_15_periodos_consolidado.csv
```

## Fase 6D4-R — Transiciones de la periferia externa

La fase se repitió con los assets corregidos:

```text
projects/mapbiomas-lomas-jhoreck/assets/inputs/
anillos_por_ambito_periferia_externa_gee

projects/mapbiomas-lomas-jhoreck/assets/inputs/
anillos_sistema_periferia_externa_gee
```

El enclave interno de SEDAPAL se conservó como unidad separada y su
intersección con ambas familias de anillos fue `0 ha`.

Resultados consolidados:

| Control | Resultado |
|---|---:|
| Filas | 3,357 |
| Columnas | 16 |
| Bandas | 15 |
| Unidades espaciales | 18 |
| Combinaciones unidad–banda | 270 de 270 |
| Códigos distintos | 51 |
| Duplicados unidad–banda–transición | 0 |
| Errores de identidad | 0 |
| Errores de periodo | 0 |
| Errores de codificación | 0 |
| Clases no documentadas | 0 |
| Áreas inválidas | 0 |
| Unidades con cobertura inestable | 0 |

La diferencia máxima de cobertura entre bandas de una misma unidad fue
`3.6e-11 ha`, atribuible a precisión numérica.

Producto validado:

```text
04_extraccion_series/02_resultados/
serie_transiciones_anillos_periferia_externa_seleccionadas.csv
```

**Dictamen final 6D4-R:** PASS. El producto corregido sustituye cualquier
extracción anterior de transiciones de anillos.
