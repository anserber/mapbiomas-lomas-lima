// PASO 5F — Verificación conjunta de los assets de anillos.
// No exporta archivos ni modifica assets.

var ASSET_AMBITOS =
  'projects/mapbiomas-lomas-jhoreck/assets/inputs/anillos_por_ambito_gee';
var ASSET_SISTEMA =
  'projects/mapbiomas-lomas-jhoreck/assets/inputs/anillos_sistema_gee';

var anillosAmbitos = ee.FeatureCollection(ASSET_AMBITOS);
var anillosSistema = ee.FeatureCollection(ASSET_SISTEMA);
var utm18s = ee.Projection('EPSG:32718');

var idsEsperados = ee.List([
  'amancaes',
  'ancon',
  'carabayllo_1',
  'carabayllo_2',
  'villa_maria'
]);
var zonasEsperadas = ee.List(['0_500', '500_1000', '1000_2000']);

print('PASO 5F — VERIFICACIÓN DE ASSETS');
print('Table ID — anillos por ámbito', ASSET_AMBITOS);
print('Table ID — anillos del sistema', ASSET_SISTEMA);
print('Objetos por ámbito — esperado: 15', anillosAmbitos.size());
print('Objetos del sistema — esperado: 3', anillosSistema.size());
print(
  'id_ambito — esperado: 5 valores',
  anillosAmbitos.aggregate_array('id_ambito').distinct().sort()
);
print(
  'Zonas por ámbito — esperado: 3 valores',
  anillosAmbitos.aggregate_array('zona').distinct().sort()
);
print(
  'Zonas del sistema — esperado: 3 valores',
  anillosSistema.aggregate_array('zona').distinct().sort()
);

var ambitosConClave = anillosAmbitos.map(function (feature) {
  var clave = ee.String(feature.get('id_ambito'))
    .cat('|')
    .cat(ee.String(feature.get('zona')));
  return feature.set('clave_control', clave);
});

print(
  'Combinaciones id_ambito × zona — esperado: 15',
  ambitosConClave.aggregate_count_distinct('clave_control')
);

var obligatoriosAmbitos = anillosAmbitos.filter(
  ee.Filter.notNull([
    'id_ambito', 'nombre', 'zona', 'dmin_m', 'dmax_m', 'area_ha'
  ])
);
var obligatoriosSistema = anillosSistema.filter(
  ee.Filter.notNull(['unidad', 'zona', 'dmin_m', 'dmax_m', 'area_ha'])
);
print(
  'Objetos por ámbito con campos completos — esperado: 15',
  obligatoriosAmbitos.size()
);
print(
  'Objetos del sistema con campos completos — esperado: 3',
  obligatoriosSistema.size()
);

function agregarControlArea(feature) {
  var areaGuardada = ee.Number(feature.get('area_ha'));
  var areaCalculada = feature.geometry().area({
    maxError: 1,
    proj: utm18s
  }).divide(10000);
  var diferencia = areaCalculada.subtract(areaGuardada);
  var diferenciaPct = diferencia.abs()
    .divide(areaGuardada)
    .multiply(100);
  return feature.set({
    area_gee_ha: areaCalculada,
    dif_area_ha: diferencia,
    dif_area_abs_pct: diferenciaPct
  });
}

var controlAmbitos = anillosAmbitos.map(agregarControlArea);
var controlSistema = anillosSistema.map(agregarControlArea);
print(
  'Diferencia porcentual máxima — anillos por ámbito',
  controlAmbitos.aggregate_max('dif_area_abs_pct')
);
print(
  'Diferencia porcentual máxima — anillos del sistema',
  controlSistema.aggregate_max('dif_area_abs_pct')
);
print('Control de áreas — anillos por ámbito', controlAmbitos);
print('Control de áreas — sistema', controlSistema);

var comparacionSistema = ee.FeatureCollection(zonasEsperadas.map(function (zona) {
  zona = ee.String(zona);
  var sumaAmbitos = ee.Number(
    anillosAmbitos.filter(ee.Filter.eq('zona', zona)).aggregate_sum('area_ha')
  );
  var areaSistema = ee.Number(
    anillosSistema.filter(ee.Filter.eq('zona', zona)).first().get('area_ha')
  );
  return ee.Feature(null, {
    zona: zona,
    suma_ambitos_ha: sumaAmbitos,
    area_sistema_disuelto_ha: areaSistema,
    solapamiento_entre_ambitos_ha: sumaAmbitos.subtract(areaSistema)
  });
}));

print(
  'Control: suma por ámbito frente al sistema disuelto',
  comparacionSistema.sort('zona')
);

Map.centerObject(anillosAmbitos, 9);
Map.addLayer(
  anillosAmbitos.style({color: '00BFFF', fillColor: '00000000', width: 2}),
  {},
  '15 anillos por ámbito'
);
Map.addLayer(
  anillosSistema.style({color: 'FF8C00', fillColor: '00000000', width: 3}),
  {},
  '3 anillos del sistema'
);

print('PASO 5F — VERIFICACIÓN FINALIZADA; no se realizaron exportaciones');
