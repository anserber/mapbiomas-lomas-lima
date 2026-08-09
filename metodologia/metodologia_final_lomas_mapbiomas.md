# Metodología final — Persistencia cartográfica y presión urbana

## 1. Diseño

Estudio observacional, retrospectivo, espacial y temporal. La unidad de
información es el píxel MapBiomas de aproximadamente 30 m y la unidad de
reporte es el ámbito territorial o el anillo externo disuelto.

## 2. Ámbito espacial

### 2.1 Núcleo

Cinco ámbitos oficiales del ACR Sistema de Lomas de Lima:

- Lomas de Amancaes;
- Lomas de Ancón;
- Lomas de Carabayllo 1;
- Lomas de Carabayllo 2;
- Lomas de Villa María.

### 2.2 Periferia

Tres anillos terrestres externos, disjuntos y disueltos para todo el sistema:

- 0–500 m;
- 500–1,000 m;
- 1,000–2,000 m.

Los 15 anillos por ámbito se conservan para diagnóstico local. No se suman
entre sí porque pueden solaparse. Los totales del sistema usan únicamente los
tres anillos disueltos. El enclave SEDAPAL de Carabayllo 2 se representa como
exclusión interna y no como periferia externa.

### 2.3 KBA Atocongo

Se utiliza como contexto internacional y dominio restringido de control. No se
publican geometría, coordenadas, tablas detalladas ni derivados que permitan
reconstruir los datos licenciados. Los resultados públicos no dependen de su
redistribución.

## 3. Insumo principal

### 3.1 MapBiomas Perú Colección 3

- Integración anual: `projects/mapbiomas-public/assets/peru/collection3/mapbiomas_peru_collection3_integration_v1`.
- Transiciones: `projects/mapbiomas-public/assets/peru/collection3/mapbiomas_peru_collection3_transitions_v1`.
- Periodo anual: 1985–2024.
- Resolución nominal: 30 m.
- Clase focal natural: `70 — Loma costera`, producto beta.
- Clase focal antrópica: `24 — Infraestructura urbana`.

También se utilizan los mosaicos oficiales de apoyo para color natural, falso
color e índices espectrales. Landsat Collection 2 y Sentinel-2 se emplean solo
como evidencia auxiliar independiente; no reemplazan ni recalculan la
clasificación y las superficies MapBiomas.

## 4. Preparación y control espacial

1. Conservar las fuentes originales sin sobrescribirlas.
2. Validar geometrías y normalizarlas a multipolígonos.
3. Usar EPSG:32718 para áreas y distancias, y EPSG:4326 para intercambio con
   GEE.
4. Verificar áreas vectoriales frente a los valores oficiales.
5. Construir anillos externos disjuntos, recortarlos a tierra y excluir el ACR
   y el enclave documentado.
6. Auditar objetos, identificadores, áreas y solapamientos antes de extraer
   píxeles.

## 5. Indicadores de estado de la clase 70

Para cada píxel `x` y año `t` se define `I70(x,t)=1` cuando el píxel pertenece
a la clase 70 y `0` en caso contrario.

- **Frecuencia:** suma de `I70` durante los 40 años.
- **Racha máxima:** mayor número de años consecutivos en clase 70.
- **Alguna vez 70:** píxeles con frecuencia mayor que cero.
- **Siempre 70:** píxeles con frecuencia igual a 40.
- **Ruido aislado:** reversiones de un solo año identificadas por la secuencia
  temporal; se reportan como control, no como cambio territorial.

La persistencia es un indicador cartográfico de permanencia de la clase, no
una medición directa de integridad o calidad ecológica.

## 6. Eventos temporales

### 6.1 Regla principal W5

Un evento estable W5 comienza cuando un píxel sale de la clase 70 hacia una
clase de destino y permanece en ella durante el año del evento y cuatro años
posteriores. El periodo con ventana completa es 1990–2020.

La métrica `ha-evento` suma superficie por evento temporal. No equivale
necesariamente a superficie única cuando un mismo píxel presenta más de un
evento en años diferentes.

### 6.2 Presión urbana estable

La variable principal de presión es la superficie W5 `70→24`. Debe reportarse:

- en hectáreas-evento;
- por unidad territorial;
- normalizada por 1,000 ha de superficie de la unidad cuando se comparen
  ámbitos de tamaños diferentes.

### 6.3 Eventos recientes censurados

Las transiciones `70→24` iniciadas en 2021–2023 no pueden completar cinco años
antes de 2024. Se reportan como **vigilancia reciente censurada**, nunca se
suman a la presión W5 confirmada.

### 6.4 Intercambios naturales y rupturas conocidas

Los intercambios `68↔70` son señales cartográficas entre clases naturales. No
se denominan pérdida ni recuperación ecológica. Se excluyen de los totales de
pérdida las rupturas conocidas:

- Ancón 2000–2001: aproximadamente 532.735 ha `70→68`;
- Carabayllo 2 2014–2015: aproximadamente 10.734 ha `70→13/68`.

Estas rupturas son discontinuidades cartográficas documentadas, no errores en
la geometría oficial del ACR.

## 7. Validación visual ciega

Se diseñó una muestra estratificada de 66 evaluaciones ciegas, equivalentes a
60 sectores únicos, con seis repeticiones para controlar consistencia
intraevaluador. Se compararon mosaicos MapBiomas, color natural, falso color,
NDVI y, cuando correspondía, Landsat C2 y Sentinel-2 como fuentes auxiliares.

Resultados:

- 60 evaluaciones con decisión: 43 acuerdos y 17 desacuerdos;
- concordancia descriptiva: 71.7 %;
- 6 indeterminadas, excluidas del denominador evaluable;
- 6 de 6 repeticiones con veredicto idéntico;
- confianza global: MEDIA;
- E1 Persistente 70 y E2 Urbano W5: ALTA;
- E3 Urbano censurado y E4 Intercambio `68↔70`: MEDIA;
- E5 Recuperación `68→70` y E6 Cambio `70→13`: BAJA.

La muestra fue estratificada y dirigida a señales candidatas. Por ello, el
71.7 % es concordancia de la muestra evaluable y no exactitud temática oficial
ni estimación probabilística para todo el paisaje.

## 8. Productos complementarios

- **MapBiomas Fuego:** descartado del núcleo; señal nula en las ocho unidades
  públicas durante 2013–2024.
- **Vegetación Secundaria:** descartada; señal W5 nula.
- **Pérdida de Vegetación reconstruida:** contexto de sensibilidad, no producto
  oficial independiente ni superficie adicional. En 2001–2020 reconstruyó
  34.457 ha W5, de las cuales 18.453 ha se solaparon con el núcleo.
- **MapBiomas Agua y Alerta:** no incorporados porque no responden de manera
  directa a la pregunta cerrada.

## 9. Regla de interpretación y priorización

No se construirá por ahora un índice ponderado único. Se utilizarán cuatro
salidas transparentes:

1. **Referencia cartográfica:** superficie siempre clase 70.
2. **Vigilancia confirmada:** eventos estables W5 `70→24` respaldados por E2.
3. **Vigilancia reciente:** eventos censurados `70→24` respaldados por E3 y
   pendientes de confirmación en futuras colecciones.
4. **Revisión de incertidumbre:** `68↔70`, rupturas conocidas y señales con
   confianza baja.

Una unidad no será denominada prioritaria para restauración solo por una
transición de clase. Las recomendaciones se expresarán como vigilancia,
verificación de campo o revisión cartográfica.

## 10. Reproducibilidad

- QGIS: geometrías, áreas, anillos y control visual local.
- GEE: assets, series anuales, transiciones, persistencia y exportaciones.
- Python: conciliación de CSV, validaciones, tablas, gráficos y automatización.
- GitHub: código, documentación y productos públicos sin datos KBA
  restringidos.

R y Google Colab son opcionales; no se introducirán si duplican una tarea ya
resuelta. El repositorio debe excluir datos KBA, temporales, descargas pesadas,
credenciales y productos sujetos a restricciones.

## 11. Análisis diferido

No se entrenará un modelo ni se producirá una proyección 2050 en esta versión.
Para autorizar esa extensión se necesitarán:

1. una variable objetivo validada e interpretable;
2. suficientes ejemplos positivos y negativos independientes;
3. predictores temporales y futuros defendibles;
4. partición espacial para evitar fuga de información;
5. calibración, incertidumbre y validación fuera de muestra.

