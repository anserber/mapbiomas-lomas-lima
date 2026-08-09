// PASO 6A — Auditoría estructural del asset de transiciones MapBiomas Perú C3
// No exporta ni modifica datos.

var ASSET_TRANSICIONES =
  'projects/mapbiomas-public/assets/peru/collection3/' +
  'mapbiomas_peru_collection3_transitions_v1';

var ASSET_ACR =
  'projects/mapbiomas-lomas-jhoreck/assets/inputs/' +
  'acr_lomas_5_ambitos_gee';

var transiciones = ee.Image(ASSET_TRANSICIONES);
var acr = ee.FeatureCollection(ASSET_ACR);
var bandas = transiciones.bandNames();
var primeraBanda = ee.String(bandas.get(0));
var ultimaBanda = ee.String(bandas.get(bandas.size().subtract(1)));
var imagenPrimeraBanda = transiciones.select([primeraBanda]);
var proyeccion = imagenPrimeraBanda.projection();

print('PASO 6A — AUDITORÍA DE TRANSICIONES');
print('Table ID / Asset ID de transiciones', ASSET_TRANSICIONES);
print('Asset del ACR', ASSET_ACR);
print('Número de bandas', bandas.size());
print('Nombres exactos de todas las bandas', bandas);
print('Primera banda', primeraBanda);
print('Última banda', ultimaBanda);
print('Tipo de píxel por banda', transiciones.bandTypes());
print('CRS de la primera banda', proyeccion.crs());
print('Transformación de la primera banda', proyeccion.transform());
print('Escala nominal de la primera banda — m', proyeccion.nominalScale());
print('Propiedades disponibles del asset', transiciones.propertyNames());
print('Número de ámbitos del ACR — esperado: 5', acr.size());
print(
  'id_ambito del ACR — esperado: 5',
  acr.aggregate_array('id_ambito').distinct().sort()
);

Map.centerObject(acr, 9);
Map.addLayer(
  imagenPrimeraBanda.clip(acr.geometry()),
  {
    min: 0,
    max: 7070,
    palette: ['1a1a1a', 'f4d03f', 'e74c3c', '3498db', '2ecc71']
  },
  'Primera banda — solo diagnóstico, no interpretar'
);
Map.addLayer(
  acr.style({
    color: '00D5FF',
    fillColor: '00000000',
    width: 2
  }),
  {},
  'ACR — cinco ámbitos'
);

print('PASO 6A FINALIZADO — no se ejecutaron exportaciones');
