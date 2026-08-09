# Persistencia de ocho transiciones urbanas del Paso 6

**Estado:** PASS  
**Fuente principal:** MapBiomas Perú, Colección 3  
**Control espacial:** asset oficial de transiciones frente a bandas anuales

## Control de consistencia

El diagnóstico 6F1-B comprobó en un caso del sistema y otro del ACR que:

- el código 7024 del asset oficial coincide con la reconstrucción
  `clase_inicial × 100 + clase_final`;
- las áreas coinciden con el CSV consolidado;
- la diferencia espacial XOR es **0 ha**.

La versión final de 6F1 redujo los casos por periodo y por geometría. La
diferencia porcentual máxima frente a las áreas validadas fue
**0.000000759 %**, considerada residuo numérico inmaterial.

## Resultados

| Control | Unidad | Periodo | Área 70→24 (ha) | Persistencia continua hasta 2024 (%) |
|---|---|---:|---:|---:|
| CV-009 | Sistema 0–500 m | 2021–2022 | 12.932612 | 100.000 |
| CV-012 | Sistema 0–500 m | 2014–2015 | 4.158760 | 100.000 |
| CV-014 | Sistema 500–1,000 m | 2021–2022 | 2.697715 | 100.000 |
| CV-017 | Lomas de Villa María | 2022–2023 | 1.521714 | 51.746 |
| CV-018 | Lomas de Amancaes | 2021–2022 | 1.093521 | 100.000 |
| CV-023 | Lomas de Amancaes | 2019–2020 | 0.236403 | 100.000 |
| CV-024 | Lomas de Villa María | 2019–2020 | 0.204406 | 100.000 |
| CV-027 | Lomas de Amancaes | 2022–2023 | 0.144449 | 0.000 |

## Decisión

- Seis controles se clasifican como **transición urbana persistente según
  MapBiomas**.
- CV-017 se clasifica como **persistencia parcial**.
- CV-027 se clasifica como **transición no persistente** y se conserva como
  alerta metodológica.
- La persistencia temática no equivale por sí sola a impacto ecológico
  confirmado.
- Los cambios que terminan en 2024 continúan siendo provisionales porque no
  existen años posteriores en la colección.
