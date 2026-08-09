# Plantilla por lote — evaluación visual ciega EVAL-016 a EVAL-066

## Propósito

Esta plantilla reúne las 51 evaluaciones pendientes del Paso 8D. Jhoreck realiza únicamente la inspección en el visor de Google Earth Engine (GEE), pega la salida completa de la consola y registra lo que observa. La interpretación final, la normalización de términos y la actualización del libro maestro se harán después, en una sola revisión del archivo completo.

Nombre recomendado para entregar el documento terminado:

`lote_evaluaciones_EVAL016_EVAL066_paso08D.md`

## Cómo trabajar

1. Abre el visor integrado restringido del Paso 8D y presiona `Run` una sola vez.
2. Selecciona las evaluaciones en orden estricto: EVAL-016, EVAL-017, …, EVAL-066.
3. No vuelvas a ejecutar el script al cambiar de evaluación: `Run` reinicia el desplegable en EVAL-001.
4. Antes de observar, confirma que el visor muestre el ID, unidad, estrato y años indicados en esta plantilla.
5. Alterna las capas disponibles. Algunas evaluaciones mostrarán más controles que otras.
6. Pega toda la salida pertinente de la consola entre los marcadores `[INICIO_CONSOLA_GEE]` y `[FIN_CONSOLA_GEE]`. No la resumas ni corrijas.
7. Escribe tus observaciones solo sobre la huella candidata señalada por su contorno; usa la ventana de 150 × 150 m y el contexto de 500 m para interpretar el entorno.
8. Si una capa no aparece, escribe `NO MOSTRADA`. No inventes ni dejes implícito que fue revisada.
9. No asignes todavía `ACUERDO`, `DESACUERDO`, `INDETERMINADO`, proceso observado ni confianza. Eso se decidirá después integrando todas las evidencias.
10. Guarda periódicamente el Google Doc y, al terminar, descárgalo como Markdown (`.md`). Si Google Docs no ofrece Markdown directamente, descárgalo como texto o DOCX y lo convertiremos sin alterar el contenido.

## Jerarquía de evidencia que se mantendrá

- Evidencia principal: MapBiomas Perú — clases 70 y 24, serie, transiciones, mosaicos, persistencia, conectividad y variables internas cuando correspondan.
- Control interno MapBiomas: NDVI y, para candidatos urbanos, NDBI, NUACI y tamaño del parche conectado.
- Evidencia auxiliar: Landsat Collection 2 y Sentinel-2 cuando estén disponibles. Ayudan a interpretar y asignar confianza, pero no reemplazan MapBiomas ni deciden por sí solas.
- La capa candidata o su contorno solo localiza la huella que debe examinarse; no constituye evidencia independiente.

## Reglas de redacción

- Describe patrones observables: `claro → oscuro → claro`, mayor heterogeneidad, textura más regular, borde urbano cercano, cambio localizado, etc.
- Indica si el patrón es uniforme o si varía entre píxeles.
- No traduzcas automáticamente `más claro` o `más oscuro` como pérdida, recuperación o urbanización.
- No uses causas no demostradas como ilegalidad, invasión, degradación, deforestación o minería.
- En evaluaciones KBA restringidas, no agregues coordenadas, geometrías ni enlaces de descarga.
- No abras ni consultes la clave de repeticiones ciegas antes de terminar las 66 evaluaciones.

## Detente y marca el caso como bloqueado si ocurre cualquiera de estos problemas

- El ID, la unidad, el estrato o los años del visor no coinciden con esta plantilla.
- La consola presenta un error que impide obtener las métricas principales.
- No cargan las capas principales de MapBiomas.
- La selección vuelve a EVAL-001 y no puedes recuperar el caso correcto.
- La huella candidata no puede distinguirse de la ventana de 150 × 150 m.

En esos casos, no improvises. Registra el error completo en “Incidencias y limitaciones” y continúa con el siguiente caso solo si el visor lo permite.

## Valores para registrar durante la inspección

En “Capas revisadas” usa únicamente: `SI`, `NO` o `NO MOSTRADA`.

En “Estado del caso” usa:

- `LISTO_PARA_INTEGRAR: SI` cuando la identidad fue verificada, la consola fue pegada y registraste las capas realmente observadas.
- `LISTO_PARA_INTEGRAR: NO` cuando falta información o existe un error no resuelto.

---

## EVAL-016

### A. Identidad esperada

- Dominio: `kba_restricted`
- Unidad ID: `kba|atocongo`
- Unidad: Lomas de Atocongo
- Estrato: `E6_CAMBIO_70_13`
- Años esperados — inicio | evento | fin: `2009 | 2010 | 2014`

### B. Control previo

- [ ] El desplegable muestra `EVAL-016`.
- [ ] La unidad y el estrato coinciden.
- [ ] Los años coinciden.
- [ ] Las capas principales de MapBiomas cargaron.
- [ ] El contorno candidato se distingue de la ventana 150 × 150 m.

### C. Salida completa de la consola GEE

[INICIO_CONSOLA_GEE]

PEGAR AQUÍ TODA LA SALIDA PERTINENTE DE LA CONSOLA PARA EVAL-016.

[FIN_CONSOLA_GEE]

### D. Capas revisadas

- MapBiomas — color natural: 
- MapBiomas — falso color: 
- MapBiomas — NDVI: 
- MapBiomas — NDBI: 
- MapBiomas — NUACI: 
- Landsat C2 — color natural: 
- Landsat C2 — falso color: 
- Landsat C2 — NDVI cuantitativo en consola: 
- Sentinel-2 — color natural: 
- Sentinel-2 — falso color: 
- Sentinel-2 — NDVI cuantitativo en consola: 
- Contexto 500 m: 
- Fuente visual adicional distinta del visor: 

### E. Observaciones visuales de Jhoreck

- MapBiomas — color natural:
- MapBiomas — falso color:
- MapBiomas — NDVI:
- MapBiomas — NDBI, si aparece:
- MapBiomas — NUACI, si aparece:
- Landsat C2 — color natural:
- Landsat C2 — falso color:
- Sentinel-2 — color natural, si aparece:
- Sentinel-2 — falso color, si aparece:
- Forma, textura, conectividad y contexto del candidato:
- ¿El patrón es uniforme en la huella?: 
- Observación integradora, sin asignar todavía veredicto:

### F. Incidencias y limitaciones

- Errores de consola o teselas:
- Capas no mostradas:
- Dificultad de interpretación:
- Otra observación:

### G. Estado del caso

- `LISTO_PARA_INTEGRAR: `
- Motivo si la respuesta es `NO`:

---

## EVAL-017

### A. Identidad esperada

- Dominio: `anillo_sistema`
- Unidad ID: `sistema|1000_2000`
- Unidad: Sistema disuelto 1000_2000
- Estrato: `E2_URBANO_W5`
- Años esperados — inicio | evento | fin: `2012 | 2013 | 2017`

### B. Control previo

- [ ] El desplegable muestra `EVAL-017`.
- [ ] La unidad y el estrato coinciden.
- [ ] Los años coinciden.
- [ ] Las capas principales de MapBiomas cargaron.
- [ ] El contorno candidato se distingue de la ventana 150 × 150 m.

### C. Salida completa de la consola GEE

[INICIO_CONSOLA_GEE]

PEGAR AQUÍ TODA LA SALIDA PERTINENTE DE LA CONSOLA PARA EVAL-017.

[FIN_CONSOLA_GEE]

### D. Capas revisadas

- MapBiomas — color natural: 
- MapBiomas — falso color: 
- MapBiomas — NDVI: 
- MapBiomas — NDBI: 
- MapBiomas — NUACI: 
- Landsat C2 — color natural: 
- Landsat C2 — falso color: 
- Landsat C2 — NDVI cuantitativo en consola: 
- Sentinel-2 — color natural: 
- Sentinel-2 — falso color: 
- Sentinel-2 — NDVI cuantitativo en consola: 
- Contexto 500 m: 
- Fuente visual adicional distinta del visor: 

### E. Observaciones visuales de Jhoreck

- MapBiomas — color natural:
- MapBiomas — falso color:
- MapBiomas — NDVI:
- MapBiomas — NDBI, si aparece:
- MapBiomas — NUACI, si aparece:
- Landsat C2 — color natural:
- Landsat C2 — falso color:
- Sentinel-2 — color natural, si aparece:
- Sentinel-2 — falso color, si aparece:
- Forma, textura, conectividad y contexto del candidato:
- ¿El patrón es uniforme en la huella?: 
- Observación integradora, sin asignar todavía veredicto:

### F. Incidencias y limitaciones

- Errores de consola o teselas:
- Capas no mostradas:
- Dificultad de interpretación:
- Otra observación:

### G. Estado del caso

- `LISTO_PARA_INTEGRAR: `
- Motivo si la respuesta es `NO`:

---

## EVAL-018

### A. Identidad esperada

- Dominio: `kba_restricted`
- Unidad ID: `kba|atocongo`
- Unidad: Lomas de Atocongo
- Estrato: `E2_URBANO_W5`
- Años esperados — inicio | evento | fin: `2017 | 2018 | 2022`

### B. Control previo

- [ ] El desplegable muestra `EVAL-018`.
- [ ] La unidad y el estrato coinciden.
- [ ] Los años coinciden.
- [ ] Las capas principales de MapBiomas cargaron.
- [ ] El contorno candidato se distingue de la ventana 150 × 150 m.

### C. Salida completa de la consola GEE

[INICIO_CONSOLA_GEE]

PEGAR AQUÍ TODA LA SALIDA PERTINENTE DE LA CONSOLA PARA EVAL-018.

[FIN_CONSOLA_GEE]

### D. Capas revisadas

- MapBiomas — color natural: 
- MapBiomas — falso color: 
- MapBiomas — NDVI: 
- MapBiomas — NDBI: 
- MapBiomas — NUACI: 
- Landsat C2 — color natural: 
- Landsat C2 — falso color: 
- Landsat C2 — NDVI cuantitativo en consola: 
- Sentinel-2 — color natural: 
- Sentinel-2 — falso color: 
- Sentinel-2 — NDVI cuantitativo en consola: 
- Contexto 500 m: 
- Fuente visual adicional distinta del visor: 

### E. Observaciones visuales de Jhoreck

- MapBiomas — color natural:
- MapBiomas — falso color:
- MapBiomas — NDVI:
- MapBiomas — NDBI, si aparece:
- MapBiomas — NUACI, si aparece:
- Landsat C2 — color natural:
- Landsat C2 — falso color:
- Sentinel-2 — color natural, si aparece:
- Sentinel-2 — falso color, si aparece:
- Forma, textura, conectividad y contexto del candidato:
- ¿El patrón es uniforme en la huella?: 
- Observación integradora, sin asignar todavía veredicto:

### F. Incidencias y limitaciones

- Errores de consola o teselas:
- Capas no mostradas:
- Dificultad de interpretación:
- Otra observación:

### G. Estado del caso

- `LISTO_PARA_INTEGRAR: `
- Motivo si la respuesta es `NO`:

---

## EVAL-019

### A. Identidad esperada

- Dominio: `acr`
- Unidad ID: `acr|carabayllo_2`
- Unidad: Lomas de Carabayllo 2
- Estrato: `E1_PERSISTENTE70`
- Años esperados — inicio | evento | fin: `1985 | N/A | 2024`

### B. Control previo

- [ ] El desplegable muestra `EVAL-019`.
- [ ] La unidad y el estrato coinciden.
- [ ] Los años coinciden.
- [ ] Las capas principales de MapBiomas cargaron.
- [ ] El contorno candidato se distingue de la ventana 150 × 150 m.

### C. Salida completa de la consola GEE

[INICIO_CONSOLA_GEE]

PEGAR AQUÍ TODA LA SALIDA PERTINENTE DE LA CONSOLA PARA EVAL-019.

[FIN_CONSOLA_GEE]

### D. Capas revisadas

- MapBiomas — color natural: 
- MapBiomas — falso color: 
- MapBiomas — NDVI: 
- MapBiomas — NDBI: 
- MapBiomas — NUACI: 
- Landsat C2 — color natural: 
- Landsat C2 — falso color: 
- Landsat C2 — NDVI cuantitativo en consola: 
- Sentinel-2 — color natural: 
- Sentinel-2 — falso color: 
- Sentinel-2 — NDVI cuantitativo en consola: 
- Contexto 500 m: 
- Fuente visual adicional distinta del visor: 

### E. Observaciones visuales de Jhoreck

- MapBiomas — color natural:
- MapBiomas — falso color:
- MapBiomas — NDVI:
- MapBiomas — NDBI, si aparece:
- MapBiomas — NUACI, si aparece:
- Landsat C2 — color natural:
- Landsat C2 — falso color:
- Sentinel-2 — color natural, si aparece:
- Sentinel-2 — falso color, si aparece:
- Forma, textura, conectividad y contexto del candidato:
- ¿El patrón es uniforme en la huella?: 
- Observación integradora, sin asignar todavía veredicto:

### F. Incidencias y limitaciones

- Errores de consola o teselas:
- Capas no mostradas:
- Dificultad de interpretación:
- Otra observación:

### G. Estado del caso

- `LISTO_PARA_INTEGRAR: `
- Motivo si la respuesta es `NO`:

---

## EVAL-020

### A. Identidad esperada

- Dominio: `anillo_sistema`
- Unidad ID: `sistema|1000_2000`
- Unidad: Sistema disuelto 1000_2000
- Estrato: `E1_PERSISTENTE70`
- Años esperados — inicio | evento | fin: `1985 | N/A | 2024`

### B. Control previo

- [ ] El desplegable muestra `EVAL-020`.
- [ ] La unidad y el estrato coinciden.
- [ ] Los años coinciden.
- [ ] Las capas principales de MapBiomas cargaron.
- [ ] El contorno candidato se distingue de la ventana 150 × 150 m.

### C. Salida completa de la consola GEE

[INICIO_CONSOLA_GEE]

PEGAR AQUÍ TODA LA SALIDA PERTINENTE DE LA CONSOLA PARA EVAL-020.

[FIN_CONSOLA_GEE]

### D. Capas revisadas

- MapBiomas — color natural: 
- MapBiomas — falso color: 
- MapBiomas — NDVI: 
- MapBiomas — NDBI: 
- MapBiomas — NUACI: 
- Landsat C2 — color natural: 
- Landsat C2 — falso color: 
- Landsat C2 — NDVI cuantitativo en consola: 
- Sentinel-2 — color natural: 
- Sentinel-2 — falso color: 
- Sentinel-2 — NDVI cuantitativo en consola: 
- Contexto 500 m: 
- Fuente visual adicional distinta del visor: 

### E. Observaciones visuales de Jhoreck

- MapBiomas — color natural:
- MapBiomas — falso color:
- MapBiomas — NDVI:
- MapBiomas — NDBI, si aparece:
- MapBiomas — NUACI, si aparece:
- Landsat C2 — color natural:
- Landsat C2 — falso color:
- Sentinel-2 — color natural, si aparece:
- Sentinel-2 — falso color, si aparece:
- Forma, textura, conectividad y contexto del candidato:
- ¿El patrón es uniforme en la huella?: 
- Observación integradora, sin asignar todavía veredicto:

### F. Incidencias y limitaciones

- Errores de consola o teselas:
- Capas no mostradas:
- Dificultad de interpretación:
- Otra observación:

### G. Estado del caso

- `LISTO_PARA_INTEGRAR: `
- Motivo si la respuesta es `NO`:

---

## EVAL-021

### A. Identidad esperada

- Dominio: `kba_restricted`
- Unidad ID: `kba|atocongo`
- Unidad: Lomas de Atocongo
- Estrato: `E5_RECUPERACION_68_70`
- Años esperados — inicio | evento | fin: `1996 | 1997 | 2001`

### B. Control previo

- [ ] El desplegable muestra `EVAL-021`.
- [ ] La unidad y el estrato coinciden.
- [ ] Los años coinciden.
- [ ] Las capas principales de MapBiomas cargaron.
- [ ] El contorno candidato se distingue de la ventana 150 × 150 m.

### C. Salida completa de la consola GEE

[INICIO_CONSOLA_GEE]

PEGAR AQUÍ TODA LA SALIDA PERTINENTE DE LA CONSOLA PARA EVAL-021.

[FIN_CONSOLA_GEE]

### D. Capas revisadas

- MapBiomas — color natural: 
- MapBiomas — falso color: 
- MapBiomas — NDVI: 
- MapBiomas — NDBI: 
- MapBiomas — NUACI: 
- Landsat C2 — color natural: 
- Landsat C2 — falso color: 
- Landsat C2 — NDVI cuantitativo en consola: 
- Sentinel-2 — color natural: 
- Sentinel-2 — falso color: 
- Sentinel-2 — NDVI cuantitativo en consola: 
- Contexto 500 m: 
- Fuente visual adicional distinta del visor: 

### E. Observaciones visuales de Jhoreck

- MapBiomas — color natural:
- MapBiomas — falso color:
- MapBiomas — NDVI:
- MapBiomas — NDBI, si aparece:
- MapBiomas — NUACI, si aparece:
- Landsat C2 — color natural:
- Landsat C2 — falso color:
- Sentinel-2 — color natural, si aparece:
- Sentinel-2 — falso color, si aparece:
- Forma, textura, conectividad y contexto del candidato:
- ¿El patrón es uniforme en la huella?: 
- Observación integradora, sin asignar todavía veredicto:

### F. Incidencias y limitaciones

- Errores de consola o teselas:
- Capas no mostradas:
- Dificultad de interpretación:
- Otra observación:

### G. Estado del caso

- `LISTO_PARA_INTEGRAR: `
- Motivo si la respuesta es `NO`:

---

## EVAL-022

### A. Identidad esperada

- Dominio: `kba_restricted`
- Unidad ID: `kba|atocongo`
- Unidad: Lomas de Atocongo
- Estrato: `E5_RECUPERACION_68_70`
- Años esperados — inicio | evento | fin: `1998 | 1999 | 2003`

### B. Control previo

- [ ] El desplegable muestra `EVAL-022`.
- [ ] La unidad y el estrato coinciden.
- [ ] Los años coinciden.
- [ ] Las capas principales de MapBiomas cargaron.
- [ ] El contorno candidato se distingue de la ventana 150 × 150 m.

### C. Salida completa de la consola GEE

[INICIO_CONSOLA_GEE]

PEGAR AQUÍ TODA LA SALIDA PERTINENTE DE LA CONSOLA PARA EVAL-022.

[FIN_CONSOLA_GEE]

### D. Capas revisadas

- MapBiomas — color natural: 
- MapBiomas — falso color: 
- MapBiomas — NDVI: 
- MapBiomas — NDBI: 
- MapBiomas — NUACI: 
- Landsat C2 — color natural: 
- Landsat C2 — falso color: 
- Landsat C2 — NDVI cuantitativo en consola: 
- Sentinel-2 — color natural: 
- Sentinel-2 — falso color: 
- Sentinel-2 — NDVI cuantitativo en consola: 
- Contexto 500 m: 
- Fuente visual adicional distinta del visor: 

### E. Observaciones visuales de Jhoreck

- MapBiomas — color natural:
- MapBiomas — falso color:
- MapBiomas — NDVI:
- MapBiomas — NDBI, si aparece:
- MapBiomas — NUACI, si aparece:
- Landsat C2 — color natural:
- Landsat C2 — falso color:
- Sentinel-2 — color natural, si aparece:
- Sentinel-2 — falso color, si aparece:
- Forma, textura, conectividad y contexto del candidato:
- ¿El patrón es uniforme en la huella?: 
- Observación integradora, sin asignar todavía veredicto:

### F. Incidencias y limitaciones

- Errores de consola o teselas:
- Capas no mostradas:
- Dificultad de interpretación:
- Otra observación:

### G. Estado del caso

- `LISTO_PARA_INTEGRAR: `
- Motivo si la respuesta es `NO`:

---

## EVAL-023

### A. Identidad esperada

- Dominio: `acr`
- Unidad ID: `acr|carabayllo_2`
- Unidad: Lomas de Carabayllo 2
- Estrato: `E6_CAMBIO_70_13`
- Años esperados — inicio | evento | fin: `2014 | 2015 | 2019`

### B. Control previo

- [ ] El desplegable muestra `EVAL-023`.
- [ ] La unidad y el estrato coinciden.
- [ ] Los años coinciden.
- [ ] Las capas principales de MapBiomas cargaron.
- [ ] El contorno candidato se distingue de la ventana 150 × 150 m.

### C. Salida completa de la consola GEE

[INICIO_CONSOLA_GEE]

PEGAR AQUÍ TODA LA SALIDA PERTINENTE DE LA CONSOLA PARA EVAL-023.

[FIN_CONSOLA_GEE]

### D. Capas revisadas

- MapBiomas — color natural: 
- MapBiomas — falso color: 
- MapBiomas — NDVI: 
- MapBiomas — NDBI: 
- MapBiomas — NUACI: 
- Landsat C2 — color natural: 
- Landsat C2 — falso color: 
- Landsat C2 — NDVI cuantitativo en consola: 
- Sentinel-2 — color natural: 
- Sentinel-2 — falso color: 
- Sentinel-2 — NDVI cuantitativo en consola: 
- Contexto 500 m: 
- Fuente visual adicional distinta del visor: 

### E. Observaciones visuales de Jhoreck

- MapBiomas — color natural:
- MapBiomas — falso color:
- MapBiomas — NDVI:
- MapBiomas — NDBI, si aparece:
- MapBiomas — NUACI, si aparece:
- Landsat C2 — color natural:
- Landsat C2 — falso color:
- Sentinel-2 — color natural, si aparece:
- Sentinel-2 — falso color, si aparece:
- Forma, textura, conectividad y contexto del candidato:
- ¿El patrón es uniforme en la huella?: 
- Observación integradora, sin asignar todavía veredicto:

### F. Incidencias y limitaciones

- Errores de consola o teselas:
- Capas no mostradas:
- Dificultad de interpretación:
- Otra observación:

### G. Estado del caso

- `LISTO_PARA_INTEGRAR: `
- Motivo si la respuesta es `NO`:

---

## EVAL-024

### A. Identidad esperada

- Dominio: `acr`
- Unidad ID: `acr|carabayllo_2`
- Unidad: Lomas de Carabayllo 2
- Estrato: `E6_CAMBIO_70_13`
- Años esperados — inicio | evento | fin: `2009 | 2010 | 2014`

### B. Control previo

- [ ] El desplegable muestra `EVAL-024`.
- [ ] La unidad y el estrato coinciden.
- [ ] Los años coinciden.
- [ ] Las capas principales de MapBiomas cargaron.
- [ ] El contorno candidato se distingue de la ventana 150 × 150 m.

### C. Salida completa de la consola GEE

[INICIO_CONSOLA_GEE]

PEGAR AQUÍ TODA LA SALIDA PERTINENTE DE LA CONSOLA PARA EVAL-024.

[FIN_CONSOLA_GEE]

### D. Capas revisadas

- MapBiomas — color natural: 
- MapBiomas — falso color: 
- MapBiomas — NDVI: 
- MapBiomas — NDBI: 
- MapBiomas — NUACI: 
- Landsat C2 — color natural: 
- Landsat C2 — falso color: 
- Landsat C2 — NDVI cuantitativo en consola: 
- Sentinel-2 — color natural: 
- Sentinel-2 — falso color: 
- Sentinel-2 — NDVI cuantitativo en consola: 
- Contexto 500 m: 
- Fuente visual adicional distinta del visor: 

### E. Observaciones visuales de Jhoreck

- MapBiomas — color natural:
- MapBiomas — falso color:
- MapBiomas — NDVI:
- MapBiomas — NDBI, si aparece:
- MapBiomas — NUACI, si aparece:
- Landsat C2 — color natural:
- Landsat C2 — falso color:
- Sentinel-2 — color natural, si aparece:
- Sentinel-2 — falso color, si aparece:
- Forma, textura, conectividad y contexto del candidato:
- ¿El patrón es uniforme en la huella?: 
- Observación integradora, sin asignar todavía veredicto:

### F. Incidencias y limitaciones

- Errores de consola o teselas:
- Capas no mostradas:
- Dificultad de interpretación:
- Otra observación:

### G. Estado del caso

- `LISTO_PARA_INTEGRAR: `
- Motivo si la respuesta es `NO`:

---

## EVAL-025

### A. Identidad esperada

- Dominio: `anillo_sistema`
- Unidad ID: `sistema|500_1000`
- Unidad: Sistema disuelto 500_1000
- Estrato: `E4_INTERCAMBIO_68_70`
- Años esperados — inicio | evento | fin: `2003 | 2004 | 2008`

### B. Control previo

- [ ] El desplegable muestra `EVAL-025`.
- [ ] La unidad y el estrato coinciden.
- [ ] Los años coinciden.
- [ ] Las capas principales de MapBiomas cargaron.
- [ ] El contorno candidato se distingue de la ventana 150 × 150 m.

### C. Salida completa de la consola GEE

[INICIO_CONSOLA_GEE]

PEGAR AQUÍ TODA LA SALIDA PERTINENTE DE LA CONSOLA PARA EVAL-025.

[FIN_CONSOLA_GEE]

### D. Capas revisadas

- MapBiomas — color natural: 
- MapBiomas — falso color: 
- MapBiomas — NDVI: 
- MapBiomas — NDBI: 
- MapBiomas — NUACI: 
- Landsat C2 — color natural: 
- Landsat C2 — falso color: 
- Landsat C2 — NDVI cuantitativo en consola: 
- Sentinel-2 — color natural: 
- Sentinel-2 — falso color: 
- Sentinel-2 — NDVI cuantitativo en consola: 
- Contexto 500 m: 
- Fuente visual adicional distinta del visor: 

### E. Observaciones visuales de Jhoreck

- MapBiomas — color natural:
- MapBiomas — falso color:
- MapBiomas — NDVI:
- MapBiomas — NDBI, si aparece:
- MapBiomas — NUACI, si aparece:
- Landsat C2 — color natural:
- Landsat C2 — falso color:
- Sentinel-2 — color natural, si aparece:
- Sentinel-2 — falso color, si aparece:
- Forma, textura, conectividad y contexto del candidato:
- ¿El patrón es uniforme en la huella?: 
- Observación integradora, sin asignar todavía veredicto:

### F. Incidencias y limitaciones

- Errores de consola o teselas:
- Capas no mostradas:
- Dificultad de interpretación:
- Otra observación:

### G. Estado del caso

- `LISTO_PARA_INTEGRAR: `
- Motivo si la respuesta es `NO`:

---

## EVAL-026

### A. Identidad esperada

- Dominio: `kba_restricted`
- Unidad ID: `kba|atocongo`
- Unidad: Lomas de Atocongo
- Estrato: `E1_PERSISTENTE70`
- Años esperados — inicio | evento | fin: `1985 | N/A | 2024`

### B. Control previo

- [ ] El desplegable muestra `EVAL-026`.
- [ ] La unidad y el estrato coinciden.
- [ ] Los años coinciden.
- [ ] Las capas principales de MapBiomas cargaron.
- [ ] El contorno candidato se distingue de la ventana 150 × 150 m.

### C. Salida completa de la consola GEE

[INICIO_CONSOLA_GEE]

PEGAR AQUÍ TODA LA SALIDA PERTINENTE DE LA CONSOLA PARA EVAL-026.

[FIN_CONSOLA_GEE]

### D. Capas revisadas

- MapBiomas — color natural: 
- MapBiomas — falso color: 
- MapBiomas — NDVI: 
- MapBiomas — NDBI: 
- MapBiomas — NUACI: 
- Landsat C2 — color natural: 
- Landsat C2 — falso color: 
- Landsat C2 — NDVI cuantitativo en consola: 
- Sentinel-2 — color natural: 
- Sentinel-2 — falso color: 
- Sentinel-2 — NDVI cuantitativo en consola: 
- Contexto 500 m: 
- Fuente visual adicional distinta del visor: 

### E. Observaciones visuales de Jhoreck

- MapBiomas — color natural:
- MapBiomas — falso color:
- MapBiomas — NDVI:
- MapBiomas — NDBI, si aparece:
- MapBiomas — NUACI, si aparece:
- Landsat C2 — color natural:
- Landsat C2 — falso color:
- Sentinel-2 — color natural, si aparece:
- Sentinel-2 — falso color, si aparece:
- Forma, textura, conectividad y contexto del candidato:
- ¿El patrón es uniforme en la huella?: 
- Observación integradora, sin asignar todavía veredicto:

### F. Incidencias y limitaciones

- Errores de consola o teselas:
- Capas no mostradas:
- Dificultad de interpretación:
- Otra observación:

### G. Estado del caso

- `LISTO_PARA_INTEGRAR: `
- Motivo si la respuesta es `NO`:

---

## EVAL-027

### A. Identidad esperada

- Dominio: `kba_restricted`
- Unidad ID: `kba|atocongo`
- Unidad: Lomas de Atocongo
- Estrato: `E5_RECUPERACION_68_70`
- Años esperados — inicio | evento | fin: `2001 | 2002 | 2006`

### B. Control previo

- [ ] El desplegable muestra `EVAL-027`.
- [ ] La unidad y el estrato coinciden.
- [ ] Los años coinciden.
- [ ] Las capas principales de MapBiomas cargaron.
- [ ] El contorno candidato se distingue de la ventana 150 × 150 m.

### C. Salida completa de la consola GEE

[INICIO_CONSOLA_GEE]

PEGAR AQUÍ TODA LA SALIDA PERTINENTE DE LA CONSOLA PARA EVAL-027.

[FIN_CONSOLA_GEE]

### D. Capas revisadas

- MapBiomas — color natural: 
- MapBiomas — falso color: 
- MapBiomas — NDVI: 
- MapBiomas — NDBI: 
- MapBiomas — NUACI: 
- Landsat C2 — color natural: 
- Landsat C2 — falso color: 
- Landsat C2 — NDVI cuantitativo en consola: 
- Sentinel-2 — color natural: 
- Sentinel-2 — falso color: 
- Sentinel-2 — NDVI cuantitativo en consola: 
- Contexto 500 m: 
- Fuente visual adicional distinta del visor: 

### E. Observaciones visuales de Jhoreck

- MapBiomas — color natural:
- MapBiomas — falso color:
- MapBiomas — NDVI:
- MapBiomas — NDBI, si aparece:
- MapBiomas — NUACI, si aparece:
- Landsat C2 — color natural:
- Landsat C2 — falso color:
- Sentinel-2 — color natural, si aparece:
- Sentinel-2 — falso color, si aparece:
- Forma, textura, conectividad y contexto del candidato:
- ¿El patrón es uniforme en la huella?: 
- Observación integradora, sin asignar todavía veredicto:

### F. Incidencias y limitaciones

- Errores de consola o teselas:
- Capas no mostradas:
- Dificultad de interpretación:
- Otra observación:

### G. Estado del caso

- `LISTO_PARA_INTEGRAR: `
- Motivo si la respuesta es `NO`:

---

## EVAL-028

### A. Identidad esperada

- Dominio: `acr`
- Unidad ID: `acr|amancaes`
- Unidad: Lomas de Amancaes
- Estrato: `E3_URBANO_CENSURADO`
- Años esperados — inicio | evento | fin: `2023 | 2024 | 2024`

### B. Control previo

- [ ] El desplegable muestra `EVAL-028`.
- [ ] La unidad y el estrato coinciden.
- [ ] Los años coinciden.
- [ ] Las capas principales de MapBiomas cargaron.
- [ ] El contorno candidato se distingue de la ventana 150 × 150 m.

### C. Salida completa de la consola GEE

[INICIO_CONSOLA_GEE]

PEGAR AQUÍ TODA LA SALIDA PERTINENTE DE LA CONSOLA PARA EVAL-028.

[FIN_CONSOLA_GEE]

### D. Capas revisadas

- MapBiomas — color natural: 
- MapBiomas — falso color: 
- MapBiomas — NDVI: 
- MapBiomas — NDBI: 
- MapBiomas — NUACI: 
- Landsat C2 — color natural: 
- Landsat C2 — falso color: 
- Landsat C2 — NDVI cuantitativo en consola: 
- Sentinel-2 — color natural: 
- Sentinel-2 — falso color: 
- Sentinel-2 — NDVI cuantitativo en consola: 
- Contexto 500 m: 
- Fuente visual adicional distinta del visor: 

### E. Observaciones visuales de Jhoreck

- MapBiomas — color natural:
- MapBiomas — falso color:
- MapBiomas — NDVI:
- MapBiomas — NDBI, si aparece:
- MapBiomas — NUACI, si aparece:
- Landsat C2 — color natural:
- Landsat C2 — falso color:
- Sentinel-2 — color natural, si aparece:
- Sentinel-2 — falso color, si aparece:
- Forma, textura, conectividad y contexto del candidato:
- ¿El patrón es uniforme en la huella?: 
- Observación integradora, sin asignar todavía veredicto:

### F. Incidencias y limitaciones

- Errores de consola o teselas:
- Capas no mostradas:
- Dificultad de interpretación:
- Otra observación:

### G. Estado del caso

- `LISTO_PARA_INTEGRAR: `
- Motivo si la respuesta es `NO`:

---

## EVAL-029

### A. Identidad esperada

- Dominio: `kba_restricted`
- Unidad ID: `kba|atocongo`
- Unidad: Lomas de Atocongo
- Estrato: `E1_PERSISTENTE70`
- Años esperados — inicio | evento | fin: `1985 | N/A | 2024`

### B. Control previo

- [ ] El desplegable muestra `EVAL-029`.
- [ ] La unidad y el estrato coinciden.
- [ ] Los años coinciden.
- [ ] Las capas principales de MapBiomas cargaron.
- [ ] El contorno candidato se distingue de la ventana 150 × 150 m.

### C. Salida completa de la consola GEE

[INICIO_CONSOLA_GEE]

PEGAR AQUÍ TODA LA SALIDA PERTINENTE DE LA CONSOLA PARA EVAL-029.

[FIN_CONSOLA_GEE]

### D. Capas revisadas

- MapBiomas — color natural: 
- MapBiomas — falso color: 
- MapBiomas — NDVI: 
- MapBiomas — NDBI: 
- MapBiomas — NUACI: 
- Landsat C2 — color natural: 
- Landsat C2 — falso color: 
- Landsat C2 — NDVI cuantitativo en consola: 
- Sentinel-2 — color natural: 
- Sentinel-2 — falso color: 
- Sentinel-2 — NDVI cuantitativo en consola: 
- Contexto 500 m: 
- Fuente visual adicional distinta del visor: 

### E. Observaciones visuales de Jhoreck

- MapBiomas — color natural:
- MapBiomas — falso color:
- MapBiomas — NDVI:
- MapBiomas — NDBI, si aparece:
- MapBiomas — NUACI, si aparece:
- Landsat C2 — color natural:
- Landsat C2 — falso color:
- Sentinel-2 — color natural, si aparece:
- Sentinel-2 — falso color, si aparece:
- Forma, textura, conectividad y contexto del candidato:
- ¿El patrón es uniforme en la huella?: 
- Observación integradora, sin asignar todavía veredicto:

### F. Incidencias y limitaciones

- Errores de consola o teselas:
- Capas no mostradas:
- Dificultad de interpretación:
- Otra observación:

### G. Estado del caso

- `LISTO_PARA_INTEGRAR: `
- Motivo si la respuesta es `NO`:

---

## EVAL-030

### A. Identidad esperada

- Dominio: `anillo_sistema`
- Unidad ID: `sistema|1000_2000`
- Unidad: Sistema disuelto 1000_2000
- Estrato: `E1_PERSISTENTE70`
- Años esperados — inicio | evento | fin: `1985 | N/A | 2024`

### B. Control previo

- [ ] El desplegable muestra `EVAL-030`.
- [ ] La unidad y el estrato coinciden.
- [ ] Los años coinciden.
- [ ] Las capas principales de MapBiomas cargaron.
- [ ] El contorno candidato se distingue de la ventana 150 × 150 m.

### C. Salida completa de la consola GEE

[INICIO_CONSOLA_GEE]

PEGAR AQUÍ TODA LA SALIDA PERTINENTE DE LA CONSOLA PARA EVAL-030.

[FIN_CONSOLA_GEE]

### D. Capas revisadas

- MapBiomas — color natural: 
- MapBiomas — falso color: 
- MapBiomas — NDVI: 
- MapBiomas — NDBI: 
- MapBiomas — NUACI: 
- Landsat C2 — color natural: 
- Landsat C2 — falso color: 
- Landsat C2 — NDVI cuantitativo en consola: 
- Sentinel-2 — color natural: 
- Sentinel-2 — falso color: 
- Sentinel-2 — NDVI cuantitativo en consola: 
- Contexto 500 m: 
- Fuente visual adicional distinta del visor: 

### E. Observaciones visuales de Jhoreck

- MapBiomas — color natural:
- MapBiomas — falso color:
- MapBiomas — NDVI:
- MapBiomas — NDBI, si aparece:
- MapBiomas — NUACI, si aparece:
- Landsat C2 — color natural:
- Landsat C2 — falso color:
- Sentinel-2 — color natural, si aparece:
- Sentinel-2 — falso color, si aparece:
- Forma, textura, conectividad y contexto del candidato:
- ¿El patrón es uniforme en la huella?: 
- Observación integradora, sin asignar todavía veredicto:

### F. Incidencias y limitaciones

- Errores de consola o teselas:
- Capas no mostradas:
- Dificultad de interpretación:
- Otra observación:

### G. Estado del caso

- `LISTO_PARA_INTEGRAR: `
- Motivo si la respuesta es `NO`:

---

## EVAL-031

### A. Identidad esperada

- Dominio: `acr`
- Unidad ID: `acr|villa_maria`
- Unidad: Lomas de Villa María
- Estrato: `E4_INTERCAMBIO_68_70`
- Años esperados — inicio | evento | fin: `2014 | 2015 | 2019`

### B. Control previo

- [ ] El desplegable muestra `EVAL-031`.
- [ ] La unidad y el estrato coinciden.
- [ ] Los años coinciden.
- [ ] Las capas principales de MapBiomas cargaron.
- [ ] El contorno candidato se distingue de la ventana 150 × 150 m.

### C. Salida completa de la consola GEE

[INICIO_CONSOLA_GEE]

PEGAR AQUÍ TODA LA SALIDA PERTINENTE DE LA CONSOLA PARA EVAL-031.

[FIN_CONSOLA_GEE]

### D. Capas revisadas

- MapBiomas — color natural: 
- MapBiomas — falso color: 
- MapBiomas — NDVI: 
- MapBiomas — NDBI: 
- MapBiomas — NUACI: 
- Landsat C2 — color natural: 
- Landsat C2 — falso color: 
- Landsat C2 — NDVI cuantitativo en consola: 
- Sentinel-2 — color natural: 
- Sentinel-2 — falso color: 
- Sentinel-2 — NDVI cuantitativo en consola: 
- Contexto 500 m: 
- Fuente visual adicional distinta del visor: 

### E. Observaciones visuales de Jhoreck

- MapBiomas — color natural:
- MapBiomas — falso color:
- MapBiomas — NDVI:
- MapBiomas — NDBI, si aparece:
- MapBiomas — NUACI, si aparece:
- Landsat C2 — color natural:
- Landsat C2 — falso color:
- Sentinel-2 — color natural, si aparece:
- Sentinel-2 — falso color, si aparece:
- Forma, textura, conectividad y contexto del candidato:
- ¿El patrón es uniforme en la huella?: 
- Observación integradora, sin asignar todavía veredicto:

### F. Incidencias y limitaciones

- Errores de consola o teselas:
- Capas no mostradas:
- Dificultad de interpretación:
- Otra observación:

### G. Estado del caso

- `LISTO_PARA_INTEGRAR: `
- Motivo si la respuesta es `NO`:

---

## EVAL-032

### A. Identidad esperada

- Dominio: `kba_restricted`
- Unidad ID: `kba|atocongo`
- Unidad: Lomas de Atocongo
- Estrato: `E2_URBANO_W5`
- Años esperados — inicio | evento | fin: `2013 | 2014 | 2018`

### B. Control previo

- [ ] El desplegable muestra `EVAL-032`.
- [ ] La unidad y el estrato coinciden.
- [ ] Los años coinciden.
- [ ] Las capas principales de MapBiomas cargaron.
- [ ] El contorno candidato se distingue de la ventana 150 × 150 m.

### C. Salida completa de la consola GEE

[INICIO_CONSOLA_GEE]

PEGAR AQUÍ TODA LA SALIDA PERTINENTE DE LA CONSOLA PARA EVAL-032.

[FIN_CONSOLA_GEE]

### D. Capas revisadas

- MapBiomas — color natural: 
- MapBiomas — falso color: 
- MapBiomas — NDVI: 
- MapBiomas — NDBI: 
- MapBiomas — NUACI: 
- Landsat C2 — color natural: 
- Landsat C2 — falso color: 
- Landsat C2 — NDVI cuantitativo en consola: 
- Sentinel-2 — color natural: 
- Sentinel-2 — falso color: 
- Sentinel-2 — NDVI cuantitativo en consola: 
- Contexto 500 m: 
- Fuente visual adicional distinta del visor: 

### E. Observaciones visuales de Jhoreck

- MapBiomas — color natural:
- MapBiomas — falso color:
- MapBiomas — NDVI:
- MapBiomas — NDBI, si aparece:
- MapBiomas — NUACI, si aparece:
- Landsat C2 — color natural:
- Landsat C2 — falso color:
- Sentinel-2 — color natural, si aparece:
- Sentinel-2 — falso color, si aparece:
- Forma, textura, conectividad y contexto del candidato:
- ¿El patrón es uniforme en la huella?: 
- Observación integradora, sin asignar todavía veredicto:

### F. Incidencias y limitaciones

- Errores de consola o teselas:
- Capas no mostradas:
- Dificultad de interpretación:
- Otra observación:

### G. Estado del caso

- `LISTO_PARA_INTEGRAR: `
- Motivo si la respuesta es `NO`:

---

## EVAL-033

### A. Identidad esperada

- Dominio: `anillo_sistema`
- Unidad ID: `sistema|0_500`
- Unidad: Sistema disuelto 0_500
- Estrato: `E2_URBANO_W5`
- Años esperados — inicio | evento | fin: `2017 | 2018 | 2022`

### B. Control previo

- [ ] El desplegable muestra `EVAL-033`.
- [ ] La unidad y el estrato coinciden.
- [ ] Los años coinciden.
- [ ] Las capas principales de MapBiomas cargaron.
- [ ] El contorno candidato se distingue de la ventana 150 × 150 m.

### C. Salida completa de la consola GEE

[INICIO_CONSOLA_GEE]

PEGAR AQUÍ TODA LA SALIDA PERTINENTE DE LA CONSOLA PARA EVAL-033.

[FIN_CONSOLA_GEE]

### D. Capas revisadas

- MapBiomas — color natural: 
- MapBiomas — falso color: 
- MapBiomas — NDVI: 
- MapBiomas — NDBI: 
- MapBiomas — NUACI: 
- Landsat C2 — color natural: 
- Landsat C2 — falso color: 
- Landsat C2 — NDVI cuantitativo en consola: 
- Sentinel-2 — color natural: 
- Sentinel-2 — falso color: 
- Sentinel-2 — NDVI cuantitativo en consola: 
- Contexto 500 m: 
- Fuente visual adicional distinta del visor: 

### E. Observaciones visuales de Jhoreck

- MapBiomas — color natural:
- MapBiomas — falso color:
- MapBiomas — NDVI:
- MapBiomas — NDBI, si aparece:
- MapBiomas — NUACI, si aparece:
- Landsat C2 — color natural:
- Landsat C2 — falso color:
- Sentinel-2 — color natural, si aparece:
- Sentinel-2 — falso color, si aparece:
- Forma, textura, conectividad y contexto del candidato:
- ¿El patrón es uniforme en la huella?: 
- Observación integradora, sin asignar todavía veredicto:

### F. Incidencias y limitaciones

- Errores de consola o teselas:
- Capas no mostradas:
- Dificultad de interpretación:
- Otra observación:

### G. Estado del caso

- `LISTO_PARA_INTEGRAR: `
- Motivo si la respuesta es `NO`:

---

## EVAL-034

### A. Identidad esperada

- Dominio: `kba_restricted`
- Unidad ID: `kba|atocongo`
- Unidad: Lomas de Atocongo
- Estrato: `E4_INTERCAMBIO_68_70`
- Años esperados — inicio | evento | fin: `2004 | 2005 | 2009`

### B. Control previo

- [ ] El desplegable muestra `EVAL-034`.
- [ ] La unidad y el estrato coinciden.
- [ ] Los años coinciden.
- [ ] Las capas principales de MapBiomas cargaron.
- [ ] El contorno candidato se distingue de la ventana 150 × 150 m.

### C. Salida completa de la consola GEE

[INICIO_CONSOLA_GEE]

PEGAR AQUÍ TODA LA SALIDA PERTINENTE DE LA CONSOLA PARA EVAL-034.

[FIN_CONSOLA_GEE]

### D. Capas revisadas

- MapBiomas — color natural: 
- MapBiomas — falso color: 
- MapBiomas — NDVI: 
- MapBiomas — NDBI: 
- MapBiomas — NUACI: 
- Landsat C2 — color natural: 
- Landsat C2 — falso color: 
- Landsat C2 — NDVI cuantitativo en consola: 
- Sentinel-2 — color natural: 
- Sentinel-2 — falso color: 
- Sentinel-2 — NDVI cuantitativo en consola: 
- Contexto 500 m: 
- Fuente visual adicional distinta del visor: 

### E. Observaciones visuales de Jhoreck

- MapBiomas — color natural:
- MapBiomas — falso color:
- MapBiomas — NDVI:
- MapBiomas — NDBI, si aparece:
- MapBiomas — NUACI, si aparece:
- Landsat C2 — color natural:
- Landsat C2 — falso color:
- Sentinel-2 — color natural, si aparece:
- Sentinel-2 — falso color, si aparece:
- Forma, textura, conectividad y contexto del candidato:
- ¿El patrón es uniforme en la huella?: 
- Observación integradora, sin asignar todavía veredicto:

### F. Incidencias y limitaciones

- Errores de consola o teselas:
- Capas no mostradas:
- Dificultad de interpretación:
- Otra observación:

### G. Estado del caso

- `LISTO_PARA_INTEGRAR: `
- Motivo si la respuesta es `NO`:

---

## EVAL-035

### A. Identidad esperada

- Dominio: `kba_restricted`
- Unidad ID: `kba|atocongo`
- Unidad: Lomas de Atocongo
- Estrato: `E4_INTERCAMBIO_68_70`
- Años esperados — inicio | evento | fin: `2004 | 2005 | 2009`

### B. Control previo

- [ ] El desplegable muestra `EVAL-035`.
- [ ] La unidad y el estrato coinciden.
- [ ] Los años coinciden.
- [ ] Las capas principales de MapBiomas cargaron.
- [ ] El contorno candidato se distingue de la ventana 150 × 150 m.

### C. Salida completa de la consola GEE

[INICIO_CONSOLA_GEE]

PEGAR AQUÍ TODA LA SALIDA PERTINENTE DE LA CONSOLA PARA EVAL-035.

[FIN_CONSOLA_GEE]

### D. Capas revisadas

- MapBiomas — color natural: 
- MapBiomas — falso color: 
- MapBiomas — NDVI: 
- MapBiomas — NDBI: 
- MapBiomas — NUACI: 
- Landsat C2 — color natural: 
- Landsat C2 — falso color: 
- Landsat C2 — NDVI cuantitativo en consola: 
- Sentinel-2 — color natural: 
- Sentinel-2 — falso color: 
- Sentinel-2 — NDVI cuantitativo en consola: 
- Contexto 500 m: 
- Fuente visual adicional distinta del visor: 

### E. Observaciones visuales de Jhoreck

- MapBiomas — color natural:
- MapBiomas — falso color:
- MapBiomas — NDVI:
- MapBiomas — NDBI, si aparece:
- MapBiomas — NUACI, si aparece:
- Landsat C2 — color natural:
- Landsat C2 — falso color:
- Sentinel-2 — color natural, si aparece:
- Sentinel-2 — falso color, si aparece:
- Forma, textura, conectividad y contexto del candidato:
- ¿El patrón es uniforme en la huella?: 
- Observación integradora, sin asignar todavía veredicto:

### F. Incidencias y limitaciones

- Errores de consola o teselas:
- Capas no mostradas:
- Dificultad de interpretación:
- Otra observación:

### G. Estado del caso

- `LISTO_PARA_INTEGRAR: `
- Motivo si la respuesta es `NO`:

---

## EVAL-036

### A. Identidad esperada

- Dominio: `acr`
- Unidad ID: `acr|ancon`
- Unidad: Lomas de Ancón
- Estrato: `E5_RECUPERACION_68_70`
- Años esperados — inicio | evento | fin: `2001 | 2002 | 2006`

### B. Control previo

- [ ] El desplegable muestra `EVAL-036`.
- [ ] La unidad y el estrato coinciden.
- [ ] Los años coinciden.
- [ ] Las capas principales de MapBiomas cargaron.
- [ ] El contorno candidato se distingue de la ventana 150 × 150 m.

### C. Salida completa de la consola GEE

[INICIO_CONSOLA_GEE]

PEGAR AQUÍ TODA LA SALIDA PERTINENTE DE LA CONSOLA PARA EVAL-036.

[FIN_CONSOLA_GEE]

### D. Capas revisadas

- MapBiomas — color natural: 
- MapBiomas — falso color: 
- MapBiomas — NDVI: 
- MapBiomas — NDBI: 
- MapBiomas — NUACI: 
- Landsat C2 — color natural: 
- Landsat C2 — falso color: 
- Landsat C2 — NDVI cuantitativo en consola: 
- Sentinel-2 — color natural: 
- Sentinel-2 — falso color: 
- Sentinel-2 — NDVI cuantitativo en consola: 
- Contexto 500 m: 
- Fuente visual adicional distinta del visor: 

### E. Observaciones visuales de Jhoreck

- MapBiomas — color natural:
- MapBiomas — falso color:
- MapBiomas — NDVI:
- MapBiomas — NDBI, si aparece:
- MapBiomas — NUACI, si aparece:
- Landsat C2 — color natural:
- Landsat C2 — falso color:
- Sentinel-2 — color natural, si aparece:
- Sentinel-2 — falso color, si aparece:
- Forma, textura, conectividad y contexto del candidato:
- ¿El patrón es uniforme en la huella?: 
- Observación integradora, sin asignar todavía veredicto:

### F. Incidencias y limitaciones

- Errores de consola o teselas:
- Capas no mostradas:
- Dificultad de interpretación:
- Otra observación:

### G. Estado del caso

- `LISTO_PARA_INTEGRAR: `
- Motivo si la respuesta es `NO`:

---

## EVAL-037

### A. Identidad esperada

- Dominio: `anillo_sistema`
- Unidad ID: `sistema|1000_2000`
- Unidad: Sistema disuelto 1000_2000
- Estrato: `E3_URBANO_CENSURADO`
- Años esperados — inicio | evento | fin: `2022 | 2023 | 2024`

### B. Control previo

- [ ] El desplegable muestra `EVAL-037`.
- [ ] La unidad y el estrato coinciden.
- [ ] Los años coinciden.
- [ ] Las capas principales de MapBiomas cargaron.
- [ ] El contorno candidato se distingue de la ventana 150 × 150 m.

### C. Salida completa de la consola GEE

[INICIO_CONSOLA_GEE]

PEGAR AQUÍ TODA LA SALIDA PERTINENTE DE LA CONSOLA PARA EVAL-037.

[FIN_CONSOLA_GEE]

### D. Capas revisadas

- MapBiomas — color natural: 
- MapBiomas — falso color: 
- MapBiomas — NDVI: 
- MapBiomas — NDBI: 
- MapBiomas — NUACI: 
- Landsat C2 — color natural: 
- Landsat C2 — falso color: 
- Landsat C2 — NDVI cuantitativo en consola: 
- Sentinel-2 — color natural: 
- Sentinel-2 — falso color: 
- Sentinel-2 — NDVI cuantitativo en consola: 
- Contexto 500 m: 
- Fuente visual adicional distinta del visor: 

### E. Observaciones visuales de Jhoreck

- MapBiomas — color natural:
- MapBiomas — falso color:
- MapBiomas — NDVI:
- MapBiomas — NDBI, si aparece:
- MapBiomas — NUACI, si aparece:
- Landsat C2 — color natural:
- Landsat C2 — falso color:
- Sentinel-2 — color natural, si aparece:
- Sentinel-2 — falso color, si aparece:
- Forma, textura, conectividad y contexto del candidato:
- ¿El patrón es uniforme en la huella?: 
- Observación integradora, sin asignar todavía veredicto:

### F. Incidencias y limitaciones

- Errores de consola o teselas:
- Capas no mostradas:
- Dificultad de interpretación:
- Otra observación:

### G. Estado del caso

- `LISTO_PARA_INTEGRAR: `
- Motivo si la respuesta es `NO`:

---

## EVAL-038

### A. Identidad esperada

- Dominio: `kba_restricted`
- Unidad ID: `kba|atocongo`
- Unidad: Lomas de Atocongo
- Estrato: `E3_URBANO_CENSURADO`
- Años esperados — inicio | evento | fin: `2023 | 2024 | 2024`

### B. Control previo

- [ ] El desplegable muestra `EVAL-038`.
- [ ] La unidad y el estrato coinciden.
- [ ] Los años coinciden.
- [ ] Las capas principales de MapBiomas cargaron.
- [ ] El contorno candidato se distingue de la ventana 150 × 150 m.

### C. Salida completa de la consola GEE

[INICIO_CONSOLA_GEE]

PEGAR AQUÍ TODA LA SALIDA PERTINENTE DE LA CONSOLA PARA EVAL-038.

[FIN_CONSOLA_GEE]

### D. Capas revisadas

- MapBiomas — color natural: 
- MapBiomas — falso color: 
- MapBiomas — NDVI: 
- MapBiomas — NDBI: 
- MapBiomas — NUACI: 
- Landsat C2 — color natural: 
- Landsat C2 — falso color: 
- Landsat C2 — NDVI cuantitativo en consola: 
- Sentinel-2 — color natural: 
- Sentinel-2 — falso color: 
- Sentinel-2 — NDVI cuantitativo en consola: 
- Contexto 500 m: 
- Fuente visual adicional distinta del visor: 

### E. Observaciones visuales de Jhoreck

- MapBiomas — color natural:
- MapBiomas — falso color:
- MapBiomas — NDVI:
- MapBiomas — NDBI, si aparece:
- MapBiomas — NUACI, si aparece:
- Landsat C2 — color natural:
- Landsat C2 — falso color:
- Sentinel-2 — color natural, si aparece:
- Sentinel-2 — falso color, si aparece:
- Forma, textura, conectividad y contexto del candidato:
- ¿El patrón es uniforme en la huella?: 
- Observación integradora, sin asignar todavía veredicto:

### F. Incidencias y limitaciones

- Errores de consola o teselas:
- Capas no mostradas:
- Dificultad de interpretación:
- Otra observación:

### G. Estado del caso

- `LISTO_PARA_INTEGRAR: `
- Motivo si la respuesta es `NO`:

---

## EVAL-039

### A. Identidad esperada

- Dominio: `acr`
- Unidad ID: `acr|villa_maria`
- Unidad: Lomas de Villa María
- Estrato: `E3_URBANO_CENSURADO`
- Años esperados — inicio | evento | fin: `2021 | 2022 | 2024`

### B. Control previo

- [ ] El desplegable muestra `EVAL-039`.
- [ ] La unidad y el estrato coinciden.
- [ ] Los años coinciden.
- [ ] Las capas principales de MapBiomas cargaron.
- [ ] El contorno candidato se distingue de la ventana 150 × 150 m.

### C. Salida completa de la consola GEE

[INICIO_CONSOLA_GEE]

PEGAR AQUÍ TODA LA SALIDA PERTINENTE DE LA CONSOLA PARA EVAL-039.

[FIN_CONSOLA_GEE]

### D. Capas revisadas

- MapBiomas — color natural: 
- MapBiomas — falso color: 
- MapBiomas — NDVI: 
- MapBiomas — NDBI: 
- MapBiomas — NUACI: 
- Landsat C2 — color natural: 
- Landsat C2 — falso color: 
- Landsat C2 — NDVI cuantitativo en consola: 
- Sentinel-2 — color natural: 
- Sentinel-2 — falso color: 
- Sentinel-2 — NDVI cuantitativo en consola: 
- Contexto 500 m: 
- Fuente visual adicional distinta del visor: 

### E. Observaciones visuales de Jhoreck

- MapBiomas — color natural:
- MapBiomas — falso color:
- MapBiomas — NDVI:
- MapBiomas — NDBI, si aparece:
- MapBiomas — NUACI, si aparece:
- Landsat C2 — color natural:
- Landsat C2 — falso color:
- Sentinel-2 — color natural, si aparece:
- Sentinel-2 — falso color, si aparece:
- Forma, textura, conectividad y contexto del candidato:
- ¿El patrón es uniforme en la huella?: 
- Observación integradora, sin asignar todavía veredicto:

### F. Incidencias y limitaciones

- Errores de consola o teselas:
- Capas no mostradas:
- Dificultad de interpretación:
- Otra observación:

### G. Estado del caso

- `LISTO_PARA_INTEGRAR: `
- Motivo si la respuesta es `NO`:

---

## EVAL-040

### A. Identidad esperada

- Dominio: `kba_restricted`
- Unidad ID: `kba|atocongo`
- Unidad: Lomas de Atocongo
- Estrato: `E6_CAMBIO_70_13`
- Años esperados — inicio | evento | fin: `2009 | 2010 | 2014`

### B. Control previo

- [ ] El desplegable muestra `EVAL-040`.
- [ ] La unidad y el estrato coinciden.
- [ ] Los años coinciden.
- [ ] Las capas principales de MapBiomas cargaron.
- [ ] El contorno candidato se distingue de la ventana 150 × 150 m.

### C. Salida completa de la consola GEE

[INICIO_CONSOLA_GEE]

PEGAR AQUÍ TODA LA SALIDA PERTINENTE DE LA CONSOLA PARA EVAL-040.

[FIN_CONSOLA_GEE]

### D. Capas revisadas

- MapBiomas — color natural: 
- MapBiomas — falso color: 
- MapBiomas — NDVI: 
- MapBiomas — NDBI: 
- MapBiomas — NUACI: 
- Landsat C2 — color natural: 
- Landsat C2 — falso color: 
- Landsat C2 — NDVI cuantitativo en consola: 
- Sentinel-2 — color natural: 
- Sentinel-2 — falso color: 
- Sentinel-2 — NDVI cuantitativo en consola: 
- Contexto 500 m: 
- Fuente visual adicional distinta del visor: 

### E. Observaciones visuales de Jhoreck

- MapBiomas — color natural:
- MapBiomas — falso color:
- MapBiomas — NDVI:
- MapBiomas — NDBI, si aparece:
- MapBiomas — NUACI, si aparece:
- Landsat C2 — color natural:
- Landsat C2 — falso color:
- Sentinel-2 — color natural, si aparece:
- Sentinel-2 — falso color, si aparece:
- Forma, textura, conectividad y contexto del candidato:
- ¿El patrón es uniforme en la huella?: 
- Observación integradora, sin asignar todavía veredicto:

### F. Incidencias y limitaciones

- Errores de consola o teselas:
- Capas no mostradas:
- Dificultad de interpretación:
- Otra observación:

### G. Estado del caso

- `LISTO_PARA_INTEGRAR: `
- Motivo si la respuesta es `NO`:

---

## EVAL-041

### A. Identidad esperada

- Dominio: `anillo_sistema`
- Unidad ID: `sistema|500_1000`
- Unidad: Sistema disuelto 500_1000
- Estrato: `E5_RECUPERACION_68_70`
- Años esperados — inicio | evento | fin: `1993 | 1994 | 1998`

### B. Control previo

- [ ] El desplegable muestra `EVAL-041`.
- [ ] La unidad y el estrato coinciden.
- [ ] Los años coinciden.
- [ ] Las capas principales de MapBiomas cargaron.
- [ ] El contorno candidato se distingue de la ventana 150 × 150 m.

### C. Salida completa de la consola GEE

[INICIO_CONSOLA_GEE]

PEGAR AQUÍ TODA LA SALIDA PERTINENTE DE LA CONSOLA PARA EVAL-041.

[FIN_CONSOLA_GEE]

### D. Capas revisadas

- MapBiomas — color natural: 
- MapBiomas — falso color: 
- MapBiomas — NDVI: 
- MapBiomas — NDBI: 
- MapBiomas — NUACI: 
- Landsat C2 — color natural: 
- Landsat C2 — falso color: 
- Landsat C2 — NDVI cuantitativo en consola: 
- Sentinel-2 — color natural: 
- Sentinel-2 — falso color: 
- Sentinel-2 — NDVI cuantitativo en consola: 
- Contexto 500 m: 
- Fuente visual adicional distinta del visor: 

### E. Observaciones visuales de Jhoreck

- MapBiomas — color natural:
- MapBiomas — falso color:
- MapBiomas — NDVI:
- MapBiomas — NDBI, si aparece:
- MapBiomas — NUACI, si aparece:
- Landsat C2 — color natural:
- Landsat C2 — falso color:
- Sentinel-2 — color natural, si aparece:
- Sentinel-2 — falso color, si aparece:
- Forma, textura, conectividad y contexto del candidato:
- ¿El patrón es uniforme en la huella?: 
- Observación integradora, sin asignar todavía veredicto:

### F. Incidencias y limitaciones

- Errores de consola o teselas:
- Capas no mostradas:
- Dificultad de interpretación:
- Otra observación:

### G. Estado del caso

- `LISTO_PARA_INTEGRAR: `
- Motivo si la respuesta es `NO`:

---

## EVAL-042

### A. Identidad esperada

- Dominio: `anillo_sistema`
- Unidad ID: `sistema|500_1000`
- Unidad: Sistema disuelto 500_1000
- Estrato: `E3_URBANO_CENSURADO`
- Años esperados — inicio | evento | fin: `2023 | 2024 | 2024`

### B. Control previo

- [ ] El desplegable muestra `EVAL-042`.
- [ ] La unidad y el estrato coinciden.
- [ ] Los años coinciden.
- [ ] Las capas principales de MapBiomas cargaron.
- [ ] El contorno candidato se distingue de la ventana 150 × 150 m.

### C. Salida completa de la consola GEE

[INICIO_CONSOLA_GEE]

PEGAR AQUÍ TODA LA SALIDA PERTINENTE DE LA CONSOLA PARA EVAL-042.

[FIN_CONSOLA_GEE]

### D. Capas revisadas

- MapBiomas — color natural: 
- MapBiomas — falso color: 
- MapBiomas — NDVI: 
- MapBiomas — NDBI: 
- MapBiomas — NUACI: 
- Landsat C2 — color natural: 
- Landsat C2 — falso color: 
- Landsat C2 — NDVI cuantitativo en consola: 
- Sentinel-2 — color natural: 
- Sentinel-2 — falso color: 
- Sentinel-2 — NDVI cuantitativo en consola: 
- Contexto 500 m: 
- Fuente visual adicional distinta del visor: 

### E. Observaciones visuales de Jhoreck

- MapBiomas — color natural:
- MapBiomas — falso color:
- MapBiomas — NDVI:
- MapBiomas — NDBI, si aparece:
- MapBiomas — NUACI, si aparece:
- Landsat C2 — color natural:
- Landsat C2 — falso color:
- Sentinel-2 — color natural, si aparece:
- Sentinel-2 — falso color, si aparece:
- Forma, textura, conectividad y contexto del candidato:
- ¿El patrón es uniforme en la huella?: 
- Observación integradora, sin asignar todavía veredicto:

### F. Incidencias y limitaciones

- Errores de consola o teselas:
- Capas no mostradas:
- Dificultad de interpretación:
- Otra observación:

### G. Estado del caso

- `LISTO_PARA_INTEGRAR: `
- Motivo si la respuesta es `NO`:

---

## EVAL-043

### A. Identidad esperada

- Dominio: `kba_restricted`
- Unidad ID: `kba|atocongo`
- Unidad: Lomas de Atocongo
- Estrato: `E4_INTERCAMBIO_68_70`
- Años esperados — inicio | evento | fin: `2010 | 2011 | 2015`

### B. Control previo

- [ ] El desplegable muestra `EVAL-043`.
- [ ] La unidad y el estrato coinciden.
- [ ] Los años coinciden.
- [ ] Las capas principales de MapBiomas cargaron.
- [ ] El contorno candidato se distingue de la ventana 150 × 150 m.

### C. Salida completa de la consola GEE

[INICIO_CONSOLA_GEE]

PEGAR AQUÍ TODA LA SALIDA PERTINENTE DE LA CONSOLA PARA EVAL-043.

[FIN_CONSOLA_GEE]

### D. Capas revisadas

- MapBiomas — color natural: 
- MapBiomas — falso color: 
- MapBiomas — NDVI: 
- MapBiomas — NDBI: 
- MapBiomas — NUACI: 
- Landsat C2 — color natural: 
- Landsat C2 — falso color: 
- Landsat C2 — NDVI cuantitativo en consola: 
- Sentinel-2 — color natural: 
- Sentinel-2 — falso color: 
- Sentinel-2 — NDVI cuantitativo en consola: 
- Contexto 500 m: 
- Fuente visual adicional distinta del visor: 

### E. Observaciones visuales de Jhoreck

- MapBiomas — color natural:
- MapBiomas — falso color:
- MapBiomas — NDVI:
- MapBiomas — NDBI, si aparece:
- MapBiomas — NUACI, si aparece:
- Landsat C2 — color natural:
- Landsat C2 — falso color:
- Sentinel-2 — color natural, si aparece:
- Sentinel-2 — falso color, si aparece:
- Forma, textura, conectividad y contexto del candidato:
- ¿El patrón es uniforme en la huella?: 
- Observación integradora, sin asignar todavía veredicto:

### F. Incidencias y limitaciones

- Errores de consola o teselas:
- Capas no mostradas:
- Dificultad de interpretación:
- Otra observación:

### G. Estado del caso

- `LISTO_PARA_INTEGRAR: `
- Motivo si la respuesta es `NO`:

---

## EVAL-044

### A. Identidad esperada

- Dominio: `acr`
- Unidad ID: `acr|ancon`
- Unidad: Lomas de Ancón
- Estrato: `E4_INTERCAMBIO_68_70`
- Años esperados — inicio | evento | fin: `2000 | 2001 | 2005`

### B. Control previo

- [ ] El desplegable muestra `EVAL-044`.
- [ ] La unidad y el estrato coinciden.
- [ ] Los años coinciden.
- [ ] Las capas principales de MapBiomas cargaron.
- [ ] El contorno candidato se distingue de la ventana 150 × 150 m.

### C. Salida completa de la consola GEE

[INICIO_CONSOLA_GEE]

PEGAR AQUÍ TODA LA SALIDA PERTINENTE DE LA CONSOLA PARA EVAL-044.

[FIN_CONSOLA_GEE]

### D. Capas revisadas

- MapBiomas — color natural: 
- MapBiomas — falso color: 
- MapBiomas — NDVI: 
- MapBiomas — NDBI: 
- MapBiomas — NUACI: 
- Landsat C2 — color natural: 
- Landsat C2 — falso color: 
- Landsat C2 — NDVI cuantitativo en consola: 
- Sentinel-2 — color natural: 
- Sentinel-2 — falso color: 
- Sentinel-2 — NDVI cuantitativo en consola: 
- Contexto 500 m: 
- Fuente visual adicional distinta del visor: 

### E. Observaciones visuales de Jhoreck

- MapBiomas — color natural:
- MapBiomas — falso color:
- MapBiomas — NDVI:
- MapBiomas — NDBI, si aparece:
- MapBiomas — NUACI, si aparece:
- Landsat C2 — color natural:
- Landsat C2 — falso color:
- Sentinel-2 — color natural, si aparece:
- Sentinel-2 — falso color, si aparece:
- Forma, textura, conectividad y contexto del candidato:
- ¿El patrón es uniforme en la huella?: 
- Observación integradora, sin asignar todavía veredicto:

### F. Incidencias y limitaciones

- Errores de consola o teselas:
- Capas no mostradas:
- Dificultad de interpretación:
- Otra observación:

### G. Estado del caso

- `LISTO_PARA_INTEGRAR: `
- Motivo si la respuesta es `NO`:

---

## EVAL-045

### A. Identidad esperada

- Dominio: `kba_restricted`
- Unidad ID: `kba|atocongo`
- Unidad: Lomas de Atocongo
- Estrato: `E3_URBANO_CENSURADO`
- Años esperados — inicio | evento | fin: `2023 | 2024 | 2024`

### B. Control previo

- [ ] El desplegable muestra `EVAL-045`.
- [ ] La unidad y el estrato coinciden.
- [ ] Los años coinciden.
- [ ] Las capas principales de MapBiomas cargaron.
- [ ] El contorno candidato se distingue de la ventana 150 × 150 m.

### C. Salida completa de la consola GEE

[INICIO_CONSOLA_GEE]

PEGAR AQUÍ TODA LA SALIDA PERTINENTE DE LA CONSOLA PARA EVAL-045.

[FIN_CONSOLA_GEE]

### D. Capas revisadas

- MapBiomas — color natural: 
- MapBiomas — falso color: 
- MapBiomas — NDVI: 
- MapBiomas — NDBI: 
- MapBiomas — NUACI: 
- Landsat C2 — color natural: 
- Landsat C2 — falso color: 
- Landsat C2 — NDVI cuantitativo en consola: 
- Sentinel-2 — color natural: 
- Sentinel-2 — falso color: 
- Sentinel-2 — NDVI cuantitativo en consola: 
- Contexto 500 m: 
- Fuente visual adicional distinta del visor: 

### E. Observaciones visuales de Jhoreck

- MapBiomas — color natural:
- MapBiomas — falso color:
- MapBiomas — NDVI:
- MapBiomas — NDBI, si aparece:
- MapBiomas — NUACI, si aparece:
- Landsat C2 — color natural:
- Landsat C2 — falso color:
- Sentinel-2 — color natural, si aparece:
- Sentinel-2 — falso color, si aparece:
- Forma, textura, conectividad y contexto del candidato:
- ¿El patrón es uniforme en la huella?: 
- Observación integradora, sin asignar todavía veredicto:

### F. Incidencias y limitaciones

- Errores de consola o teselas:
- Capas no mostradas:
- Dificultad de interpretación:
- Otra observación:

### G. Estado del caso

- `LISTO_PARA_INTEGRAR: `
- Motivo si la respuesta es `NO`:

---

## EVAL-046

### A. Identidad esperada

- Dominio: `anillo_sistema`
- Unidad ID: `sistema|500_1000`
- Unidad: Sistema disuelto 500_1000
- Estrato: `E1_PERSISTENTE70`
- Años esperados — inicio | evento | fin: `1985 | N/A | 2024`

### B. Control previo

- [ ] El desplegable muestra `EVAL-046`.
- [ ] La unidad y el estrato coinciden.
- [ ] Los años coinciden.
- [ ] Las capas principales de MapBiomas cargaron.
- [ ] El contorno candidato se distingue de la ventana 150 × 150 m.

### C. Salida completa de la consola GEE

[INICIO_CONSOLA_GEE]

PEGAR AQUÍ TODA LA SALIDA PERTINENTE DE LA CONSOLA PARA EVAL-046.

[FIN_CONSOLA_GEE]

### D. Capas revisadas

- MapBiomas — color natural: 
- MapBiomas — falso color: 
- MapBiomas — NDVI: 
- MapBiomas — NDBI: 
- MapBiomas — NUACI: 
- Landsat C2 — color natural: 
- Landsat C2 — falso color: 
- Landsat C2 — NDVI cuantitativo en consola: 
- Sentinel-2 — color natural: 
- Sentinel-2 — falso color: 
- Sentinel-2 — NDVI cuantitativo en consola: 
- Contexto 500 m: 
- Fuente visual adicional distinta del visor: 

### E. Observaciones visuales de Jhoreck

- MapBiomas — color natural:
- MapBiomas — falso color:
- MapBiomas — NDVI:
- MapBiomas — NDBI, si aparece:
- MapBiomas — NUACI, si aparece:
- Landsat C2 — color natural:
- Landsat C2 — falso color:
- Sentinel-2 — color natural, si aparece:
- Sentinel-2 — falso color, si aparece:
- Forma, textura, conectividad y contexto del candidato:
- ¿El patrón es uniforme en la huella?: 
- Observación integradora, sin asignar todavía veredicto:

### F. Incidencias y limitaciones

- Errores de consola o teselas:
- Capas no mostradas:
- Dificultad de interpretación:
- Otra observación:

### G. Estado del caso

- `LISTO_PARA_INTEGRAR: `
- Motivo si la respuesta es `NO`:

---

## EVAL-047

### A. Identidad esperada

- Dominio: `anillo_sistema`
- Unidad ID: `sistema|0_500`
- Unidad: Sistema disuelto 0_500
- Estrato: `E2_URBANO_W5`
- Años esperados — inicio | evento | fin: `2012 | 2013 | 2017`

### B. Control previo

- [ ] El desplegable muestra `EVAL-047`.
- [ ] La unidad y el estrato coinciden.
- [ ] Los años coinciden.
- [ ] Las capas principales de MapBiomas cargaron.
- [ ] El contorno candidato se distingue de la ventana 150 × 150 m.

### C. Salida completa de la consola GEE

[INICIO_CONSOLA_GEE]

PEGAR AQUÍ TODA LA SALIDA PERTINENTE DE LA CONSOLA PARA EVAL-047.

[FIN_CONSOLA_GEE]

### D. Capas revisadas

- MapBiomas — color natural: 
- MapBiomas — falso color: 
- MapBiomas — NDVI: 
- MapBiomas — NDBI: 
- MapBiomas — NUACI: 
- Landsat C2 — color natural: 
- Landsat C2 — falso color: 
- Landsat C2 — NDVI cuantitativo en consola: 
- Sentinel-2 — color natural: 
- Sentinel-2 — falso color: 
- Sentinel-2 — NDVI cuantitativo en consola: 
- Contexto 500 m: 
- Fuente visual adicional distinta del visor: 

### E. Observaciones visuales de Jhoreck

- MapBiomas — color natural:
- MapBiomas — falso color:
- MapBiomas — NDVI:
- MapBiomas — NDBI, si aparece:
- MapBiomas — NUACI, si aparece:
- Landsat C2 — color natural:
- Landsat C2 — falso color:
- Sentinel-2 — color natural, si aparece:
- Sentinel-2 — falso color, si aparece:
- Forma, textura, conectividad y contexto del candidato:
- ¿El patrón es uniforme en la huella?: 
- Observación integradora, sin asignar todavía veredicto:

### F. Incidencias y limitaciones

- Errores de consola o teselas:
- Capas no mostradas:
- Dificultad de interpretación:
- Otra observación:

### G. Estado del caso

- `LISTO_PARA_INTEGRAR: `
- Motivo si la respuesta es `NO`:

---

## EVAL-048

### A. Identidad esperada

- Dominio: `kba_restricted`
- Unidad ID: `kba|atocongo`
- Unidad: Lomas de Atocongo
- Estrato: `E1_PERSISTENTE70`
- Años esperados — inicio | evento | fin: `1985 | N/A | 2024`

### B. Control previo

- [ ] El desplegable muestra `EVAL-048`.
- [ ] La unidad y el estrato coinciden.
- [ ] Los años coinciden.
- [ ] Las capas principales de MapBiomas cargaron.
- [ ] El contorno candidato se distingue de la ventana 150 × 150 m.

### C. Salida completa de la consola GEE

[INICIO_CONSOLA_GEE]

PEGAR AQUÍ TODA LA SALIDA PERTINENTE DE LA CONSOLA PARA EVAL-048.

[FIN_CONSOLA_GEE]

### D. Capas revisadas

- MapBiomas — color natural: 
- MapBiomas — falso color: 
- MapBiomas — NDVI: 
- MapBiomas — NDBI: 
- MapBiomas — NUACI: 
- Landsat C2 — color natural: 
- Landsat C2 — falso color: 
- Landsat C2 — NDVI cuantitativo en consola: 
- Sentinel-2 — color natural: 
- Sentinel-2 — falso color: 
- Sentinel-2 — NDVI cuantitativo en consola: 
- Contexto 500 m: 
- Fuente visual adicional distinta del visor: 

### E. Observaciones visuales de Jhoreck

- MapBiomas — color natural:
- MapBiomas — falso color:
- MapBiomas — NDVI:
- MapBiomas — NDBI, si aparece:
- MapBiomas — NUACI, si aparece:
- Landsat C2 — color natural:
- Landsat C2 — falso color:
- Sentinel-2 — color natural, si aparece:
- Sentinel-2 — falso color, si aparece:
- Forma, textura, conectividad y contexto del candidato:
- ¿El patrón es uniforme en la huella?: 
- Observación integradora, sin asignar todavía veredicto:

### F. Incidencias y limitaciones

- Errores de consola o teselas:
- Capas no mostradas:
- Dificultad de interpretación:
- Otra observación:

### G. Estado del caso

- `LISTO_PARA_INTEGRAR: `
- Motivo si la respuesta es `NO`:

---

## EVAL-049

### A. Identidad esperada

- Dominio: `kba_restricted`
- Unidad ID: `kba|atocongo`
- Unidad: Lomas de Atocongo
- Estrato: `E2_URBANO_W5`
- Años esperados — inicio | evento | fin: `2013 | 2014 | 2018`

### B. Control previo

- [ ] El desplegable muestra `EVAL-049`.
- [ ] La unidad y el estrato coinciden.
- [ ] Los años coinciden.
- [ ] Las capas principales de MapBiomas cargaron.
- [ ] El contorno candidato se distingue de la ventana 150 × 150 m.

### C. Salida completa de la consola GEE

[INICIO_CONSOLA_GEE]

PEGAR AQUÍ TODA LA SALIDA PERTINENTE DE LA CONSOLA PARA EVAL-049.

[FIN_CONSOLA_GEE]

### D. Capas revisadas

- MapBiomas — color natural: 
- MapBiomas — falso color: 
- MapBiomas — NDVI: 
- MapBiomas — NDBI: 
- MapBiomas — NUACI: 
- Landsat C2 — color natural: 
- Landsat C2 — falso color: 
- Landsat C2 — NDVI cuantitativo en consola: 
- Sentinel-2 — color natural: 
- Sentinel-2 — falso color: 
- Sentinel-2 — NDVI cuantitativo en consola: 
- Contexto 500 m: 
- Fuente visual adicional distinta del visor: 

### E. Observaciones visuales de Jhoreck

- MapBiomas — color natural:
- MapBiomas — falso color:
- MapBiomas — NDVI:
- MapBiomas — NDBI, si aparece:
- MapBiomas — NUACI, si aparece:
- Landsat C2 — color natural:
- Landsat C2 — falso color:
- Sentinel-2 — color natural, si aparece:
- Sentinel-2 — falso color, si aparece:
- Forma, textura, conectividad y contexto del candidato:
- ¿El patrón es uniforme en la huella?: 
- Observación integradora, sin asignar todavía veredicto:

### F. Incidencias y limitaciones

- Errores de consola o teselas:
- Capas no mostradas:
- Dificultad de interpretación:
- Otra observación:

### G. Estado del caso

- `LISTO_PARA_INTEGRAR: `
- Motivo si la respuesta es `NO`:

---

## EVAL-050

### A. Identidad esperada

- Dominio: `kba_restricted`
- Unidad ID: `kba|atocongo`
- Unidad: Lomas de Atocongo
- Estrato: `E3_URBANO_CENSURADO`
- Años esperados — inicio | evento | fin: `2023 | 2024 | 2024`

### B. Control previo

- [ ] El desplegable muestra `EVAL-050`.
- [ ] La unidad y el estrato coinciden.
- [ ] Los años coinciden.
- [ ] Las capas principales de MapBiomas cargaron.
- [ ] El contorno candidato se distingue de la ventana 150 × 150 m.

### C. Salida completa de la consola GEE

[INICIO_CONSOLA_GEE]

PEGAR AQUÍ TODA LA SALIDA PERTINENTE DE LA CONSOLA PARA EVAL-050.

[FIN_CONSOLA_GEE]

### D. Capas revisadas

- MapBiomas — color natural: 
- MapBiomas — falso color: 
- MapBiomas — NDVI: 
- MapBiomas — NDBI: 
- MapBiomas — NUACI: 
- Landsat C2 — color natural: 
- Landsat C2 — falso color: 
- Landsat C2 — NDVI cuantitativo en consola: 
- Sentinel-2 — color natural: 
- Sentinel-2 — falso color: 
- Sentinel-2 — NDVI cuantitativo en consola: 
- Contexto 500 m: 
- Fuente visual adicional distinta del visor: 

### E. Observaciones visuales de Jhoreck

- MapBiomas — color natural:
- MapBiomas — falso color:
- MapBiomas — NDVI:
- MapBiomas — NDBI, si aparece:
- MapBiomas — NUACI, si aparece:
- Landsat C2 — color natural:
- Landsat C2 — falso color:
- Sentinel-2 — color natural, si aparece:
- Sentinel-2 — falso color, si aparece:
- Forma, textura, conectividad y contexto del candidato:
- ¿El patrón es uniforme en la huella?: 
- Observación integradora, sin asignar todavía veredicto:

### F. Incidencias y limitaciones

- Errores de consola o teselas:
- Capas no mostradas:
- Dificultad de interpretación:
- Otra observación:

### G. Estado del caso

- `LISTO_PARA_INTEGRAR: `
- Motivo si la respuesta es `NO`:

---

## EVAL-051

### A. Identidad esperada

- Dominio: `anillo_sistema`
- Unidad ID: `sistema|0_500`
- Unidad: Sistema disuelto 0_500
- Estrato: `E6_CAMBIO_70_13`
- Años esperados — inicio | evento | fin: `2014 | 2015 | 2019`

### B. Control previo

- [ ] El desplegable muestra `EVAL-051`.
- [ ] La unidad y el estrato coinciden.
- [ ] Los años coinciden.
- [ ] Las capas principales de MapBiomas cargaron.
- [ ] El contorno candidato se distingue de la ventana 150 × 150 m.

### C. Salida completa de la consola GEE

[INICIO_CONSOLA_GEE]

PEGAR AQUÍ TODA LA SALIDA PERTINENTE DE LA CONSOLA PARA EVAL-051.

[FIN_CONSOLA_GEE]

### D. Capas revisadas

- MapBiomas — color natural: 
- MapBiomas — falso color: 
- MapBiomas — NDVI: 
- MapBiomas — NDBI: 
- MapBiomas — NUACI: 
- Landsat C2 — color natural: 
- Landsat C2 — falso color: 
- Landsat C2 — NDVI cuantitativo en consola: 
- Sentinel-2 — color natural: 
- Sentinel-2 — falso color: 
- Sentinel-2 — NDVI cuantitativo en consola: 
- Contexto 500 m: 
- Fuente visual adicional distinta del visor: 

### E. Observaciones visuales de Jhoreck

- MapBiomas — color natural:
- MapBiomas — falso color:
- MapBiomas — NDVI:
- MapBiomas — NDBI, si aparece:
- MapBiomas — NUACI, si aparece:
- Landsat C2 — color natural:
- Landsat C2 — falso color:
- Sentinel-2 — color natural, si aparece:
- Sentinel-2 — falso color, si aparece:
- Forma, textura, conectividad y contexto del candidato:
- ¿El patrón es uniforme en la huella?: 
- Observación integradora, sin asignar todavía veredicto:

### F. Incidencias y limitaciones

- Errores de consola o teselas:
- Capas no mostradas:
- Dificultad de interpretación:
- Otra observación:

### G. Estado del caso

- `LISTO_PARA_INTEGRAR: `
- Motivo si la respuesta es `NO`:

---

## EVAL-052

### A. Identidad esperada

- Dominio: `acr`
- Unidad ID: `acr|ancon`
- Unidad: Lomas de Ancón
- Estrato: `E5_RECUPERACION_68_70`
- Años esperados — inicio | evento | fin: `1989 | 1990 | 1994`

### B. Control previo

- [ ] El desplegable muestra `EVAL-052`.
- [ ] La unidad y el estrato coinciden.
- [ ] Los años coinciden.
- [ ] Las capas principales de MapBiomas cargaron.
- [ ] El contorno candidato se distingue de la ventana 150 × 150 m.

### C. Salida completa de la consola GEE

[INICIO_CONSOLA_GEE]

PEGAR AQUÍ TODA LA SALIDA PERTINENTE DE LA CONSOLA PARA EVAL-052.

[FIN_CONSOLA_GEE]

### D. Capas revisadas

- MapBiomas — color natural: 
- MapBiomas — falso color: 
- MapBiomas — NDVI: 
- MapBiomas — NDBI: 
- MapBiomas — NUACI: 
- Landsat C2 — color natural: 
- Landsat C2 — falso color: 
- Landsat C2 — NDVI cuantitativo en consola: 
- Sentinel-2 — color natural: 
- Sentinel-2 — falso color: 
- Sentinel-2 — NDVI cuantitativo en consola: 
- Contexto 500 m: 
- Fuente visual adicional distinta del visor: 

### E. Observaciones visuales de Jhoreck

- MapBiomas — color natural:
- MapBiomas — falso color:
- MapBiomas — NDVI:
- MapBiomas — NDBI, si aparece:
- MapBiomas — NUACI, si aparece:
- Landsat C2 — color natural:
- Landsat C2 — falso color:
- Sentinel-2 — color natural, si aparece:
- Sentinel-2 — falso color, si aparece:
- Forma, textura, conectividad y contexto del candidato:
- ¿El patrón es uniforme en la huella?: 
- Observación integradora, sin asignar todavía veredicto:

### F. Incidencias y limitaciones

- Errores de consola o teselas:
- Capas no mostradas:
- Dificultad de interpretación:
- Otra observación:

### G. Estado del caso

- `LISTO_PARA_INTEGRAR: `
- Motivo si la respuesta es `NO`:

---

## EVAL-053

### A. Identidad esperada

- Dominio: `kba_restricted`
- Unidad ID: `kba|atocongo`
- Unidad: Lomas de Atocongo
- Estrato: `E2_URBANO_W5`
- Años esperados — inicio | evento | fin: `2016 | 2017 | 2021`

### B. Control previo

- [ ] El desplegable muestra `EVAL-053`.
- [ ] La unidad y el estrato coinciden.
- [ ] Los años coinciden.
- [ ] Las capas principales de MapBiomas cargaron.
- [ ] El contorno candidato se distingue de la ventana 150 × 150 m.

### C. Salida completa de la consola GEE

[INICIO_CONSOLA_GEE]

PEGAR AQUÍ TODA LA SALIDA PERTINENTE DE LA CONSOLA PARA EVAL-053.

[FIN_CONSOLA_GEE]

### D. Capas revisadas

- MapBiomas — color natural: 
- MapBiomas — falso color: 
- MapBiomas — NDVI: 
- MapBiomas — NDBI: 
- MapBiomas — NUACI: 
- Landsat C2 — color natural: 
- Landsat C2 — falso color: 
- Landsat C2 — NDVI cuantitativo en consola: 
- Sentinel-2 — color natural: 
- Sentinel-2 — falso color: 
- Sentinel-2 — NDVI cuantitativo en consola: 
- Contexto 500 m: 
- Fuente visual adicional distinta del visor: 

### E. Observaciones visuales de Jhoreck

- MapBiomas — color natural:
- MapBiomas — falso color:
- MapBiomas — NDVI:
- MapBiomas — NDBI, si aparece:
- MapBiomas — NUACI, si aparece:
- Landsat C2 — color natural:
- Landsat C2 — falso color:
- Sentinel-2 — color natural, si aparece:
- Sentinel-2 — falso color, si aparece:
- Forma, textura, conectividad y contexto del candidato:
- ¿El patrón es uniforme en la huella?: 
- Observación integradora, sin asignar todavía veredicto:

### F. Incidencias y limitaciones

- Errores de consola o teselas:
- Capas no mostradas:
- Dificultad de interpretación:
- Otra observación:

### G. Estado del caso

- `LISTO_PARA_INTEGRAR: `
- Motivo si la respuesta es `NO`:

---

## EVAL-054

### A. Identidad esperada

- Dominio: `acr`
- Unidad ID: `acr|ancon`
- Unidad: Lomas de Ancón
- Estrato: `E1_PERSISTENTE70`
- Años esperados — inicio | evento | fin: `1985 | N/A | 2024`

### B. Control previo

- [ ] El desplegable muestra `EVAL-054`.
- [ ] La unidad y el estrato coinciden.
- [ ] Los años coinciden.
- [ ] Las capas principales de MapBiomas cargaron.
- [ ] El contorno candidato se distingue de la ventana 150 × 150 m.

### C. Salida completa de la consola GEE

[INICIO_CONSOLA_GEE]

PEGAR AQUÍ TODA LA SALIDA PERTINENTE DE LA CONSOLA PARA EVAL-054.

[FIN_CONSOLA_GEE]

### D. Capas revisadas

- MapBiomas — color natural: 
- MapBiomas — falso color: 
- MapBiomas — NDVI: 
- MapBiomas — NDBI: 
- MapBiomas — NUACI: 
- Landsat C2 — color natural: 
- Landsat C2 — falso color: 
- Landsat C2 — NDVI cuantitativo en consola: 
- Sentinel-2 — color natural: 
- Sentinel-2 — falso color: 
- Sentinel-2 — NDVI cuantitativo en consola: 
- Contexto 500 m: 
- Fuente visual adicional distinta del visor: 

### E. Observaciones visuales de Jhoreck

- MapBiomas — color natural:
- MapBiomas — falso color:
- MapBiomas — NDVI:
- MapBiomas — NDBI, si aparece:
- MapBiomas — NUACI, si aparece:
- Landsat C2 — color natural:
- Landsat C2 — falso color:
- Sentinel-2 — color natural, si aparece:
- Sentinel-2 — falso color, si aparece:
- Forma, textura, conectividad y contexto del candidato:
- ¿El patrón es uniforme en la huella?: 
- Observación integradora, sin asignar todavía veredicto:

### F. Incidencias y limitaciones

- Errores de consola o teselas:
- Capas no mostradas:
- Dificultad de interpretación:
- Otra observación:

### G. Estado del caso

- `LISTO_PARA_INTEGRAR: `
- Motivo si la respuesta es `NO`:

---

## EVAL-055

### A. Identidad esperada

- Dominio: `kba_restricted`
- Unidad ID: `kba|atocongo`
- Unidad: Lomas de Atocongo
- Estrato: `E4_INTERCAMBIO_68_70`
- Años esperados — inicio | evento | fin: `2012 | 2013 | 2017`

### B. Control previo

- [ ] El desplegable muestra `EVAL-055`.
- [ ] La unidad y el estrato coinciden.
- [ ] Los años coinciden.
- [ ] Las capas principales de MapBiomas cargaron.
- [ ] El contorno candidato se distingue de la ventana 150 × 150 m.

### C. Salida completa de la consola GEE

[INICIO_CONSOLA_GEE]

PEGAR AQUÍ TODA LA SALIDA PERTINENTE DE LA CONSOLA PARA EVAL-055.

[FIN_CONSOLA_GEE]

### D. Capas revisadas

- MapBiomas — color natural: 
- MapBiomas — falso color: 
- MapBiomas — NDVI: 
- MapBiomas — NDBI: 
- MapBiomas — NUACI: 
- Landsat C2 — color natural: 
- Landsat C2 — falso color: 
- Landsat C2 — NDVI cuantitativo en consola: 
- Sentinel-2 — color natural: 
- Sentinel-2 — falso color: 
- Sentinel-2 — NDVI cuantitativo en consola: 
- Contexto 500 m: 
- Fuente visual adicional distinta del visor: 

### E. Observaciones visuales de Jhoreck

- MapBiomas — color natural:
- MapBiomas — falso color:
- MapBiomas — NDVI:
- MapBiomas — NDBI, si aparece:
- MapBiomas — NUACI, si aparece:
- Landsat C2 — color natural:
- Landsat C2 — falso color:
- Sentinel-2 — color natural, si aparece:
- Sentinel-2 — falso color, si aparece:
- Forma, textura, conectividad y contexto del candidato:
- ¿El patrón es uniforme en la huella?: 
- Observación integradora, sin asignar todavía veredicto:

### F. Incidencias y limitaciones

- Errores de consola o teselas:
- Capas no mostradas:
- Dificultad de interpretación:
- Otra observación:

### G. Estado del caso

- `LISTO_PARA_INTEGRAR: `
- Motivo si la respuesta es `NO`:

---

## EVAL-056

### A. Identidad esperada

- Dominio: `anillo_sistema`
- Unidad ID: `sistema|0_500`
- Unidad: Sistema disuelto 0_500
- Estrato: `E6_CAMBIO_70_13`
- Años esperados — inicio | evento | fin: `2014 | 2015 | 2019`

### B. Control previo

- [ ] El desplegable muestra `EVAL-056`.
- [ ] La unidad y el estrato coinciden.
- [ ] Los años coinciden.
- [ ] Las capas principales de MapBiomas cargaron.
- [ ] El contorno candidato se distingue de la ventana 150 × 150 m.

### C. Salida completa de la consola GEE

[INICIO_CONSOLA_GEE]

PEGAR AQUÍ TODA LA SALIDA PERTINENTE DE LA CONSOLA PARA EVAL-056.

[FIN_CONSOLA_GEE]

### D. Capas revisadas

- MapBiomas — color natural: 
- MapBiomas — falso color: 
- MapBiomas — NDVI: 
- MapBiomas — NDBI: 
- MapBiomas — NUACI: 
- Landsat C2 — color natural: 
- Landsat C2 — falso color: 
- Landsat C2 — NDVI cuantitativo en consola: 
- Sentinel-2 — color natural: 
- Sentinel-2 — falso color: 
- Sentinel-2 — NDVI cuantitativo en consola: 
- Contexto 500 m: 
- Fuente visual adicional distinta del visor: 

### E. Observaciones visuales de Jhoreck

- MapBiomas — color natural:
- MapBiomas — falso color:
- MapBiomas — NDVI:
- MapBiomas — NDBI, si aparece:
- MapBiomas — NUACI, si aparece:
- Landsat C2 — color natural:
- Landsat C2 — falso color:
- Sentinel-2 — color natural, si aparece:
- Sentinel-2 — falso color, si aparece:
- Forma, textura, conectividad y contexto del candidato:
- ¿El patrón es uniforme en la huella?: 
- Observación integradora, sin asignar todavía veredicto:

### F. Incidencias y limitaciones

- Errores de consola o teselas:
- Capas no mostradas:
- Dificultad de interpretación:
- Otra observación:

### G. Estado del caso

- `LISTO_PARA_INTEGRAR: `
- Motivo si la respuesta es `NO`:

---

## EVAL-057

### A. Identidad esperada

- Dominio: `anillo_sistema`
- Unidad ID: `sistema|1000_2000`
- Unidad: Sistema disuelto 1000_2000
- Estrato: `E4_INTERCAMBIO_68_70`
- Años esperados — inicio | evento | fin: `2006 | 2007 | 2011`

### B. Control previo

- [ ] El desplegable muestra `EVAL-057`.
- [ ] La unidad y el estrato coinciden.
- [ ] Los años coinciden.
- [ ] Las capas principales de MapBiomas cargaron.
- [ ] El contorno candidato se distingue de la ventana 150 × 150 m.

### C. Salida completa de la consola GEE

[INICIO_CONSOLA_GEE]

PEGAR AQUÍ TODA LA SALIDA PERTINENTE DE LA CONSOLA PARA EVAL-057.

[FIN_CONSOLA_GEE]

### D. Capas revisadas

- MapBiomas — color natural: 
- MapBiomas — falso color: 
- MapBiomas — NDVI: 
- MapBiomas — NDBI: 
- MapBiomas — NUACI: 
- Landsat C2 — color natural: 
- Landsat C2 — falso color: 
- Landsat C2 — NDVI cuantitativo en consola: 
- Sentinel-2 — color natural: 
- Sentinel-2 — falso color: 
- Sentinel-2 — NDVI cuantitativo en consola: 
- Contexto 500 m: 
- Fuente visual adicional distinta del visor: 

### E. Observaciones visuales de Jhoreck

- MapBiomas — color natural:
- MapBiomas — falso color:
- MapBiomas — NDVI:
- MapBiomas — NDBI, si aparece:
- MapBiomas — NUACI, si aparece:
- Landsat C2 — color natural:
- Landsat C2 — falso color:
- Sentinel-2 — color natural, si aparece:
- Sentinel-2 — falso color, si aparece:
- Forma, textura, conectividad y contexto del candidato:
- ¿El patrón es uniforme en la huella?: 
- Observación integradora, sin asignar todavía veredicto:

### F. Incidencias y limitaciones

- Errores de consola o teselas:
- Capas no mostradas:
- Dificultad de interpretación:
- Otra observación:

### G. Estado del caso

- `LISTO_PARA_INTEGRAR: `
- Motivo si la respuesta es `NO`:

---

## EVAL-058

### A. Identidad esperada

- Dominio: `anillo_sistema`
- Unidad ID: `sistema|500_1000`
- Unidad: Sistema disuelto 500_1000
- Estrato: `E2_URBANO_W5`
- Años esperados — inicio | evento | fin: `2019 | 2020 | 2024`

### B. Control previo

- [ ] El desplegable muestra `EVAL-058`.
- [ ] La unidad y el estrato coinciden.
- [ ] Los años coinciden.
- [ ] Las capas principales de MapBiomas cargaron.
- [ ] El contorno candidato se distingue de la ventana 150 × 150 m.

### C. Salida completa de la consola GEE

[INICIO_CONSOLA_GEE]

PEGAR AQUÍ TODA LA SALIDA PERTINENTE DE LA CONSOLA PARA EVAL-058.

[FIN_CONSOLA_GEE]

### D. Capas revisadas

- MapBiomas — color natural: 
- MapBiomas — falso color: 
- MapBiomas — NDVI: 
- MapBiomas — NDBI: 
- MapBiomas — NUACI: 
- Landsat C2 — color natural: 
- Landsat C2 — falso color: 
- Landsat C2 — NDVI cuantitativo en consola: 
- Sentinel-2 — color natural: 
- Sentinel-2 — falso color: 
- Sentinel-2 — NDVI cuantitativo en consola: 
- Contexto 500 m: 
- Fuente visual adicional distinta del visor: 

### E. Observaciones visuales de Jhoreck

- MapBiomas — color natural:
- MapBiomas — falso color:
- MapBiomas — NDVI:
- MapBiomas — NDBI, si aparece:
- MapBiomas — NUACI, si aparece:
- Landsat C2 — color natural:
- Landsat C2 — falso color:
- Sentinel-2 — color natural, si aparece:
- Sentinel-2 — falso color, si aparece:
- Forma, textura, conectividad y contexto del candidato:
- ¿El patrón es uniforme en la huella?: 
- Observación integradora, sin asignar todavía veredicto:

### F. Incidencias y limitaciones

- Errores de consola o teselas:
- Capas no mostradas:
- Dificultad de interpretación:
- Otra observación:

### G. Estado del caso

- `LISTO_PARA_INTEGRAR: `
- Motivo si la respuesta es `NO`:

---

## EVAL-059

### A. Identidad esperada

- Dominio: `kba_restricted`
- Unidad ID: `kba|atocongo`
- Unidad: Lomas de Atocongo
- Estrato: `E5_RECUPERACION_68_70`
- Años esperados — inicio | evento | fin: `1996 | 1997 | 2001`

### B. Control previo

- [ ] El desplegable muestra `EVAL-059`.
- [ ] La unidad y el estrato coinciden.
- [ ] Los años coinciden.
- [ ] Las capas principales de MapBiomas cargaron.
- [ ] El contorno candidato se distingue de la ventana 150 × 150 m.

### C. Salida completa de la consola GEE

[INICIO_CONSOLA_GEE]

PEGAR AQUÍ TODA LA SALIDA PERTINENTE DE LA CONSOLA PARA EVAL-059.

[FIN_CONSOLA_GEE]

### D. Capas revisadas

- MapBiomas — color natural: 
- MapBiomas — falso color: 
- MapBiomas — NDVI: 
- MapBiomas — NDBI: 
- MapBiomas — NUACI: 
- Landsat C2 — color natural: 
- Landsat C2 — falso color: 
- Landsat C2 — NDVI cuantitativo en consola: 
- Sentinel-2 — color natural: 
- Sentinel-2 — falso color: 
- Sentinel-2 — NDVI cuantitativo en consola: 
- Contexto 500 m: 
- Fuente visual adicional distinta del visor: 

### E. Observaciones visuales de Jhoreck

- MapBiomas — color natural:
- MapBiomas — falso color:
- MapBiomas — NDVI:
- MapBiomas — NDBI, si aparece:
- MapBiomas — NUACI, si aparece:
- Landsat C2 — color natural:
- Landsat C2 — falso color:
- Sentinel-2 — color natural, si aparece:
- Sentinel-2 — falso color, si aparece:
- Forma, textura, conectividad y contexto del candidato:
- ¿El patrón es uniforme en la huella?: 
- Observación integradora, sin asignar todavía veredicto:

### F. Incidencias y limitaciones

- Errores de consola o teselas:
- Capas no mostradas:
- Dificultad de interpretación:
- Otra observación:

### G. Estado del caso

- `LISTO_PARA_INTEGRAR: `
- Motivo si la respuesta es `NO`:

---

## EVAL-060

### A. Identidad esperada

- Dominio: `kba_restricted`
- Unidad ID: `kba|atocongo`
- Unidad: Lomas de Atocongo
- Estrato: `E4_INTERCAMBIO_68_70`
- Años esperados — inicio | evento | fin: `2006 | 2007 | 2011`

### B. Control previo

- [ ] El desplegable muestra `EVAL-060`.
- [ ] La unidad y el estrato coinciden.
- [ ] Los años coinciden.
- [ ] Las capas principales de MapBiomas cargaron.
- [ ] El contorno candidato se distingue de la ventana 150 × 150 m.

### C. Salida completa de la consola GEE

[INICIO_CONSOLA_GEE]

PEGAR AQUÍ TODA LA SALIDA PERTINENTE DE LA CONSOLA PARA EVAL-060.

[FIN_CONSOLA_GEE]

### D. Capas revisadas

- MapBiomas — color natural: 
- MapBiomas — falso color: 
- MapBiomas — NDVI: 
- MapBiomas — NDBI: 
- MapBiomas — NUACI: 
- Landsat C2 — color natural: 
- Landsat C2 — falso color: 
- Landsat C2 — NDVI cuantitativo en consola: 
- Sentinel-2 — color natural: 
- Sentinel-2 — falso color: 
- Sentinel-2 — NDVI cuantitativo en consola: 
- Contexto 500 m: 
- Fuente visual adicional distinta del visor: 

### E. Observaciones visuales de Jhoreck

- MapBiomas — color natural:
- MapBiomas — falso color:
- MapBiomas — NDVI:
- MapBiomas — NDBI, si aparece:
- MapBiomas — NUACI, si aparece:
- Landsat C2 — color natural:
- Landsat C2 — falso color:
- Sentinel-2 — color natural, si aparece:
- Sentinel-2 — falso color, si aparece:
- Forma, textura, conectividad y contexto del candidato:
- ¿El patrón es uniforme en la huella?: 
- Observación integradora, sin asignar todavía veredicto:

### F. Incidencias y limitaciones

- Errores de consola o teselas:
- Capas no mostradas:
- Dificultad de interpretación:
- Otra observación:

### G. Estado del caso

- `LISTO_PARA_INTEGRAR: `
- Motivo si la respuesta es `NO`:

---

## EVAL-061

### A. Identidad esperada

- Dominio: `acr`
- Unidad ID: `acr|amancaes`
- Unidad: Lomas de Amancaes
- Estrato: `E2_URBANO_W5`
- Años esperados — inicio | evento | fin: `2019 | 2020 | 2024`

### B. Control previo

- [ ] El desplegable muestra `EVAL-061`.
- [ ] La unidad y el estrato coinciden.
- [ ] Los años coinciden.
- [ ] Las capas principales de MapBiomas cargaron.
- [ ] El contorno candidato se distingue de la ventana 150 × 150 m.

### C. Salida completa de la consola GEE

[INICIO_CONSOLA_GEE]

PEGAR AQUÍ TODA LA SALIDA PERTINENTE DE LA CONSOLA PARA EVAL-061.

[FIN_CONSOLA_GEE]

### D. Capas revisadas

- MapBiomas — color natural: 
- MapBiomas — falso color: 
- MapBiomas — NDVI: 
- MapBiomas — NDBI: 
- MapBiomas — NUACI: 
- Landsat C2 — color natural: 
- Landsat C2 — falso color: 
- Landsat C2 — NDVI cuantitativo en consola: 
- Sentinel-2 — color natural: 
- Sentinel-2 — falso color: 
- Sentinel-2 — NDVI cuantitativo en consola: 
- Contexto 500 m: 
- Fuente visual adicional distinta del visor: 

### E. Observaciones visuales de Jhoreck

- MapBiomas — color natural:
- MapBiomas — falso color:
- MapBiomas — NDVI:
- MapBiomas — NDBI, si aparece:
- MapBiomas — NUACI, si aparece:
- Landsat C2 — color natural:
- Landsat C2 — falso color:
- Sentinel-2 — color natural, si aparece:
- Sentinel-2 — falso color, si aparece:
- Forma, textura, conectividad y contexto del candidato:
- ¿El patrón es uniforme en la huella?: 
- Observación integradora, sin asignar todavía veredicto:

### F. Incidencias y limitaciones

- Errores de consola o teselas:
- Capas no mostradas:
- Dificultad de interpretación:
- Otra observación:

### G. Estado del caso

- `LISTO_PARA_INTEGRAR: `
- Motivo si la respuesta es `NO`:

---

## EVAL-062

### A. Identidad esperada

- Dominio: `anillo_sistema`
- Unidad ID: `sistema|0_500`
- Unidad: Sistema disuelto 0_500
- Estrato: `E3_URBANO_CENSURADO`
- Años esperados — inicio | evento | fin: `2022 | 2023 | 2024`

### B. Control previo

- [ ] El desplegable muestra `EVAL-062`.
- [ ] La unidad y el estrato coinciden.
- [ ] Los años coinciden.
- [ ] Las capas principales de MapBiomas cargaron.
- [ ] El contorno candidato se distingue de la ventana 150 × 150 m.

### C. Salida completa de la consola GEE

[INICIO_CONSOLA_GEE]

PEGAR AQUÍ TODA LA SALIDA PERTINENTE DE LA CONSOLA PARA EVAL-062.

[FIN_CONSOLA_GEE]

### D. Capas revisadas

- MapBiomas — color natural: 
- MapBiomas — falso color: 
- MapBiomas — NDVI: 
- MapBiomas — NDBI: 
- MapBiomas — NUACI: 
- Landsat C2 — color natural: 
- Landsat C2 — falso color: 
- Landsat C2 — NDVI cuantitativo en consola: 
- Sentinel-2 — color natural: 
- Sentinel-2 — falso color: 
- Sentinel-2 — NDVI cuantitativo en consola: 
- Contexto 500 m: 
- Fuente visual adicional distinta del visor: 

### E. Observaciones visuales de Jhoreck

- MapBiomas — color natural:
- MapBiomas — falso color:
- MapBiomas — NDVI:
- MapBiomas — NDBI, si aparece:
- MapBiomas — NUACI, si aparece:
- Landsat C2 — color natural:
- Landsat C2 — falso color:
- Sentinel-2 — color natural, si aparece:
- Sentinel-2 — falso color, si aparece:
- Forma, textura, conectividad y contexto del candidato:
- ¿El patrón es uniforme en la huella?: 
- Observación integradora, sin asignar todavía veredicto:

### F. Incidencias y limitaciones

- Errores de consola o teselas:
- Capas no mostradas:
- Dificultad de interpretación:
- Otra observación:

### G. Estado del caso

- `LISTO_PARA_INTEGRAR: `
- Motivo si la respuesta es `NO`:

---

## EVAL-063

### A. Identidad esperada

- Dominio: `kba_restricted`
- Unidad ID: `kba|atocongo`
- Unidad: Lomas de Atocongo
- Estrato: `E1_PERSISTENTE70`
- Años esperados — inicio | evento | fin: `1985 | N/A | 2024`

### B. Control previo

- [ ] El desplegable muestra `EVAL-063`.
- [ ] La unidad y el estrato coinciden.
- [ ] Los años coinciden.
- [ ] Las capas principales de MapBiomas cargaron.
- [ ] El contorno candidato se distingue de la ventana 150 × 150 m.

### C. Salida completa de la consola GEE

[INICIO_CONSOLA_GEE]

PEGAR AQUÍ TODA LA SALIDA PERTINENTE DE LA CONSOLA PARA EVAL-063.

[FIN_CONSOLA_GEE]

### D. Capas revisadas

- MapBiomas — color natural: 
- MapBiomas — falso color: 
- MapBiomas — NDVI: 
- MapBiomas — NDBI: 
- MapBiomas — NUACI: 
- Landsat C2 — color natural: 
- Landsat C2 — falso color: 
- Landsat C2 — NDVI cuantitativo en consola: 
- Sentinel-2 — color natural: 
- Sentinel-2 — falso color: 
- Sentinel-2 — NDVI cuantitativo en consola: 
- Contexto 500 m: 
- Fuente visual adicional distinta del visor: 

### E. Observaciones visuales de Jhoreck

- MapBiomas — color natural:
- MapBiomas — falso color:
- MapBiomas — NDVI:
- MapBiomas — NDBI, si aparece:
- MapBiomas — NUACI, si aparece:
- Landsat C2 — color natural:
- Landsat C2 — falso color:
- Sentinel-2 — color natural, si aparece:
- Sentinel-2 — falso color, si aparece:
- Forma, textura, conectividad y contexto del candidato:
- ¿El patrón es uniforme en la huella?: 
- Observación integradora, sin asignar todavía veredicto:

### F. Incidencias y limitaciones

- Errores de consola o teselas:
- Capas no mostradas:
- Dificultad de interpretación:
- Otra observación:

### G. Estado del caso

- `LISTO_PARA_INTEGRAR: `
- Motivo si la respuesta es `NO`:

---

## EVAL-064

### A. Identidad esperada

- Dominio: `acr`
- Unidad ID: `acr|amancaes`
- Unidad: Lomas de Amancaes
- Estrato: `E6_CAMBIO_70_13`
- Años esperados — inicio | evento | fin: `2014 | 2015 | 2019`

### B. Control previo

- [ ] El desplegable muestra `EVAL-064`.
- [ ] La unidad y el estrato coinciden.
- [ ] Los años coinciden.
- [ ] Las capas principales de MapBiomas cargaron.
- [ ] El contorno candidato se distingue de la ventana 150 × 150 m.

### C. Salida completa de la consola GEE

[INICIO_CONSOLA_GEE]

PEGAR AQUÍ TODA LA SALIDA PERTINENTE DE LA CONSOLA PARA EVAL-064.

[FIN_CONSOLA_GEE]

### D. Capas revisadas

- MapBiomas — color natural: 
- MapBiomas — falso color: 
- MapBiomas — NDVI: 
- MapBiomas — NDBI: 
- MapBiomas — NUACI: 
- Landsat C2 — color natural: 
- Landsat C2 — falso color: 
- Landsat C2 — NDVI cuantitativo en consola: 
- Sentinel-2 — color natural: 
- Sentinel-2 — falso color: 
- Sentinel-2 — NDVI cuantitativo en consola: 
- Contexto 500 m: 
- Fuente visual adicional distinta del visor: 

### E. Observaciones visuales de Jhoreck

- MapBiomas — color natural:
- MapBiomas — falso color:
- MapBiomas — NDVI:
- MapBiomas — NDBI, si aparece:
- MapBiomas — NUACI, si aparece:
- Landsat C2 — color natural:
- Landsat C2 — falso color:
- Sentinel-2 — color natural, si aparece:
- Sentinel-2 — falso color, si aparece:
- Forma, textura, conectividad y contexto del candidato:
- ¿El patrón es uniforme en la huella?: 
- Observación integradora, sin asignar todavía veredicto:

### F. Incidencias y limitaciones

- Errores de consola o teselas:
- Capas no mostradas:
- Dificultad de interpretación:
- Otra observación:

### G. Estado del caso

- `LISTO_PARA_INTEGRAR: `
- Motivo si la respuesta es `NO`:

---

## EVAL-065

### A. Identidad esperada

- Dominio: `anillo_sistema`
- Unidad ID: `sistema|0_500`
- Unidad: Sistema disuelto 0_500
- Estrato: `E6_CAMBIO_70_13`
- Años esperados — inicio | evento | fin: `2009 | 2010 | 2014`

### B. Control previo

- [ ] El desplegable muestra `EVAL-065`.
- [ ] La unidad y el estrato coinciden.
- [ ] Los años coinciden.
- [ ] Las capas principales de MapBiomas cargaron.
- [ ] El contorno candidato se distingue de la ventana 150 × 150 m.

### C. Salida completa de la consola GEE

[INICIO_CONSOLA_GEE]

PEGAR AQUÍ TODA LA SALIDA PERTINENTE DE LA CONSOLA PARA EVAL-065.

[FIN_CONSOLA_GEE]

### D. Capas revisadas

- MapBiomas — color natural: 
- MapBiomas — falso color: 
- MapBiomas — NDVI: 
- MapBiomas — NDBI: 
- MapBiomas — NUACI: 
- Landsat C2 — color natural: 
- Landsat C2 — falso color: 
- Landsat C2 — NDVI cuantitativo en consola: 
- Sentinel-2 — color natural: 
- Sentinel-2 — falso color: 
- Sentinel-2 — NDVI cuantitativo en consola: 
- Contexto 500 m: 
- Fuente visual adicional distinta del visor: 

### E. Observaciones visuales de Jhoreck

- MapBiomas — color natural:
- MapBiomas — falso color:
- MapBiomas — NDVI:
- MapBiomas — NDBI, si aparece:
- MapBiomas — NUACI, si aparece:
- Landsat C2 — color natural:
- Landsat C2 — falso color:
- Sentinel-2 — color natural, si aparece:
- Sentinel-2 — falso color, si aparece:
- Forma, textura, conectividad y contexto del candidato:
- ¿El patrón es uniforme en la huella?: 
- Observación integradora, sin asignar todavía veredicto:

### F. Incidencias y limitaciones

- Errores de consola o teselas:
- Capas no mostradas:
- Dificultad de interpretación:
- Otra observación:

### G. Estado del caso

- `LISTO_PARA_INTEGRAR: `
- Motivo si la respuesta es `NO`:

---

## EVAL-066

### A. Identidad esperada

- Dominio: `anillo_sistema`
- Unidad ID: `sistema|0_500`
- Unidad: Sistema disuelto 0_500
- Estrato: `E1_PERSISTENTE70`
- Años esperados — inicio | evento | fin: `1985 | N/A | 2024`

### B. Control previo

- [ ] El desplegable muestra `EVAL-066`.
- [ ] La unidad y el estrato coinciden.
- [ ] Los años coinciden.
- [ ] Las capas principales de MapBiomas cargaron.
- [ ] El contorno candidato se distingue de la ventana 150 × 150 m.

### C. Salida completa de la consola GEE

[INICIO_CONSOLA_GEE]

PEGAR AQUÍ TODA LA SALIDA PERTINENTE DE LA CONSOLA PARA EVAL-066.

[FIN_CONSOLA_GEE]

### D. Capas revisadas

- MapBiomas — color natural: 
- MapBiomas — falso color: 
- MapBiomas — NDVI: 
- MapBiomas — NDBI: 
- MapBiomas — NUACI: 
- Landsat C2 — color natural: 
- Landsat C2 — falso color: 
- Landsat C2 — NDVI cuantitativo en consola: 
- Sentinel-2 — color natural: 
- Sentinel-2 — falso color: 
- Sentinel-2 — NDVI cuantitativo en consola: 
- Contexto 500 m: 
- Fuente visual adicional distinta del visor: 

### E. Observaciones visuales de Jhoreck

- MapBiomas — color natural:
- MapBiomas — falso color:
- MapBiomas — NDVI:
- MapBiomas — NDBI, si aparece:
- MapBiomas — NUACI, si aparece:
- Landsat C2 — color natural:
- Landsat C2 — falso color:
- Sentinel-2 — color natural, si aparece:
- Sentinel-2 — falso color, si aparece:
- Forma, textura, conectividad y contexto del candidato:
- ¿El patrón es uniforme en la huella?: 
- Observación integradora, sin asignar todavía veredicto:

### F. Incidencias y limitaciones

- Errores de consola o teselas:
- Capas no mostradas:
- Dificultad de interpretación:
- Otra observación:

### G. Estado del caso

- `LISTO_PARA_INTEGRAR: `
- Motivo si la respuesta es `NO`:

---

## Control final del lote

Antes de entregar el archivo:

- [ ] Están presentes las 51 secciones, de EVAL-016 a EVAL-066.
- [ ] Todas conservan su ID original.
- [ ] Cada caso incluye su salida de consola entre ambos marcadores.
- [ ] Cada capa figura como `SI`, `NO` o `NO MOSTRADA`.
- [ ] Las observaciones distinguen MapBiomas, Landsat y Sentinel-2.
- [ ] No se asignaron veredictos por intuición ni por una sola fuente.
- [ ] No se incluyeron coordenadas ni geometrías KBA restringidas.
- [ ] No se abrió la clave de repeticiones ciegas.
- [ ] Los casos incompletos quedaron marcados como `LISTO_PARA_INTEGRAR: NO`.
- [ ] El archivo final se guardó como `lote_evaluaciones_EVAL016_EVAL066_paso08D.md`.

