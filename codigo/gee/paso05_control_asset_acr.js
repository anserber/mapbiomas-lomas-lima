// PASO 5B — Control del asset privado del ACR
// Proyecto de cómputo: mapbiomas-lomas-jhoreck
// Este script no ejecuta exportaciones.

var ACR_ASSET =
    'projects/mapbiomas-lomas-jhoreck/assets/inputs/acr_lomas_5_ambitos_gee';

var MAPBIOMAS_ASSET =
    'projects/mapbiomas-public/assets/peru/collection3/' +
    'mapbiomas_peru_collection3_integration_v1';

var acr = ee.FeatureCollection(ACR_ASSET);
var mapbiomas = ee.Image(MAPBIOMAS_ASSET);

print('PASO 5B — Table ID / Asset ID', ACR_ASSET);
print('FeatureCollection del ACR', acr);
print('Número de objetos — esperado: 5', acr.size());
print('Primer objeto', acr.first());

var ids = acr.aggregate_array('id_ambito').sort();
var nombres = acr.aggregate_array('NOMBRE').sort();

print('id_ambito — esperado: 5 valores únicos', ids);
print('Cantidad de id_ambito distintos — esperado: 5',
      ids.distinct().size());
print('Nombres de los ámbitos', nombres);
print('Objetos con los tres campos no nulos — esperado: 5',
      acr.filter(ee.Filter.notNull(['id_ambito', 'NOMBRE', 'Area_Ha'])).size());

var controlAreas = acr.map(function(feature) {
  var areaRef = ee.Number(feature.get('Area_Ha'));
  var areaGee = feature.geometry().area({maxError: 1}).divide(10000);
  var diferencia = areaGee.subtract(areaRef);
  var diferenciaPct = diferencia.abs().divide(areaRef).multiply(100);

  return ee.Feature(null, {
    id_ambito: feature.get('id_ambito'),
    nombre: feature.get('NOMBRE'),
    area_ref_ha: areaRef,
    area_gee_ha: areaGee,
    dif_ha: diferencia,
    dif_abs_pct: diferenciaPct
  });
});

print('Control de áreas: referencia frente a cálculo de GEE', controlAreas);
print('Diferencia porcentual máxima', controlAreas.aggregate_max('dif_abs_pct'));

var clasificacion2024 = mapbiomas.select('classification_2024');
var loma2024 = clasificacion2024.eq(70).selfMask();
var urbano2024 = clasificacion2024.eq(24).selfMask();

Map.centerObject(acr, 10);
Map.addLayer(
    clasificacion2024,
    {min: 0, max: 70},
    'MapBiomas 2024 — referencia',
    false
);
Map.addLayer(loma2024, {palette: ['FFD700']}, 'Clase 70 — Loma 2024');
Map.addLayer(urbano2024, {palette: ['E31A1C']}, 'Clase 24 — Urbano 2024');
Map.addLayer(
    acr.style({
      color: '00FFFF',
      fillColor: '00000000',
      width: 3
    }),
    {},
    'ACR — 5 ámbitos'
);

print('PASO 5B FINALIZADO — no se ejecutaron exportaciones');
