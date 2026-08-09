// PASO 6D1 — Verificación de la codificación de transiciones.
// Prueba si el código oficial equivale a clase_inicial * 100 + clase_final.
// No exporta datos.

var ASSET_COBERTURA =
  'projects/mapbiomas-public/assets/peru/collection3/' +
  'mapbiomas_peru_collection3_integration_v1';

var ASSET_TRANSICIONES =
  'projects/mapbiomas-public/assets/peru/collection3/' +
  'mapbiomas_peru_collection3_transitions_v1';

var ASSET_ACR =
  'projects/mapbiomas-lomas-jhoreck/assets/inputs/' +
  'acr_lomas_5_ambitos_gee';

var cobertura = ee.Image(ASSET_COBERTURA);
var transiciones = ee.Image(ASSET_TRANSICIONES);
var acr = ee.FeatureCollection(ASSET_ACR);
var geometria = acr.geometry();

var periodosControl = ee.List([
  [1985, 1986],
  [2009, 2010],
  [2023, 2024]
]);

function comprobarPeriodo(par) {
  par = ee.List(par);
  var inicio = ee.Number(par.get(0)).toInt();
  var fin = ee.Number(par.get(1)).toInt();
  var nombreBanda = ee.String('transitions_')
    .cat(inicio.format())
    .cat('_')
    .cat(fin.format());

  var claseInicial = cobertura.select(
    ee.String('classification_').cat(inicio.format())
  );
  var claseFinal = cobertura.select(
    ee.String('classification_').cat(fin.format())
  );
  var esperada = claseInicial.multiply(100).add(claseFinal).toInt16();
  var oficial = transiciones.select([nombreBanda]);
  var mascaraComun = oficial.mask().and(esperada.mask());

  var areaEvaluada = ee.Image.pixelArea()
    .updateMask(mascaraComun)
    .rename('area_evaluada_m2');
  var areaDiferente = ee.Image.pixelArea()
    .updateMask(oficial.neq(esperada).and(mascaraComun))
    .rename('area_diferente_m2');

  var areas = areaEvaluada.addBands(areaDiferente).reduceRegion({
    reducer: ee.Reducer.sum(),
    geometry: geometria,
    scale: 30,
    maxPixels: 1e9,
    tileScale: 4
  });

  var evaluada = ee.Number(areas.get('area_evaluada_m2'));
  var diferente = ee.Number(
    ee.Algorithms.If(
      ee.Algorithms.IsEqual(areas.get('area_diferente_m2'), null),
      0,
      areas.get('area_diferente_m2')
    )
  );

  return ee.Feature(null, {
    periodo: inicio.format().cat('_').cat(fin.format()),
    banda: nombreBanda,
    area_evaluada_ha: evaluada.divide(10000),
    area_diferente_ha: diferente.divide(10000),
    diferencia_pct: diferente.divide(evaluada).multiply(100),
    codificacion_coincide: diferente.eq(0)
  });
}

var controles = ee.FeatureCollection(periodosControl.map(comprobarPeriodo));

var bandaDiagnostico = transiciones.select('transitions_2023_2024');
var histograma = bandaDiagnostico.reduceRegion({
  reducer: ee.Reducer.frequencyHistogram(),
  geometry: geometria,
  scale: 30,
  maxPixels: 1e9,
  tileScale: 4
});

print('PASO 6D1 — VALIDACIÓN DE CODIFICACIÓN');
print('Fórmula probada: clase_inicial × 100 + clase_final');
print('Controles — esperado: diferencia 0 % en los tres periodos', controles);
print(
  'Periodos — orden de las listas',
  controles.aggregate_array('periodo')
);
print(
  'Área evaluada — ha',
  controles.aggregate_array('area_evaluada_ha')
);
print(
  'Área diferente — ha; esperado: [0, 0, 0]',
  controles.aggregate_array('area_diferente_ha')
);
print(
  'Diferencia — %; esperado: [0, 0, 0]',
  controles.aggregate_array('diferencia_pct')
);
print(
  'Codificación coincide — esperado: [1, 1, 1]',
  controles.aggregate_array('codificacion_coincide')
);
print('Histograma de códigos 2023–2024 dentro del ACR', histograma);

Map.centerObject(acr, 9);
Map.addLayer(
  bandaDiagnostico.clip(geometria),
  {min: 0, max: 7070},
  'Transiciones 2023–2024 — diagnóstico'
);
Map.addLayer(
  acr.style({color: '00D5FF', fillColor: '00000000', width: 2}),
  {},
  'ACR — cinco ámbitos'
);

print('PASO 6D1 FINALIZADO — no se ejecutaron exportaciones');
