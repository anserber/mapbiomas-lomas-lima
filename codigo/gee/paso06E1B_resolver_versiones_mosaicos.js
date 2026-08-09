// PASO 6E1-B — Resolver versiones y teselas de mosaicos Landsat.
// Objetivo: definir una selección única por año y región antes del control visual.
// No exporta archivos ni interpreta cambios.

var ASSET_ACR =
  'projects/mapbiomas-lomas-jhoreck/assets/inputs/acr_lomas_5_ambitos_gee';
var MOSAICOS_1985_2021 =
  'projects/nexgenmap/MapBiomas2/LANDSAT/PANAMAZON/mosaics-2';
var MOSAICOS_2022_2024 =
  'projects/mapbiomas-raisg/MOSAICOS/mosaics-2';

var acr = ee.FeatureCollection(ASSET_ACR);
var aoi = acr.geometry();

var antiguos = ee.ImageCollection(MOSAICOS_1985_2021).filterBounds(aoi);
var recientes = ee.ImageCollection(MOSAICOS_2022_2024).filterBounds(aoi);

var bandasControl = ee.List([
  'blue_median',
  'green_median',
  'red_median',
  'nir_median',
  'swir1_median',
  'swir2_median',
  'ndvi_median',
  'evi2_median',
  'ndwi_gao_median',
  'ndbi_median'
]);

function agregarClave(imagen) {
  var year = ee.Number(imagen.get('year')).format('%d');
  var region = ee.Number(imagen.get('region_code')).format('%d');
  var version = ee.String(imagen.get('version'));
  return imagen.set('clave_year_region_version',
    year.cat('|').cat(region).cat('|').cat(version));
}

function auditarAnio(coleccion, year, etiqueta) {
  var subset = coleccion.filter(ee.Filter.eq('year', year))
    .map(agregarClave);

  print(etiqueta + ' — cantidad total', subset.size());
  print(etiqueta + ' — índices', subset.aggregate_array('system:index').sort());
  print(etiqueta + ' — year|region|version',
    subset.aggregate_histogram('clave_year_region_version'));
  print(etiqueta + ' — regiones', subset.aggregate_histogram('region_code'));
  print(etiqueta + ' — versiones', subset.aggregate_histogram('version'));
  print(etiqueta + ' — satélites', subset.aggregate_histogram('satellite'));
  print(etiqueta + ' — nimages', subset.aggregate_array('nimages').sort());
  print(etiqueta + ' — cloud_cover',
    subset.aggregate_array('cloud_cover').sort());
}

function bandasAusentes(coleccion, etiqueta) {
  var primera = ee.Image(coleccion.first());
  var disponibles = primera.bandNames();
  print(etiqueta + ' — bandas de control ausentes',
    bandasControl.removeAll(disponibles));
}

print('PASO 6E1-B — VERSIONES Y TESELAS DE MOSAICOS');
print('Regiones necesarias', [703, 704, 705]);

bandasAusentes(
  antiguos.filter(ee.Filter.eq('year', 1985)),
  '1985–2021'
);
bandasAusentes(
  recientes.filter(ee.Filter.eq('year', 2024)),
  '2022–2024'
);

auditarAnio(antiguos, 1985, '1985');
auditarAnio(antiguos, 2000, '2000');
auditarAnio(antiguos, 2021, '2021');
auditarAnio(recientes, 2022, '2022');
auditarAnio(recientes, 2023, '2023');
auditarAnio(recientes, 2024, '2024');

Map.centerObject(acr, 9);
Map.addLayer(
  acr.style({color: '00FFFF', fillColor: '00000000', width: 2}),
  {},
  'Cinco ámbitos del ACR'
);

print('No se ejecutaron exportaciones.');
print('Envía la salida completa antes de construir 6E2.');
