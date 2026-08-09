# Auditoría de integración — Paso 8D

## Alcance

- Lote revisado: `EVAL-016` a `EVAL-066`.
- Registros del lote: **51**.
- Registros totales del libro consolidado: **66**.
- Archivo fuente archivado: `06_validacion_visual/01_intermediate/00_raw/lote_evaluaciones_EVAL016_EVAL066_paso08D.md`.
- SHA-256 del lote: `51f6c0815191b33d0ae581f757095ced506b01ee0ab18d21ba94d5206043b8fd`.
- Libro consolidado: `outputs/019f9a3f-8f76-7331-9999-224e79161647/ficha_evaluacion_visual_ciega_paso08_completa_66.xlsx`.

## Controles superados

- 66 identificadores únicos y consecutivos, desde `EVAL-001` hasta `EVAL-066`.
- 0 identificadores ausentes y 0 duplicados.
- 66 filas con `estado_fila = COMPLETO`.
- 0 campos obligatorios vacíos.
- 0 valores fuera de los vocabularios permitidos.
- 0 errores de fórmula detectados.
- Regla de evidencia insuficiente verificada: `NO` implica `INDETERMINADO`, `NO_DETERMINABLE` y confianza `BAJA`.
- Hoja `CONTROL`: 66 completas, 0 en revisión, 0 incompletas y 0 pendientes.

## Distribución de resultados

### Evidencia

- `SI`: 60.
- `NO`: 6.

### Veredicto visual

- `ACUERDO`: 43.
- `DESACUERDO`: 17.
- `INDETERMINADO`: 6.

### Proceso observado

- `CONVERSION_A_URBANO`: 18.
- `OTRO_CAMBIO`: 17.
- `PERSISTENCIA_70`: 11.
- `INTERCAMBIO_70_68`: 8.
- `RECUPERACION_A_70`: 3.
- `CAMBIO_70_13`: 3.
- `NO_DETERMINABLE`: 6.

### Confianza

- `ALTA`: 11.
- `MEDIA`: 48.
- `BAJA`: 7.

## Casos indeterminados

Los seis casos cerrados como indeterminados son `EVAL-033`, `EVAL-036`, `EVAL-038`, `EVAL-042`, `EVAL-045` y `EVAL-050`.

- `EVAL-036` se clasificó como evidencia insuficiente por conflicto entre señales temporales.
- Los otros cinco quedaron como evidencia insuficiente porque el registro aportado no permitía sostener un veredicto visual homogéneo con el protocolo.

No se forzó una clasificación para completar artificialmente la tabla.

## Restricciones y siguiente punto de control

- La información KBA restringida permanece separada y no debe incorporarse a productos públicos ni al repositorio abierto.
- **No se abrió ni consultó la clave de repeticiones ciegas.**
- El Paso 8D está completo. Antes del Paso 8E debe realizarse una pausa explícita y, con autorización del usuario, abrir la clave para medir concordancia intraobservador y reconciliar las repeticiones.
