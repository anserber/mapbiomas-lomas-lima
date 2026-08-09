# Control del Paso 8B1 — reserva de candidatos públicos

**Fecha:** 2026-07-29  
**Estado:** PASS con limitación documentada  
**Semilla:** `20260729`  
**Parche mínimo:** 3 píxeles conectados  
**Exportación:** autorizada

## Resultado

- Grupos esperados: 12.
- Grupos obtenidos: 12.
- Candidatos totales: 861.
- Todos los grupos alcanzaron el mínimo de 3 candidatos.

| Grupo | Candidatos |
|---|---:|
| `E1_PERSISTENTE70|acr` | 80 |
| `E1_PERSISTENTE70|anillo_sistema` | 80 |
| `E2_URBANO_W5|acr` | 3 |
| `E2_URBANO_W5|anillo_sistema` | 80 |
| `E3_URBANO_CENSURADO|acr` | 80 |
| `E3_URBANO_CENSURADO|anillo_sistema` | 80 |
| `E4_INTERCAMBIO_68_70|acr` | 80 |
| `E4_INTERCAMBIO_68_70|anillo_sistema` | 80 |
| `E5_RECUPERACION_68_70|acr` | 80 |
| `E5_RECUPERACION_68_70|anillo_sistema` | 80 |
| `E6_CAMBIO_70_13|acr` | 80 |
| `E6_CAMBIO_70_13|anillo_sistema` | 58 |

## Limitación

`E2_URBANO_W5|acr` contiene exactamente tres candidatos que cumplen el parche
mínimo. En el cierre de la muestra se comprobará su separación espacial. Si no
es posible obtener tres sectores independientes, la cuota faltante se
reasignará a `E2_URBANO_W5|anillo_sistema`, conforme al protocolo, sin reducir
retroactivamente el criterio de parche.

## Decisión

La reserva pública es suficiente. Se autoriza ejecutar el Task
`paso08B1_reserva_candidatos_publicos` y continuar con el control de separación
espacial antes de congelar la muestra.
