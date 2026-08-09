# Control del Paso 7D2 — resultados finales de anillos

**Fecha:** 2026-07-28  
**Estado:** PASS  
**Producto:** `paso07D2_resultados_finales_anillos_periferia_externa_1985_2024.csv`

## Alcance

El producto utiliza exclusivamente los anillos corregidos de periferia externa:

- 15 anillos por ámbito: cinco ámbitos por tres distancias;
- 3 anillos del sistema disuelto;
- exclusión del interior del ACR;
- exclusión del enclave rectangular de SEDAPAL en Carabayllo 2.

Los tres anillos del sistema disuelto son la fuente válida para calcular
totales. Los 15 anillos por ámbito se conservan para comparaciones y no deben
sumarse porque existen superposiciones entre ámbitos.

## Validación del archivo descargado

- Filas: 18.
- Columnas: 45, incluidos `system:index` y `.geo`.
- Unidades únicas: 18.
- Duplicados de `unidad_id`: 0.
- Anillos por ámbito: 15.
- Anillos del sistema disuelto: 3.
- Zonas presentes: `0_500`, `500_1000` y `1000_2000`.
- Combinaciones esperadas `id_ambito × zona`: 15 de 15.
- Campos obligatorios vacíos: 0.
- Valores numéricos negativos inesperados: 0.
- Periodo uniforme: `1985–2024`.
- Método principal uniforme: `W5`.

El campo `.geo` contiene geometrías vacías porque la tabla final fue exportada
sin geometría. Esto es esperado y no afecta los indicadores.

## Conciliaciones independientes

- Diferencia máxima entre pérdida W5 y suma de destinos:
  `2.8422e-14 ha`.
- Diferencia máxima entre recuperación W5 y suma de orígenes:
  `2.8422e-14 ha`.
- Diferencia máxima entre candidatos censurados y suma de destinos:
  `1.4211e-14 ha`.
- Diferencia máxima entre área vectorial y grilla de 30 m:
  `0.06485 %` en los 18 registros.

Los residuos son numéricamente irrelevantes.

## Resultados de control del sistema disuelto

| Zona | Área de referencia (ha) | Urbano W5 (ha-evento) | Urbano censurado 2021–2024 (ha-evento) | Intercambio 70→68 W5 (ha-evento) |
|---|---:|---:|---:|---:|
| 0–500 m | 5265.400521 | 15.173571 | 31.349853 | 474.355542 |
| 500–1000 m | 5519.222634 | 5.085425 | 9.092468 | 295.835110 |
| 1000–2000 m | 12074.582794 | 1.574035 | 4.439825 | 537.258129 |

Totales válidos del sistema disuelto:

- urbano robusto W5: `21.833030 ha-evento`;
- candidato urbano censurado 2021–2024: `44.882147 ha-evento`.

La señal urbana robusta y la señal censurada reciente se concentran en el
primer anillo y disminuyen con la distancia. Este patrón es descriptivo; no
demuestra por sí solo causalidad ni pérdida ecológica observada en campo.

Los valores altos de `70→68` se mantienen separados como intercambio entre
clases naturales/cartográficas y no se reportarán automáticamente como pérdida
ecológica.

## Decisión

El archivo queda habilitado como producto final de los anillos de periferia
externa. El Paso 7D2 está aprobado. Permanece pendiente el flujo temporal local
de la KBA Lomas de Atocongo antes de declarar completamente cerrado el Paso 7.

## Ruta

```text
05_analisis_temporal/02_final/
paso07D2_resultados_finales_anillos_periferia_externa_1985_2024.csv
```
