// PASO 6E2-C — Control independiente con Dynamic World.
// Evalúa si la señal 70→24 de Villa María ya parecía construida en 2021
// o si la probabilidad de superficie construida aumentó y persistió después.
// MapBiomas sigue siendo la fuente principal; Dynamic World es corroboración.
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

function compuestoBuilt(year) {
  return coleccionDW(year)
    .select('built')
    .median()
    .rename('built_prob')
    .clip(contexto);
}

function compuestoLabel(year) {
  return coleccionDW(year)
    .select('label')
    .mode()
    .rename('label_mode')
    .clip(contexto);
}

function valorSeguro(diccionario, clave) {
  return ee.Number(ee.Algorithms.If(
    diccionario.contains(clave),
    diccionario.get(clave),
    0
  ));
}

function areaHa10(mask, proyeccion) {
  var resultado = ee.Image.pixelArea()
    .divide(10000)
    .updateMask(mask)
    .reduceRegion({
      reducer: ee.Reducer.sum(),
      geometry: geometria,
      crs: proyeccion,
      scale: 10,
      maxPixels: 1e9,
      tileScale: 4
    });
  return valorSeguro(resultado, 'area');
}

function resumirYear(year) {
  year = ee.Number(year);
  var built = compuestoBuilt(year);
  var label = compuestoLabel(year);
  var proyeccion = built.projection();
  var candidatoEnGrilla = candidato.updateMask(built.mask());

  var mediaDic = built
    .updateMask(candidato)
    .reduceRegion({
      reducer: ee.Reducer.mean(),
      geometry: geometria,
      crs: proyeccion,
      scale: 10,
      maxPixels: 1e9,
      tileScale: 4
    });

  var areaCandidato = areaHa10(candidatoEnGrilla, proyeccion);
  var areaProb50 = areaHa10(
    built.gte(0.50).and(candidatoEnGrilla),
    proyeccion
  );
  var areaLabelBuilt = areaHa10(
    label.eq(6).and(candidatoEnGrilla),
    proyeccion
  );

  return ee.Feature(null, {
    year: year,
    n_imagenes_dw: coleccionDW(year).size(),
    candidato_observado_ha: areaCandidato,
    built_prob_media: valorSeguro(mediaDic, 'built_prob'),
    built_prob_ge_050_ha: areaProb50,
    built_prob_ge_050_pct: ee.Algorithms.If(
      areaCandidato.gt(0),
      areaProb50.divide(areaCandidato).multiply(100),
      0
    ),
    label_built_moda_ha: areaLabelBuilt,
    label_built_moda_pct: ee.Algorithms.If(
      areaCandidato.gt(0),
      areaLabelBuilt.divide(areaCandidato).multiply(100),
      0
    )
  });
}

var resumen = ee.FeatureCollection(years.map(resumirYear))
  .sort('year');

print('PASO 6E2-C — CONTROL INDEPENDIENTE DYNAMIC WORLD');
print('Unidad — esperado: 1 objeto', unidad.size());
print('Resumen anual 2020–2024', resumen);
print('Años — orden de las listas',
  resumen.aggregate_array('year'));
print('Número de imágenes Dynamic World',
  resumen.aggregate_array('n_imagenes_dw'));
print('Probabilidad media de construido dentro del candidato',
  resumen.aggregate_array('built_prob_media'));
print('Área con probabilidad built ≥ 0.50 — ha',
  resumen.aggregate_array('built_prob_ge_050_ha'));
print('Porcentaje con probabilidad built ≥ 0.50',
  resumen.aggregate_array('built_prob_ge_050_pct'));
print('Área cuya clase modal es built — ha',
  resumen.aggregate_array('label_built_moda_ha'));
print('Porcentaje cuya clase modal es built',
  resumen.aggregate_array('label_built_moda_pct'));

print(ui.Chart.feature.byFeature(
  resumen,
  'year',
  ['built_prob_media', 'built_prob_ge_050_pct', 'label_built_moda_pct']
).setOptions({
  title: 'Corroboración independiente dentro de los píxeles 70→24',
  hAxis: {title: 'Año', format: '####'},
  vAxes: {
    0: {title: 'Probabilidad media'},
    1: {title: 'Porcentaje del área'}
  },
  series: {
    0: {targetAxisIndex: 0, color: '#54278f'},
    1: {targetAxisIndex: 1, color: '#e6550d'},
    2: {targetAxisIndex: 1, color: '#31a354'}
  },
  pointSize: 5,
  lineWidth: 2
}));

var built2021 = compuestoBuilt(2021);
var built2022 = compuestoBuilt(2022);
var visBuilt = {
  min: 0,
  max: 1,
  palette: ['FFFFFF', 'FFF7BC', 'FEC44F', 'D95F0E', '7F0000']
};

// Contorno de los píxeles candidatos para no ocultar la imagen.
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

print('Interpretación: un aumento desde 2022 y persistencia posterior');
print('apoyan expansión construida; valores ya altos en 2020–2021');
print('indican detección tardía o reclasificación de MapBiomas.');
print('No se ejecutaron exportaciones.');
