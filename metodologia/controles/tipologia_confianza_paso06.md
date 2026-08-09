# Tipología de confianza del Paso 6

**Estado:** PASS  
**Fecha:** 2026-07-28T18:23:14-05:00  
**Controles clasificados:** 45  
**Controles revisados manualmente:** 12  

## Conteo por tipología

| Código | Registros |
|---|---:|
| AMBIGUEDAD_68_70 | 22 |
| BALANCE_MULTIANUAL | 6 |
| FINAL_SERIE | 5 |
| RUPTURA_70_13_68 | 1 |
| RUPTURA_70_68 | 1 |
| TU_NO_PERSISTENTE_MB | 1 |
| TU_PERSISTENCIA_PARCIAL_MB | 1 |
| TU_PERSISTENTE_MB | 8 |

## Reglas de uso

- Los balances multianuales describen diferencias acumuladas, no eventos.
- Los cambios que terminan en 2024 son provisionales por censura derecha.
- El intercambio dominante 68↔70 no se suma como pérdida ecológica.
- La transición 70→24 se denomina transición hacia infraestructura urbana según MapBiomas.
- Ningún control se declara automáticamente impacto ecológico confirmado.

## Controles manuales que anclan la tipología

- Villa María 2021–2022: transición urbana MapBiomas persistente al 100 %.
- Sistema 0–500 m 2022–2023: transición urbana MapBiomas persistente al 90.947 %.
- Ancón 2000–2001: probable ruptura estable entre clases 70 y 68.
- Carabayllo 2 2014–2015: ruptura estable de clase 70 hacia clases 13 y 68, sin descenso equivalente del NDVI.
- 6F1 revisó conjuntamente otras ocho transiciones urbanas.
- Seis persistieron al 100 %, una al 51.746 % y una al 0 %.

## Producto

`05_analisis_temporal/02_final/tipologia_confianza_controles_paso06.csv`
