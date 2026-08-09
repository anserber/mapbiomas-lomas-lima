# Protocolo operativo — evaluación visual ciega del Paso 8D

**Fecha:** 2026-07-29  
**Instrumento:** `ficha_evaluacion_visual_ciega_paso08.xlsx`  
**Estado inicial:** 66 evaluaciones pendientes

## 1. Regla crítica de orden

Las evaluaciones deben completarse estrictamente desde `EVAL-001` hasta
`EVAL-066`.

No se debe:

- ordenar la tabla;
- agrupar primero los sectores públicos;
- reemplazar casos difíciles;
- eliminar filas;
- buscar las repeticiones;
- abrir `clave_repeticiones_ciegas_paso08.csv`.

La muestra contiene:

- 39 evaluaciones públicas;
- 27 evaluaciones KBA restringidas;
- 66 evaluaciones totales;
- 6 repeticiones ciegas incluidas dentro de las 66.

El visor público por sí solo no permite comenzar y terminar el instrumento en
orden, porque `EVAL-003` ya corresponde al dominio KBA. Antes de iniciar
`EVAL-001` debe quedar operativo el visor restringido KBA.

## 2. Archivos y confidencialidad

### Visor público

```text
06_validacion_visual/00_scripts/paso08D_visor_publico_ciego.js
```

### Ficha restringida

```text
06_validacion_visual/kba_restricted/ficha_evaluacion_visual_ciega_paso08.xlsx
```

### Datos KBA restringidos

```text
06_validacion_visual/kba_restricted/
```

La ficha contiene coordenadas KBA y no debe publicarse en GitHub, Google Drive
público ni anexarse íntegramente al trabajo final.

## 3. Unidad visual examinada

- Ventana central: 150 × 150 m.
- Equivale aproximadamente a una cuadrícula de 5 × 5 píxeles Landsat de 30 m.
- Contexto máximo de interpretación: 500 m alrededor.
- La capa magenta indica el candidato cartográfico; no constituye por sí sola
  evidencia de cambio.
- La evaluación se realiza a nivel de parche y contexto, no de un píxel
  aislado.
- El área calculada dentro de la ventana de 150 × 150 m representa solo la
  fracción visible del candidato. No debe confundirse con el área total del
  parche conectado.

## 4. Secuencia obligatoria para cada `EVAL-xxx`

1. Seleccionar el mismo `id_muestra` en el visor correspondiente.
2. Confirmar que el nombre de la unidad, estrato y años coincidan con la fila
   Excel.
3. Observar el mosaico MapBiomas del año inicial en color natural.
4. Observar el año del evento en color natural.
5. Observar el año final disponible en color natural.
6. Repetir la comparación en falso color.
7. Revisar NDVI para los mismos años.
8. Examinar primero la ventana de 150 × 150 m.
9. Ampliar hasta 500 m solo para interpretar contexto, bordes, sombras,
   urbanización, relieve o patrones espectrales.
10. Registrar las fuentes y fechas antes de emitir el veredicto.
11. Completar evidencia, veredicto, proceso, confianza y observaciones.
12. Verificar que `estado_fila` deje de figurar como `PENDIENTE`.
13. Guardar la ficha antes de cambiar al siguiente `id_muestra`.

## 5. Campos que debe completar el evaluador

### `fuente_visual_1` y `fuente_visual_2`

Valores permitidos:

```text
MOSAICO_MAPBIOMAS
SENTINEL_2
GOOGLE_EARTH_HISTORICO
GOOGLE_SATELLITE_ACTUAL
OTRA
NO_DISPONIBLE
```

La fuente principal obligatoria es el mosaico MapBiomas. Las demás fuentes son
controles auxiliares: no sustituyen la clasificación, las transiciones ni las
superficies derivadas de MapBiomas.

Para mantener un procedimiento homogéneo dentro del mismo visor, la fuente
adicional principal será:

```text
OTRA:
Landsat Collection 2 Level 2, mediana anual con máscara QA independiente.
```

Sus capas aparecen como `Landsat C2 natural` y `Landsat C2 falso color`.
Constituyen una cadena de procesamiento complementaria y reproducible, aunque
comparten el sensor Landsat con los mosaicos de MapBiomas. Cuando exista una
fuente de mayor resolución o temporalmente más adecuada, puede añadirse como
segunda fuente complementaria.

Sentinel-2 es opcional para años recientes y se utiliza únicamente como ayuda
de resolución. No constituye verdad de referencia ni árbitro automático.

Para los estratos urbanos `E2` y `E3`, antes de recurrir a fuentes externas se
deben revisar los controles internos disponibles en MapBiomas:

```text
NDBI
NUACI
tamaño del parche conectado de clase 24
persistencia temporal
forma, textura y contexto urbano
```

El tamaño mínimo de referencia del módulo urbano es aproximadamente 0.5 ha. La
comparación debe realizarse con el parche completo conectado, no solo con la
fracción incluida en la ventana.

En `E2` y `E3` deben registrarse por separado: (a) la huella conectada de la
transición `70→24`, y (b) el parche completo conectado de clase 24 en el año
del evento y en el año final. Solo el segundo puede compararse con la referencia
aproximada de 0.5 ha del módulo urbano.

### Control cuantitativo por píxel

Para reducir la subjetividad, el visor calcula únicamente dentro de los
píxeles de la máscara candidata:

- área candidata;
- media, mediana, desviación estándar y cantidad de observaciones NDVI;
- NDVI de los años inicial, evento y final;
- diferencia entre año inicial y evento;
- diferencia entre evento y año final;
- resultados separados para el mosaico MapBiomas y Landsat Collection 2.

La interpretación del delta es:

```text
delta > 0: aumento del NDVI;
delta < 0: disminución del NDVI;
delta cercano a 0: estabilidad espectral aproximada.
```

Este control complementa la inspección visual. No constituye validación de
campo ni debe utilizarse aisladamente para emitir el veredicto.
Si para años antiguos no existe otra fuente defendible, registrar
`NO_DISPONIBLE` y evaluar si la evidencia total es suficiente.

### `fecha_fuente_1` y `fecha_fuente_2`

Formato:

```text
YYYY
YYYY-MM-DD
YYYY; YYYY; YYYY
N/A
```

Cuando una misma fuente se compare en los tres momentos de la evaluación,
registrar los años en orden `inicio; evento; final`. No inventar una fecha
exacta si la interfaz solo muestra el año.

### `evidencia_suficiente`

```text
SI
NO
```

Marcar `NO` cuando nubes, resolución, sombras, diferencias estacionales o falta
de una imagen comparable impidan decidir.

### `veredicto_visual`

```text
ACUERDO
DESACUERDO
INDETERMINADO
```

- `ACUERDO`: la evidencia respalda la trayectoria esperada del estrato.
- `DESACUERDO`: existe evidencia suficiente y contradice la trayectoria.
- `INDETERMINADO`: la evidencia no permite una decisión defendible.

Regla obligatoria:

```text
evidencia_suficiente = NO
→ veredicto_visual = INDETERMINADO
→ confianza = BAJA
```

### `proceso_observado`

```text
PERSISTENCIA_70
CONVERSION_A_URBANO
INTERCAMBIO_70_68
RECUPERACION_A_70
CAMBIO_70_13
OTRO_CAMBIO
NO_DETERMINABLE
```

### `confianza`

Usar la lista disponible en el instrumento. Regla interpretativa:

- `ALTA`: patrón claro en varias fuentes y fechas comparables.
- `MEDIA`: patrón plausible, pero existe alguna limitación.
- `BAJA`: señal ambigua, evidencia parcial o caso indeterminado.

### `observaciones`

Redactar una nota corta, factual y reproducible. Debe indicar:

- qué cambió o permaneció;
- en qué parte de la ventana;
- qué fuente lo respalda;
- cualquier limitación.

Ejemplo de estructura, no de resultado:

```text
El parche central mantiene una respuesta espectral semejante entre YYYY y
YYYY. El falso color y NDVI respaldan la permanencia; mosaico inicial con
resolución limitada.
```

Evitar términos causales como `invasión`, `ilegal`, `degradación` o
`deforestación` salvo que una fuente externa específica los demuestre.

### `evaluador` y `fecha_revision`

- Evaluador: `Jhoreck Llanto`.
- Fecha: día real de evaluación en formato `YYYY-MM-DD`.

## 6. Lectura esperada por estrato

Estas reglas orientan la evaluación, pero no obligan a marcar acuerdo.

| Estrato | Trayectoria cartográfica evaluada | Proceso esperado |
|---|---|---|
| `E1_PERSISTENTE70` | clase 70 estable durante la serie | `PERSISTENCIA_70` |
| `E2_URBANO_W5` | transición estable hacia clase 24 con ventana W5 | `CONVERSION_A_URBANO` |
| `E3_URBANO_CENSURADO` | transición reciente hacia clase 24 sin cinco años posteriores completos | `CONVERSION_A_URBANO` |
| `E4_INTERCAMBIO_68_70` | intercambio entre clases 68 y 70 | `INTERCAMBIO_70_68` |
| `E5_RECUPERACION_68_70` | transición estable desde clase 68 hacia clase 70 | `RECUPERACION_A_70` |
| `E6_CAMBIO_70_13` | transición de clase 70 hacia clase 13 | `CAMBIO_70_13` |

Para `E2` y `E3`, el veredicto se refiere a la coherencia visual de una
transición hacia superficie urbana cartografiada, no a la legalidad ni al tipo
de ocupación.

## 7. Casos difíciles

- No sustituir el sector.
- No consultar otro candidato del mismo estrato para “comparar respuestas”.
- Registrar nubes, baja resolución, sombreado, relieve, estacionalidad o
  desacuerdo entre fuentes.
- Si la clase magenta no coincide claramente con la evidencia, revisar
  color natural, falso color y NDVI antes de decidir.
- Si continúa la duda, conservar `INDETERMINADO`.

## 8. Control de cierre

La hoja `CONTROL` debe mostrar:

```text
Evaluaciones totales: 66
Completas: 66
En revisión: 0
Incompletas: 0
Pendientes: 0
Estado del Paso 8D: AVANZAR
```

Solo entonces se puede abrir la clave de repeticiones y ejecutar el Paso 8E de
concordancia, consistencia intraevaluador y dictamen de confianza.
