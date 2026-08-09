# Control del Paso 7C3 — destinos W5 en Carabayllo 2

**Fecha:** 2026-07-28  
**Unidad:** Lomas de Carabayllo 2  
**Periodo evaluable W5:** 1990–2020  
**Estado:** aprobado

## Controles

- Unidad procesada: 1.
- Años evaluables: 31.
- Años con eventos W5 filtrados: 14.
- Pérdida cartográfica W5 antes de interpretar destinos: 37.411829 ha-evento.
- Ruptura conocida 2014–2015 excluida: 10.733564 ha-evento.
- Diferencia entre el total y la suma de destinos: menor que `1e-14 ha`.

## Composición por destino

| Destino | Área (ha-evento) | Participación |
|---|---:|---:|
| 68 — Otra área natural sin vegetación | 33.641805 | 89.9229 % |
| 13 — Otra formación no boscosa | 3.770025 | 10.0771 % |
| 24 — Infraestructura urbana | 0.000000 | 0 % |
| Otros destinos | 0.000000 | 0 % |
| **Total** | **37.411829** | **100 %** |

Los eventos se distribuyeron en 2001–2006, 2008–2014 y 2020. En todos los
años, el destino fue exclusivamente una combinación de las clases naturales
13 y 68.

## Interpretación

El 89.9229 % corresponde al intercambio `70→68`, que se clasifica como
`INTERCAMBIO_NATURAL_68_70` y queda fuera del indicador principal de pérdida
ecológica.

El 10.0771 % restante corresponde a `70→13`. Ambas son clases naturales y,
sin evidencia espectral, visual o de campo adicional, este cambio tampoco se
denominará pérdida ecológica confirmada. Se conservará como:

```text
CAMBIO_NATURAL_70_13_PENDIENTE_VALIDACION
```

No se detectó pérdida W5 de clase 70 hacia infraestructura urbana en
Carabayllo 2.

## Decisión para el Paso 7D

1. Excluir `70→68` de pérdidas ecológicas principales.
2. Separar `70→13` como cambio natural pendiente de validación.
3. Mantener `70→24` como transición antrópica específica; en este control su
   valor fue cero.
4. No presentar las 37.411829 ha-evento como pérdida ecológica ni como
   urbanización.
5. Conservar por separado los eventos recientes censurados de 2021–2024.

## Script

```text
04_extraccion_series/01_scripts/paso07C3_destinos_w5_carabayllo2.js
```
