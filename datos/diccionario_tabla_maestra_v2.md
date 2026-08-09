# Diccionario — tabla maestra de resultados públicos, versión 2

**Archivo:** `tabla_maestra_resultados_publicos_v2.csv`
**Fecha:** 2026-08-05
**Sustituye a:** `tabla_maestra_resultados_publicos.csv` (v1) y su diccionario
**Sustento de los cambios:** `08_cierre_metodologico/02_final/adenda_metodologica_v1.1_ruptura_1985.md`

La versión 1 no se sobrescribe y se conserva como registro histórico.

## Campos

| Campo | Definición | Unidad / escala |
|---|---|---|
| `unidad_id` | Identificador estable de la unidad espacial. | Texto |
| `dominio` | Tipo de unidad: ACR o anillo del sistema. | Categoría |
| `nombre` | Nombre legible de la unidad. | Texto |
| `subunidad` | Ámbito o intervalo de distancia. | Texto |
| `area_ref_vectorial_ha` | Superficie del polígono, calculada en EPSG:32718. | ha |
| `area_grilla_ha` | Superficie de los píxeles MapBiomas dentro de la unidad. **Denominador de todas las tasas publicadas.** | ha |
| `area_clasificada_ha` | Superficie de grilla con clase asignada, es decir grilla menos píxeles sin dato. | ha |
| `sin_dato_ha` | `area_grilla_ha` menos `area_clasificada_ha`. Es 0.000 en los cinco ámbitos del ACR. | ha |
| `area_70_1986_ha` | Superficie clasificada como clase 70 en 1986. **Línea base del estudio.** | ha |
| `area_70_1986_pct` | Proporción de la grilla clasificada como 70 en 1986. CSV 0–1. | Proporción |
| `area_70_2024_ha` | Superficie clasificada como clase 70 en 2024. | ha |
| `area_70_2024_pct` | Proporción de la grilla clasificada como 70 en 2024. CSV 0–1. | Proporción |
| `area_siempre70_ha` | Superficie que permaneció en clase 70 durante los 40 años, 1985–2024. | ha |
| `area_siempre70_pct` | Proporción de la grilla siempre clasificada como 70. CSV 0–1. | Proporción |
| `siempre70_delta_por_excluir_1985_ha` | Variación de `area_siempre70_ha` al pasar a la ventana 1986–2024. Es **0.000 en las ocho unidades**. Campo de control de robustez. | ha |
| `area_alguna_vez70_1986_2024_ha` | **Valor primario.** Superficie clasificada como 70 al menos una vez entre 1986 y 2024. | ha |
| `area_alguna_vez70_1986_2024_pct` | Proporción de la grilla correspondiente. CSV 0–1. | Proporción |
| `area_alguna_vez70_1985_2024_ha` | **Sensibilidad.** El mismo indicador con ventana de 40 años, incluyendo 1985. | ha |
| `ruido_aislado_ha` | Superficie con reversiones aisladas identificadas como ruido temporal potencial. | ha |
| `ruido_pct_alguna_vez70` | Ruido aislado respecto de la superficie alguna vez clase 70. | % 0–100 |
| `w5_loss_total_ha_evento` | Pérdida estable W5 filtrada de rupturas cartográficas conocidas. | ha-evento |
| `w5_urbano_ha_evento` | Transición estable W5 desde clase 70 hacia infraestructura urbana, clase 24. | ha-evento |
| `censura_urbano_2021_2024_ha_evento` | Candidatos recientes 70→24 sin ventana futura suficiente para confirmar W5. | ha-evento |
| `tasa_w5_urbano_por_1000ha` | Presión urbana estable W5 normalizada por 1 000 ha de grilla. | ha-evento / 1 000 ha |
| `tasa_censura_urbano_por_1000ha` | Candidatos urbanos recientes censurados, normalizados por 1 000 ha de grilla. | ha-evento / 1 000 ha |
| `ruptura_conocida_ha` | Cambio estable documentado como ruptura cartográfica entre clases, excluido de la pérdida interpretada. | ha |
| `fuego_2013_2024_ha` | Área quemada alguna vez según MapBiomas Fuego en el periodo disponible. | ha |
| `rol_interpretativo` | Función metodológica de la unidad en el diagnóstico. | Texto |

## Cambios respecto de la versión 1

### Campos añadidos

- `area_ref_vectorial_ha`, `area_clasificada_ha`, `sin_dato_ha`: declaran de
  forma explícita las **tres definiciones de superficie** presentes en los datos
  del proyecto. La versión 1 publicaba solo la de grilla, mientras el dictamen
  del Paso 10 empleaba la vectorial sin declararlo.
- `area_70_1986_ha` y `area_70_1986_pct`: línea base del estudio, tras excluir
  1985 por ruptura de inicio de serie.
- `area_alguna_vez70_1986_2024_ha` y su porcentaje: valor primario del
  indicador con la ventana corregida.
- `siempre70_delta_por_excluir_1985_ha`: campo de control que documenta la
  robustez del indicador de persistencia.

### Campos renombrados

- `area_alguna_vez70_ha` pasa a `area_alguna_vez70_1985_2024_ha` y cambia de
  valor primario a análisis de sensibilidad.

### Campo retirado

- **`tasa_presion_urbana_indicativa_por_1000ha`.** Era la suma aritmética de
  `tasa_w5_urbano_por_1000ha` y `tasa_censura_urbano_por_1000ha`.

  Motivo de la retirada: las dos señales tienen estatus epistémico y niveles de
  confianza distintos —E2 con confianza ALTA y E3 con confianza MEDIA—, por lo
  que no deben sumarse ni presentarse como una única medida de presión urbana.
  En Lomas de Amancaes el valor era de 24.547 frente a 1.186 de presión W5
  confirmada, con el 95 % del total procedente de señal censurada.

  La retirada no elimina información: la suma es reproducible a partir de las
  dos columnas que permanecen publicadas. La versión 1 conserva el registro.

## Notas de uso

1. Las métricas de porcentaje no deben mezclarse: los campos `*_pct` de
   composición se guardan como proporciones de 0 a 1 en el CSV;
   `ruido_pct_alguna_vez70` está expresado en porcentaje de 0 a 100.
2. Los campos `ha-evento` no deben sumarse entre sí ni describirse como
   hectáreas físicas únicas perdidas.
3. **La señal W5 confirmada y la señal reciente censurada no deben sumarse ni
   presentarse como una única medida de presión urbana.**
4. **El año 1985 no debe emplearse como referencia de ningún cálculo de cambio.**
   Es una ruptura cartográfica de inicio de serie documentada en
   `05_analisis_temporal/evidencia/dictamen_ruptura_1985_y_regimenes_sensor.md`.
5. **El régimen III (2014–2022) presenta la menor volatilidad medida.** En
   comparación con este régimen, el régimen I es 3,3 veces más volátil y el
   régimen II cerca de 12 veces más volátil. Los años 2023–2024 se analizan por
   separado debido al cambio de versión del mosaico.
6. Todas las tasas emplean `area_grilla_ha` como denominador.
7. La KBA Lomas de Atocongo no aparece en esta tabla porque sus datos espaciales
   tienen condiciones de uso restringidas.
8. `area_siempre70_ha` conserva la ventana de 40 años porque se demostró que el
   indicador es insensible a la exclusión de 1985: el campo
   `siempre70_delta_por_excluir_1985_ha` vale 0.000 en las ocho unidades.
