# Control del Paso 8B2 — selección pública congelada

**Fecha:** 2026-07-29  
**Estado:** PASS  
**Semilla:** `20260729`  
**Separación objetivo:** 150 m

## Calidad de la reserva

- Filas de la reserva principal: 861.
- Filas del complemento Carabayllo 1: 80.
- `candidate_id` únicos entre reserva y complemento: 941.
- Coordenadas duplicadas: 0.
- Valores obligatorios vacíos: 0.
- Grupos presentes: 12 de 12.
- Todos los candidatos cumplen el parche mínimo de 3 píxeles.

## Muestra pública seleccionada

- Sectores únicos: 36.
- Estratos representados: 6 de 6.
- Ámbitos ACR representados: 5 de 5.
- Separación mínima observada dentro de estrato y dominio: 175.992 m.

| Estrato | ACR | Anillo del sistema | Total |
|---|---:|---:|---:|
| `E1_PERSISTENTE70` | 3 | 3 | 6 |
| `E2_URBANO_W5` | 2 | 4 | 6 |
| `E3_URBANO_CENSURADO` | 3 | 3 | 6 |
| `E4_INTERCAMBIO_68_70` | 3 | 3 | 6 |
| `E5_RECUPERACION_68_70` | 3 | 3 | 6 |
| `E6_CAMBIO_70_13` | 3 | 3 | 6 |

## Reasignaciones

- `E2_URBANO_W5`: 1 plaza(s) de ACR reasignada(s) a anillo_sistema.

## Cobertura por unidad

| Unidad | Sectores |
|---|---:|
| `acr|amancaes` | 3 |
| `acr|ancon` | 5 |
| `acr|carabayllo_1` | 1 |
| `acr|carabayllo_2` | 3 |
| `acr|villa_maria` | 5 |
| `sistema|0_500` | 9 |
| `sistema|1000_2000` | 5 |
| `sistema|500_1000` | 5 |

## Decisión

La muestra pública cumple el tamaño, la representación de estratos y ámbitos
ACR, la unicidad y la separación espacial previstas. La única desviación es la
reasignación documentada dentro de E2; no se redujo el tamaño mínimo de parche
ni se seleccionaron dos puntos separados por menos de 150 m dentro del mismo
grupo.

El complemento E1 de Carabayllo 1 se incorporó antes de congelar la muestra y no alteró las cuotas por estrato o dominio.

La muestra pública queda congelada. Todavía no contiene sectores KBA ni repeticiones ciegas.
