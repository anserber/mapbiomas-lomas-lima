# Control del Paso 8A — inventario de estratos públicos

**Fecha:** 2026-07-29  
**Estado:** PASS  
**Herramienta:** Google Earth Engine  
**Exportaciones ejecutadas:** ninguna

## Unidades

- Ámbitos ACR: 5 de 5.
- Anillos del sistema disuelto: 3 de 3.
- Unidades públicas totales: 8 de 8.

Se utilizaron los anillos del sistema disuelto para evitar duplicar superficie
por la superposición de los 15 anillos por ámbito.

## Estratos

Los seis estratos previstos estuvieron presentes:

| Estrato | Superficie única (ha) |
|---|---:|
| `E1_PERSISTENTE70` | 6512.234776 |
| `E2_URBANO_W5` | 22.490240 |
| `E3_URBANO_CENSURADO` | 66.901346 |
| `E4_INTERCAMBIO_68_70` | 4035.217008 |
| `E5_RECUPERACION_68_70` | 1061.563184 |
| `E6_CAMBIO_70_13` | 23.598817 |

Estratos vacíos: 0.

## Aclaración de la unidad

Los valores de este inventario representan **superficie única de píxeles
candidatos**. Los resultados del Paso 7 se expresaron en `ha-evento`, donde un
mismo píxel puede participar en eventos de años distintos.

Por ello, las dos tablas no deben coincidir exactamente ni utilizarse como si
tuvieran el mismo grano analítico. Esta diferencia es esperada y no constituye
un error.

El estrato `E4_INTERCAMBIO_68_70` incluye deliberadamente las rupturas
cartográficas conocidas de Ancón y Carabayllo 2. Su función en el Paso 8 es
servir como control de falsos positivos, no alimentar un indicador de pérdida
ecológica.

## Decisión

El inventario es completo y suficiente para construir la reserva pública de
candidatos. Se autoriza iniciar el Paso 8B.

