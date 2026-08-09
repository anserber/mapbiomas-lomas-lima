# Control del Paso 7C — conciliación y sensibilidad temporal

**Fecha:** 2026-07-28  
**Unidad piloto:** cinco ámbitos del ACR Sistema de Lomas de Lima  
**Estado:** aprobado con regla metodológica obligatoria

## Controles de conciliación

- Ámbitos procesados: 5.
- Años evaluables con W3: 35.
- Eventos W3 sin respaldo del asset oficial de transiciones: 0 ha.
- Eventos W5 sin respaldo del asset oficial de transiciones: 0 ha.
- Las rupturas conocidas se excluyeron correctamente:
  - Ancón: 531.245731 ha-evento en W3;
  - Carabayllo 2: 10.733564 ha-evento en W3.

## Sensibilidad W3–W5

| Tipo | W5 robusta (ha-evento) | Adicional solo W3 (ha-evento) |
|---|---:|---:|
| Pérdida cartográfica | 2233.624751 | 177.912582 |
| Recuperación cartográfica | 656.813687 | 379.270198 |

Ancón concentra aproximadamente 96.4 % de la pérdida W5 y 94.3 % de la
recuperación W5.

## Diagnóstico focal de Ancón

Los diez años principales de pérdida W5 fueron 2002–2012, con concentración
en 2003, 2006, 2007, 2008 y 2009. Suman 2056.366576 ha-evento, equivalentes a
aproximadamente 95.5 % de toda la pérdida W5 de Ancón.

El 100 % de la superficie de cada uno de esos diez eventos tuvo destino:

```text
70 → 68
```

Los diez años principales de recuperación W5 ocurrieron principalmente entre
1990 y 1999 y sumaron 551.706224 ha-evento, aproximadamente 89.1 % de toda la
recuperación W5 de Ancón.

Entre 97.5 % y 100 % de cada evento tuvo origen:

```text
68 → 70
```

Según la leyenda oficial usada en el proyecto:

- 68: Otra área natural sin vegetación;
- 70: Loma costera.

## Decisión metodológica

El intercambio `68↔70` es una señal cartográfica entre dos clases naturales y
no se interpretará automáticamente como pérdida o recuperación ecológica.

Desde la Fase 7D:

1. la persistencia de clase 70 seguirá reportándose como estabilidad de la
   clasificación;
2. las transiciones `70→68` y `68→70` se etiquetarán como
   `INTERCAMBIO_NATURAL_68_70`;
3. estas transiciones quedarán fuera de los indicadores principales de
   pérdida y recuperación defendibles;
4. las transiciones hacia clases antrópicas se analizarán por separado;
5. los cambios entre 70 y otras clases naturales requerirán revisión visual
   antes de asignarles interpretación ecológica.

## Censura temporal

- W3: los cambios de 2023–2024 no pueden confirmarse como estables.
- W5: los cambios de 2021–2024 no pueden confirmarse como estables.
- Estos registros se conservarán como candidatos censurados, no como
  resultados consolidados.

## Scripts

```text
04_extraccion_series/01_scripts/paso07C_conciliacion_sensibilidad_acr.js
04_extraccion_series/01_scripts/paso07C2_intercambio_68_70_ancon.js
```
