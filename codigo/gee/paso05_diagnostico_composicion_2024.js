// PASO 5C — Diagnóstico de composición completa en 2024
// Prioridad: Lomas de Ancón.
// Este script no ejecuta exportaciones.

var ACR_ASSET =
    'projects/mapbiomas-lomas-jhoreck/assets/inputs/acr_lomas_5_ambitos_gee';

var MAPBIOMAS_ASSET =
    'projects/mapbiomas-public/assets/peru/collection3/' +
    'mapbiomas_peru_collection3_integration_v1';

var acr = ee.FeatureCollection(ACR_ASSET);
var mapbiomas = ee.Image(MAPBIOMAS_ASSET);
var classification =
    mapbiomas.select('classification_2024').rename('class_id').unmask(0);
var pixelAreaHa = ee.Image.pixelArea().divide(10000).rename('area_ha');
var nativeProjection = classification.projection();

var grouped = pixelAreaHa
    .addBands(classification)
    .reduceRegions({
      collection: acr,
      reducer: ee.Reducer.sum().group({
        groupField: 1,
        groupName: 'class_id'
      }),
      scale: 30,
      crs: nativeProjection,
      tileScale: 4
    })
    .sort('id_ambito');

print('PASO 5C — COMPOSICIÓN COMPLETA 2024');
print('Ámbitos — orden de las listas', grouped.aggregate_array('id_ambito'));
print('Grupos de clases — cinco ámbitos', grouped.aggregate_array('groups'));

var ancon = ee.Feature(
    grouped.filter(ee.Filter.eq('id_ambito', 'ancon')).first()
);
var groupsAncon = ee.List(ancon.get('groups'));
var clasesAncon = groupsAncon.map(function(item) {
  return ee.Dictionary(item).get('class_id');
});
var areasAncon = groupsAncon.map(function(item) {
  return ee.Dictionary(item).get('sum');
});
var totalAncon = ee.Number(areasAncon.reduce(ee.Reducer.sum()));
var porcentajesAncon = areasAncon.map(function(area) {
  return ee.Number(area).divide(totalAncon).multiply(100);
});

print('ANCÓN 2024 — códigos de clase', clasesAncon);
print('ANCÓN 2024 — áreas por clase, ha', areasAncon);
print('ANCÓN 2024 — porcentajes por clase', porcentajesAncon);
print('ANCÓN 2024 — suma de píxeles, ha', totalAncon);
print('ANCÓN — superficie oficial de referencia, ha', ancon.get('Area_Ha'));

var loma = pixelAreaHa
    .updateMask(classification.eq(70))
    .reduceRegions({
      collection: acr,
      reducer: ee.Reducer.sum(),
      scale: 30,
      crs: nativeProjection,
      tileScale: 4
    })
    .sort('id_ambito');

var urbano = pixelAreaHa
    .updateMask(classification.eq(24))
    .reduceRegions({
      collection: acr,
      reducer: ee.Reducer.sum(),
      scale: 30,
      crs: nativeProjection,
      tileScale: 4
    })
    .sort('id_ambito');

print('Orden para clase 70', loma.aggregate_array('id_ambito'));
print('Clase 70 — área 2024, ha', loma.aggregate_array('sum'));
print('Orden para clase 24', urbano.aggregate_array('id_ambito'));
print('Clase 24 — área 2024, ha', urbano.aggregate_array('sum'));

Map.centerObject(acr, 10);
Map.addLayer(
    classification.eq(70).selfMask(),
    {palette: ['FFD700']},
    'Clase 70 — Loma 2024'
);
Map.addLayer(
    classification.eq(24).selfMask(),
    {palette: ['E31A1C']},
    'Clase 24 — Urbano 2024'
);
Map.addLayer(
    acr.style({
      color: '00FFFF',
      fillColor: '00000000',
      width: 3
    }),
    {},
    'ACR — cinco ámbitos'
);

print('DIAGNÓSTICO FINALIZADO — no se ejecutaron exportaciones');
