# Control del Paso 8C — cierre de muestra

**Fecha:** 2026-07-29  
**Estado:** PASS  
**Semilla:** `20260729`

## Muestra congelada

- Sectores públicos únicos: 36.
- Sectores KBA restringidos únicos: 24.
- Sectores únicos totales: 60.
- Repeticiones ciegas: 6.
- Evaluaciones totales: 66.
- Estratos representados: 6 de 6.
- Una repetición ciega por estrato.
- Repeticiones públicas: 3.
- Repeticiones KBA: 3.
- Separación mínima en el orden entre original y repetición: 10 evaluaciones.

## Blindaje

El instrumento operativo no contiene `id_sector_unico` ni el indicador `es_repeticion_ciega`. La clave permanece en la carpeta restringida y no debe abrirse durante la evaluación.

El manifiesto compartible omite las coordenadas de los 24 sectores KBA.

## Regla de uso

No reemplazar sectores después de observar las imágenes. Los casos con evidencia insuficiente deben conservarse como `INDETERMINADO`.
