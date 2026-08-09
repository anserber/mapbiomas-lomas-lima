# Cierre técnico del Paso 6

**Estado:** PASS  
**Fecha:** 2026-07-28  
**Decisión:** autorizado iniciar el Paso 7

## Productos completados

1. periodos prioritarios seleccionados;
2. transiciones de los cinco ámbitos y de sus zonas de influencia;
3. control de codificación del asset oficial;
4. controles de cobertura, persistencia y consistencia espacial;
5. controles visuales con mosaicos Landsat, Sentinel-2 y Dynamic World;
6. tipología de confianza para 45 controles.

## Resultado de la tipología

- 45 controles clasificados;
- 12 controles revisados específicamente;
- 0 transiciones urbanas pendientes;
- 0 cambios naturales pendientes;
- 0 impactos ecológicos confirmados automáticamente;
- 5 casos de final de serie conservados como provisionales;
- 22 casos dominados por ambigüedad 68↔70;
- 2 rupturas cartográficas naturales documentadas.

## Regla para los pasos siguientes

Las clases de MapBiomas representan información cartográfica modelada.
Persistencia de una transición significa estabilidad de la etiqueta, no
causalidad ni impacto ecológico demostrado.

Los análisis posteriores deben:

- mantener separados los resultados cartográficos y las inferencias
  ecológicas;
- excluir las ambigüedades y rupturas documentadas de los totales de impacto;
- conservar los cambios de 2023–2024 como provisionales por censura derecha;
- utilizar exclusivamente el nivel `sistema` para totales del sistema de
  lomas, evitando sumar anillos solapados por ámbito.

## Decisión

El Paso 6 cumple su objetivo de depurar la señal temporal y establecer qué
transiciones son defendibles. Se puede iniciar el Paso 7, dedicado a medir
consistencia, persistencia y ruido temporal de la clase 70.
