// PASO 6E2-C — Dynamic World optimizado.
// Una sola reducción espacial para evitar "Too many concurrent aggregations".
// No exporta archivos ni declara pérdida ecológica automáticamente.

var ASSET_ACR =
  'projects/mapbiomas-lomas-jhoreck/assets/inputs/acr_lomas_5_ambitos_gee';
var ASSET_CLASES =
  'projects/mapbiomas-public/assets/peru/collection3/' +
  'mapbiomas_peru_collection3_integration_v1';

var acr = ee.FeatureCollection(ASSET_ACR);
var unidad = acr.filter(ee.Filter.eq('id_ambito', 'villa_maria'));
var geometria = unidad.geometry();
var contexto = geometria.buffer(1000);
var clases = ee.Image(ASSET_CLASES);

var candidato = clases.select('classification_2021').eq(70)
  .and(clases.select('classification_2022').eq(24))
  .clip(geometria);

var years = ee.List.sequence(2020, 2024);

function coleccionDW(year) {
  year = ee.Number(year);
  return ee.ImageCollection('GOOGLE/DYNAMICWORLD/V1')
    .filterBounds(contexto)
    .filterDate(
      ee.Date.fromYMD(year, 1, 1),
      ee.Date.fromYMD(year.add(1), 1, 1)
    );
}

function builtAnual(year) {
  return coleccionDW(year)
    .select('built')
    .median()
    .rename('built')
    .clip(contexto);
}

function labelAnual(year) {
  return coleccionDW(year)
    .select('label')
    .mode()
    .rename('label')
    .clip(contexto);
}

function bandasMetricas(year) {
  year = ee.Number(year);
  var sufijo = year.format('%d');
  var built = builtAnual(year);
  var label = labelAnual(year);
  var pixelHa = ee.Image.pixelArea().divide(10000);

  var observado = pixelHa
    .updateMask(candidato)
    .updateMask(built.mask())
    .rename(ee.String('observado_ha_').cat(sufijo));

  var probPonderada = pixelHa
    .multiply(built)
    .updateMask(candidato)
    .rename(ee.String('built_ponderado_ha_').cat(sufijo));

  var prob50 = pixelHa
    .updateMask(candidato)
    .updateMask(built.gte(0.50))
    .rename(ee.String('prob50_ha_').cat(sufijo));

  var labelBuilt = pixelHa
    .updateMask(candidato)
    .updateMask(label.eq(6))
    .rename(ee.String('label_built_ha_').cat(sufijo));

  return observado
    .addBands(probPonderada)
    .addBands(prob50)
    .addBands(labelBuilt);
}

var stack = bandasMetricas(2020);
stack = ee.Image(ee.List.sequence(2021, 2024).iterate(
  function(year, acumulado) {
    return ee.Image(acumulado).addBands(bandasMetricas(year));
  },
  stack
));

// ÚNICA reducción espacial del script.
var totales = stack.reduceRegion({
  reducer: ee.Reducer.sum(),
  geometry: geometria,
  crs: 'EPSG:32718',
  scale: 10,
  maxPixels: 1e9,
  tileScale: 4
});

function obtener(prefijo, year) {
  return ee.Number(totales.get(
    ee.String(prefijo).cat(ee.Number(year).format('%d'))
  ));
}

var nImagenes = years.map(function(year) {
  return coleccionDW(year).size();
});

var observadoHa = years.map(function(year) {
  return obtener('observado_ha_', year);
});

var probMedia = years.map(function(year) {
  var observado = obtener('observado_ha_', year);
  var ponderado = obtener('built_ponderado_ha_', year);
  return ee.Algorithms.If(
    observado.gt(0),
    ponderado.divide(observado),
    0
  );
});

var prob50Ha = years.map(function(year) {
  return obtener('prob50_ha_', year);
});

var prob50Pct = years.map(function(year) {
  var observado = obtener('observado_ha_', year);
  var area = obtener('prob50_ha_', year);
  return ee.Algorithms.If(
    observado.gt(0),
    area.divide(observado).multiply(100),
    0
  );
});

var labelBuiltHa = years.map(function(year) {
  return obtener('label_built_ha_', year);
});

var labelBuiltPct = years.map(function(year) {
  var observado = obtener('observado_ha_', year);
  var area = obtener('label_built_ha_', year);
  return ee.Algorithms.If(
    observado.gt(0),
    area.divide(observado).multiply(100),
    0
  );
});

// Un único objeto en Console reduce la repetición del mismo cálculo.
print('PASO 6E2-C — RESULTADO OPTIMIZADO', ee.Dictionary({
  years: years,
  n_imagenes_dw: nImagenes,
  candidato_observado_ha: observadoHa,
  built_prob_media: probMedia,
  built_prob_ge_050_ha: prob50Ha,
  built_prob_ge_050_pct: prob50Pct,
  label_built_moda_ha: labelBuiltHa,
  label_built_moda_pct: labelBuiltPct
}));

var built2021 = builtAnual(2021);
var built2022 = builtAnual(2022);
var visBuilt = {
  min: 0,
  max: 1,
  palette: ['FFFFFF', 'FFF7BC', 'FEC44F', 'D95F0E', '7F0000']
};

var candidato10 = candidato.unmask(0).reproject({
  crs: 'EPSG:32718',
  scale: 10
});
var bordeCandidato = candidato10
  .focalMax({radius: 1, units: 'pixels'})
  .neq(candidato10.focalMin({radius: 1, units: 'pixels'}))
  .selfMask();

var mapaIzquierdo = ui.Map();
var mapaDerecho = ui.Map();
mapaIzquierdo.setOptions('SATELLITE');
mapaDerecho.setOptions('SATELLITE');

mapaIzquierdo.addLayer(
  built2021, visBuilt, 'Probabilidad built — 2021', true
);
mapaDerecho.addLayer(
  built2022, visBuilt, 'Probabilidad built — 2022', true
);
mapaIzquierdo.addLayer(
  bordeCandidato, {palette: ['FF00FF']}, 'Contorno candidato', true
);
mapaDerecho.addLayer(
  bordeCandidato, {palette: ['FF00FF']}, 'Contorno candidato', true
);

var limite = unidad.style({
  color: '00FFFF',
  fillColor: '00000000',
  width: 2
});
mapaIzquierdo.addLayer(limite, {}, 'Límite ACR', true);
mapaDerecho.addLayer(limite, {}, 'Límite ACR', true);

mapaIzquierdo.add(ui.Label('Dynamic World 2021', {
  position: 'top-left',
  fontWeight: 'bold',
  fontSize: '16px',
  padding: '6px'
}));
mapaDerecho.add(ui.Label('Dynamic World 2022', {
  position: 'top-right',
  fontWeight: 'bold',
  fontSize: '16px',
  padding: '6px'
}));

var linker = ui.Map.Linker([mapaIzquierdo, mapaDerecho]);
var divisor = ui.SplitPanel({
  firstPanel: mapaIzquierdo,
  secondPanel: mapaDerecho,
  orientation: 'horizontal',
  wipe: true,
  style: {stretch: 'both'}
});

ui.root.widgets().reset([divisor]);
mapaIzquierdo.centerObject(unidad, 15);

print('No se ejecutaron exportaciones.');
