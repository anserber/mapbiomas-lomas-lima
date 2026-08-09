# Control del sistema 0–500 m, 2022–2023

**Estado:** revisado; transición MapBiomas mayormente persistente  
**Unidad:** periferia externa disuelta de 0–500 m  
**Transición:** clase 70 → clase 24  
**Periodo:** 2022–2023

## Resultado de MapBiomas

- Área 70→24 entre 2022 y 2023: **14.439724 ha**.
- Área que permaneció como clase 24 en 2024: **13.132530 ha**.
- Área que no permaneció como clase 24 en 2024: **1.307195 ha**.
- Persistencia de la señal hasta 2024: **90.947 %**.

La persistencia elevada indica que la transición no corresponde principalmente
a una oscilación anual aleatoria. Debe describirse como transición persistente
hacia la clase de infraestructura urbana de MapBiomas.

## Corroboración con Dynamic World

| Año | Probabilidad media `built` | Área con probabilidad ≥ 0.50 (ha) | Clase modal `built` (%) |
|---:|---:|---:|---:|
| 2021 | 0.096534 | 0.000000 | 0.366 |
| 2022 | 0.098032 | 0.000000 | 0.301 |
| 2023 | 0.093993 | 0.000000 | 0.033 |
| 2024 | 0.096997 | 0.004743 | 0.366 |

Dynamic World evaluó aproximadamente **14.593792 ha** debido a la
reproyección del candidato de 30 m sobre una grilla de 10 m.

## Decisión metodológica

Dynamic World no muestra un incremento temporal de su clase `built` asociado a
la transición. Esto no invalida MapBiomas, porque ambos productos emplean
definiciones, resoluciones, modelos y soportes espaciales diferentes.

En ambientes áridos y con urbanización dispersa, Dynamic World puede confundir
infraestructura, superficies acondicionadas y suelo desnudo. Por ello:

- MapBiomas permanece como fuente principal;
- la persistencia de la clase 24 se conserva como evidencia;
- Dynamic World se reporta como contraste no equivalente, no como verdad de
  terreno;
- no se utilizará Dynamic World como filtro obligatorio para aceptar o
  rechazar los demás cambios;
- el resultado se describirá como **presión o transición hacia infraestructura
  urbana según MapBiomas**, salvo que exista evidencia externa suficiente para
  una afirmación más específica.
