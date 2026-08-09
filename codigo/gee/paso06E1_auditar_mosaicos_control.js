// PASO 6E1 — Auditoría de mosaicos Landsat para control visual.
// No exporta archivos ni interpreta cambios.

var ASSET_ACR =
  'projects/mapbiomas-lomas-jhoreck/assets/inputs/acr_lomas_5_ambitos_gee';
var MOSAICOS_1985_2021 =
  'projects/nexgenmap/MapBiomas2/LANDSAT/PANAMAZON/mosaics-2';
var MOSAICOS_2022_2024 =
  'projects/mapbiomas-raisg/MOSAICOS/mosaics-2';

var acr = ee.FeatureCollection(ASSET_ACR);
var aoi = acr.geometry();
var mosaicosAntiguos = ee.ImageCollection(MOSAICOS_1985_2021)
  .filterBounds(aoi);
var mosaicosRecientes = ee.ImageCollection(MOSAICOS_2022_2024)
  .filterBounds(aoi);

function auditarColeccion(nombre, coleccion) {
  var primera = ee.Image(coleccion.first());
  print(nombre + ' — imágenes que intersectan el ACR', coleccion.size());
  print(nombre + ' — primera imagen', primera);
  print(nombre + ' — bandas de la primera imagen', primera.bandNames());
  print(nombre + ' — propiedades de la primera imagen',
    primera.propertyNames());
  print(nombre + ' — años disponibles',
    coleccion.aggregate_array('year').distinct().sort());
  print(nombre + ' — regiones disponibles',
    coleccion.aggregate_array('region_code').distinct().sort());
  print(nombre + ' — biomas disponibles',
    coleccion.aggregate_array('biome').distinct().sort());
  print(nombre + ' — versiones disponibles',
    coleccion.aggregate_array('version').distinct().sort());
}

print('PASO 6E1 — AUDITORÍA DE MOSAICOS PARA CONTROL VISUAL');
print('Asset ACR', ASSET_ACR);
print('Ámbitos del ACR — esperado: 5', acr.size());

auditarColeccion('Mosaicos 1985–2021', mosaicosAntiguos);
auditarColeccion('Mosaicos 2022–2024', mosaicosRecientes);

print('Imágenes del año 1985 que intersectan el ACR',
  mosaicosAntiguos.filter(ee.Filter.eq('year', 1985)).size());
print('Imágenes del año 2000 que intersectan el ACR',
  mosaicosAntiguos.filter(ee.Filter.eq('year', 2000)).size());
print('Imágenes del año 2021 que intersectan el ACR',
  mosaicosAntiguos.filter(ee.Filter.eq('year', 2021)).size());
print('Imágenes del año 2022 que intersectan el ACR',
  mosaicosRecientes.filter(ee.Filter.eq('year', 2022)).size());
print('Imágenes del año 2023 que intersectan el ACR',
  mosaicosRecientes.filter(ee.Filter.eq('year', 2023)).size());
print('Imágenes del año 2024 que intersectan el ACR',
  mosaicosRecientes.filter(ee.Filter.eq('year', 2024)).size());

Map.centerObject(acr, 9);
Map.addLayer(
  acr.style({color: '00FFFF', fillColor: '00000000', width: 2}),
  {},
  'Cinco ámbitos del ACR'
);

print('No se ejecutaron exportaciones.');
print('Envía las bandas, propiedades, años y cantidades por año antes de 6E2.');
