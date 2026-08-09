# Paso 8E — Concordancia intraobservador y tratamiento de indeterminados

## 1. Regla metodológica

Las evaluaciones originales del Paso 8D se conservan sin modificaciones. Las
repeticiones ciegas se utilizan únicamente para medir consistencia
intraobservador. Los registros `INDETERMINADO` no se convierten en desacuerdos
ni se fuerzan a una clase cuando la evidencia es insuficiente.

## 2. Repeticiones ciegas

| Evaluación original | Repetición ciega | Veredicto | Proceso observado | Confianza | Evidencia suficiente |
|---|---|---|---|---|---|
| EVAL-041 | EVAL-010 | ACUERDO | RECUPERACION_A_70 | MEDIA | SI |
| EVAL-020 | EVAL-030 | ACUERDO | PERSISTENCIA_70 | ALTA | SI |
| EVAL-015 | EVAL-039 | ACUERDO | CONVERSION_A_URBANO | MEDIA | SI |
| EVAL-016 | EVAL-040 | DESACUERDO | OTRO_CAMBIO | MEDIA | SI |
| EVAL-032 | EVAL-049 | ACUERDO | CONVERSION_A_URBANO | MEDIA | SI |
| EVAL-004 | EVAL-060 | ACUERDO | INTERCAMBIO_70_68 | MEDIA | SI |

### Resultado

- Pares evaluados: **6**.
- Concordancia exacta del veredicto: **6/6 (100 %)**.
- Concordancia exacta del proceso observado: **6/6 (100 %)**.
- Concordancia exacta de la confianza: **6/6 (100 %)**.
- Concordancia exacta de suficiencia de evidencia: **6/6 (100 %)**.

Este resultado demuestra consistencia interna en la muestra de repetición, pero
debe reportarse junto con el tamaño reducido de la prueba (`n = 6`) y no como
una estimación universal de exactitud.

## 3. Registros indeterminados

Los seis registros indeterminados son:

`EVAL-033`, `EVAL-036`, `EVAL-038`, `EVAL-042`, `EVAL-045` y `EVAL-050`.

Ninguno es una repetición ciega. Su tratamiento será:

1. conservarlos en la base completa de 66 evaluaciones;
2. reportarlos como `INDETERMINADO` y confianza `BAJA`;
3. excluirlos del denominador de concordancia temática evaluable;
4. informar su cantidad y causa por separado;
5. no contarlos automáticamente como `DESACUERDO`.

### Causas principales

- **EVAL-033:** ausencia de información MapBiomas utilizable para el año inicial
  2017 en el visor; las fuentes auxiliares no sustituyen la evidencia principal.
- **EVAL-036:** señales temporales contradictorias, sin una interpretación
  homogénea defendible.
- **EVAL-038, EVAL-042, EVAL-045 y EVAL-050:** eventos recientes censurados a la
  derecha (`2023 → 2024`, con 2024 también como fin observado) cuya evidencia no
  permitió confirmar un patrón homogéneo. La repetición de 2024 no es por sí
  sola la causa del veredicto, pero limita la comprobación de persistencia en un
  año posterior independiente.

## 4. Decisión de avance

El Paso 8E queda metodológicamente habilitado: la consistencia de las
repeticiones fue comprobada y los indeterminados tienen una regla explícita de
tratamiento. El siguiente subpaso es calcular la matriz de resultados y los
porcentajes usando dos denominadores claramente separados:

- **base total:** 66 evaluaciones;
- **base evaluable:** 60 evaluaciones, excluyendo los 6 indeterminados.
