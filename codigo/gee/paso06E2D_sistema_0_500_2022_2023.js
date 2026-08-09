// PASO 6E2-D — Control del sistema, periferia externa 0–500 m.
// Transición MapBiomas 70→24 entre 2022 y 2023.
// Comprueba persistencia en 2024 y corroboración Dynamic World 2021–2024.
// No exporta archivos ni declara pérdida ecológica automáticamente.

var ASSET_ANILLOS_SISTEMA =
  'projects/mapbiomas-lomas-jhoreck/assets/inputs/' +
  'anillos_sistema_periferia_externa_gee';
var ASSET_CLASES =
  'projects/mapbiomas-public/assets/peru/collection3/' +
  'mapbiomas_peru_collection3_integration_v1';

var anillos = ee.FeatureCollection(ASSET_ANILLOS_SISTEMA);
var unidad = anillos.filter(ee.Filter.eq('zona', '0_500'));
var geometria = unidad.geometry();
var contexto = geometria.buffer(1000);
var clases = ee.Image(ASSET_CLASES);

var c2022 = clases.select('classification_2022');
var c2023 = clases.select('classification_2023');
var c2024 = clases.select('classification_2024');

var candidato = c2022.eq(70)
  .and(c2023.eq(24))
  .clip(geometria);
var persiste2024 = candidato.and(c2024.eq(24));
var noPersiste2024 = candidato.and(c2024.neq(24));

var pixelHa30 = ee.Image.pixelArea().divide(10000);
var stackMapBiomas = pixelHa30
  .updateMask(candidato)
  .rename('candidato_ha')
  .addBands(
    pixelHa30.updateMask(persiste2024).rename('persiste_2024_ha')
  )
  .addBands(
    pixelHa30.updateMask(noPersiste2024).rename('no_persiste_2024_ha')
  );

var areasMapBiomas = stackMapBiomas.reduceRegion({
  reducer: ee.Reducer.sum(),
  geometry: geometria,
  scale: 30,
  maxPixels: 1e9,
  tileScale: 4
});

var years = ee.List.sequence(2021, 2024);

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

function bandasMetricasDW(year) {
  year = ee.Number(year);
  var sufijo = year.format('%d');
  var built = builtAnual(year);
  var label = labelAnual(year);
  var pixelHa10 = ee.Image.pixelArea().divide(10000);

  var observado = pixelHa10
    .updateMask(candidato)
    .updateMask(built.mask())
    .rename(ee.String('observado_ha_').cat(sufijo));

  var probPonderada = pixelHa10
    .multiply(built)
    .updateMask(candidato)
    .rename(ee.String('built_ponderado_ha_').cat(sufijo));

  var prob50 = pixelHa10
    .updateMask(candidato)
    .updateMask(built.gte(0.50))
    .rename(ee.String('prob50_ha_').cat(sufijo));

  var labelBuilt = pixelHa10
    .updateMask(candidato)
    .updateMask(label.eq(6))
    .rename(ee.String('label_built_ha_').cat(sufijo));

  return observado
    .addBands(probPonderada)
    .addBands(prob50)
    .addBands(labelBuilt);
}

var stackDW = bandasMetricasDW(2021);
stackDW = ee.Image(ee.List.sequence(2022, 2024).iterate(
  function(year, acumulado) {
    return ee.Image(acumulado).addBands(bandasMetricasDW(year));
  },
  stackDW
));

// Una sola reducción para todas las métricas de Dynamic World.
var totalesDW = stackDW.reduceRegion({
  reducer: ee.Reducer.sum(),
  geometry: geometria,
  crs: 'EPSG:32718',
  scale: 10,
  maxPixels: 1e9,
  tileScale: 4
});

function obtenerDW(prefijo, year) {
  return ee.Number(totalesDW.get(
    ee.String(prefijo).cat(ee.Number(year).format('%d'))
  ));
}

var nImagenes = years.map(function(year) {
  return coleccionDW(year).size();
});

var observadoHa = years.map(function(year) {
  return obtenerDW('observado_ha_', year);
});

var probMedia = years.map(function(year) {
  var observado = obtenerDW('observado_ha_', year);
  var ponderado = obtenerDW('built_ponderado_ha_', year);
  return ee.Algorithms.If(
    observado.gt(0),
    ponderado.divide(observado),
    0
  );
});

var prob50Ha = years.map(function(year) {
  return obtenerDW('prob50_ha_', year);
});

var prob50Pct = years.map(function(year) {
  var observado = obtenerDW('observado_ha_', year);
  var area = obtenerDW('prob50_ha_', year);
  return ee.Algorithms.If(
    observado.gt(0),
    area.divide(observado).multiply(100),
    0
  );
});

var labelBuiltHa = years.map(function(year) {
  return obtenerDW('label_built_ha_', year);
});

var labelBuiltPct = years.map(function(year) {
  var observado = obtenerDW('observado_ha_', year);
  var area = obtenerDW('label_built_ha_', year);
  return ee.Algorithms.If(
    observado.gt(0),
    area.divide(observado).multiply(100),
    0
  );
});

var candidatoHa = ee.Number(areasMapBiomas.get('candidato_ha'));
var persisteHa = ee.Number(areasMapBiomas.get('persiste_2024_ha'));
var noPersisteHa = ee.Number(areasMapBiomas.get('no_persiste_2024_ha'));

print('PASO 6E2-D — RESULTADO', ee.Dictionary({
  unidad_objetos: unidad.size(),
  area_70_24_2022_2023_ha: candidatoHa,
  area_persistente_como_24_en_2024_ha: persisteHa,
  area_no_persistente_como_24_en_2024_ha: noPersisteHa,
  persistencia_2024_pct: persisteHa.divide(candidatoHa).multiply(100),
  years_dynamic_world: years,
  n_imagenes_dw: nImagenes,
  candidato_observado_dw_ha: observadoHa,
  built_prob_media: probMedia,
  built_prob_ge_050_ha: prob50Ha,
  built_prob_ge_050_pct: prob50Pct,
  label_built_moda_ha: labelBuiltHa,
  label_built_moda_pct: labelBuiltPct
}));

var built2022 = builtAnual(2022);
var built2023 = builtAnual(2023);
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
  built2022, visBuilt, 'Probabilidad built — 2022', true
);
mapaDerecho.addLayer(
  built2023, visBuilt, 'Probabilidad built — 2023', true
);
mapaIzquierdo.addLayer(
  bordeCandidato, {palette: ['FF00FF']}, 'Contorno 70→24', true
);
mapaDerecho.addLayer(
  bordeCandidato, {palette: ['FF00FF']}, 'Contorno 70→24', true
);

var limite = unidad.style({
  color: '00FFFF',
  fillColor: '00000000',
  width: 2
});
mapaIzquierdo.addLayer(limite, {}, 'Anillo externo 0–500 m', true);
mapaDerecho.addLayer(limite, {}, 'Anillo externo 0–500 m', true);

mapaIzquierdo.add(ui.Label('Dynamic World 2022', {
  position: 'top-left',
  fontWeight: 'bold',
  fontSize: '16px',
  padding: '6px'
}));
mapaDerecho.add(ui.Label('Dynamic World 2023', {
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
mapaIzquierdo.centerObject(unidad, 11);

print('No se ejecutaron exportaciones.');
