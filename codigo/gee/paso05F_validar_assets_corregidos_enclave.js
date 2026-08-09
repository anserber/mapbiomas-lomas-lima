// PASO 5F-R — Validación de los assets corregidos de anillos y enclave.
// No exporta archivos ni modifica assets.

var ASSET_AMBITOS =
  'projects/mapbiomas-lomas-jhoreck/assets/inputs/' +
  'anillos_por_ambito_periferia_externa_gee';
var ASSET_SISTEMA =
  'projects/mapbiomas-lomas-jhoreck/assets/inputs/' +
  'anillos_sistema_periferia_externa_gee';
var ASSET_ENCLAVE =
  'projects/mapbiomas-lomas-jhoreck/assets/inputs/' +
  'enclave_sedapal_carabayllo2_gee';
var ASSET_ACR =
  'projects/mapbiomas-lomas-jhoreck/assets/inputs/acr_lomas_5_ambitos_gee';

var anillosAmbitos = ee.FeatureCollection(ASSET_AMBITOS);
var anillosSistema = ee.FeatureCollection(ASSET_SISTEMA);
var enclave = ee.FeatureCollection(ASSET_ENCLAVE);
var acr = ee.FeatureCollection(ASSET_ACR);
var utm18s = ee.Projection('EPSG:32718');

var idsEsperados = ee.List([
  'amancaes',
  'ancon',
  'carabayllo_1',
  'carabayllo_2',
  'villa_maria'
]);
var zonasEsperadas = ee.List(['0_500', '500_1000', '1000_2000']);

print('PASO 5F-R — VALIDACIÓN DE ASSETS CORREGIDOS');
print('Table ID — anillos por ámbito', ASSET_AMBITOS);
print('Table ID — anillos del sistema', ASSET_SISTEMA);
print('Table ID — enclave', ASSET_ENCLAVE);

print('Objetos por ámbito — esperado: 15', anillosAmbitos.size());
print('Objetos del sistema — esperado: 3', anillosSistema.size());
print('Objetos del enclave — esperado: 1', enclave.size());

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
var obligatoriosEnclave = enclave.filter(
  ee.Filter.notNull(['unidad_id', 'nombre', 'tipo', 'area_ha'])
);

print(
  'Objetos por ámbito con campos completos — esperado: 15',
  obligatoriosAmbitos.size()
);
print(
  'Objetos del sistema con campos completos — esperado: 3',
  obligatoriosSistema.size()
);
print(
  'Objetos del enclave con campos completos — esperado: 1',
  obligatoriosEnclave.size()
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
var controlEnclave = enclave.map(agregarControlArea);

print(
  'Diferencia porcentual máxima — anillos por ámbito',
  controlAmbitos.aggregate_max('dif_area_abs_pct')
);
print(
  'Diferencia porcentual máxima — anillos del sistema',
  controlSistema.aggregate_max('dif_area_abs_pct')
);
print(
  'Diferencia porcentual máxima — enclave',
  controlEnclave.aggregate_max('dif_area_abs_pct')
);

var enclaveGeom = enclave.geometry();
var acrGeom = acr.geometry();

function areaInterseccionHa(feature, geometria) {
  return feature.geometry()
    .intersection(geometria, 1)
    .area({maxError: 1, proj: utm18s})
    .divide(10000);
}

var interAmbitosEnclave = anillosAmbitos.map(function (feature) {
  return ee.Feature(null, {
    area_inter_ha: areaInterseccionHa(feature, enclaveGeom)
  });
});
var interSistemaEnclave = anillosSistema.map(function (feature) {
  return ee.Feature(null, {
    area_inter_ha: areaInterseccionHa(feature, enclaveGeom)
  });
});
var interAmbitosAcr = anillosAmbitos.map(function (feature) {
  return ee.Feature(null, {
    area_inter_ha: areaInterseccionHa(feature, acrGeom)
  });
});
var interSistemaAcr = anillosSistema.map(function (feature) {
  return ee.Feature(null, {
    area_inter_ha: areaInterseccionHa(feature, acrGeom)
  });
});

print(
  'Intersección anillos por ámbito × enclave — ha; esperado: 0',
  interAmbitosEnclave.aggregate_sum('area_inter_ha')
);
print(
  'Intersección anillos sistema × enclave — ha; esperado: 0',
  interSistemaEnclave.aggregate_sum('area_inter_ha')
);
print(
  'Intersección anillos por ámbito × ACR — ha; esperado: 0',
  interAmbitosAcr.aggregate_sum('area_inter_ha')
);
print(
  'Intersección anillos sistema × ACR — ha; esperado: 0',
  interSistemaAcr.aggregate_sum('area_inter_ha')
);

var c2_0_500 = anillosAmbitos
  .filter(ee.Filter.and(
    ee.Filter.eq('id_ambito', 'carabayllo_2'),
    ee.Filter.eq('zona', '0_500')
  ))
  .first();
var sistema_0_500 = anillosSistema
  .filter(ee.Filter.eq('zona', '0_500'))
  .first();
var enclavePrimero = enclave.first();

print(
  'Carabayllo 2, 0–500 m — área guardada, ha; esperado: 451.238695',
  c2_0_500.get('area_ha')
);
print(
  'Sistema, 0–500 m — área guardada, ha; esperado: 5265.400521',
  sistema_0_500.get('area_ha')
);
print(
  'Enclave — área guardada, ha; esperado: 10.710224',
  enclavePrimero.get('area_ha')
);

var comparacionSistema = ee.FeatureCollection(
  zonasEsperadas.map(function (zona) {
    zona = ee.String(zona);
    var sumaAmbitos = ee.Number(
      anillosAmbitos
        .filter(ee.Filter.eq('zona', zona))
        .aggregate_sum('area_ha')
    );
    var areaSistema = ee.Number(
      anillosSistema
        .filter(ee.Filter.eq('zona', zona))
        .first()
        .get('area_ha')
    );
    return ee.Feature(null, {
      zona: zona,
      suma_ambitos_ha: sumaAmbitos,
      area_sistema_disuelto_ha: areaSistema,
      solapamiento_entre_ambitos_ha: sumaAmbitos.subtract(areaSistema)
    });
  })
);

print(
  'Control: suma por ámbito frente al sistema disuelto',
  comparacionSistema.sort('zona')
);

Map.centerObject(anillosAmbitos, 9);
Map.addLayer(
  anillosAmbitos.style({
    color: '00BFFF',
    fillColor: '00000000',
    width: 2
  }),
  {},
  'Anillos por ámbito — periferia externa'
);
Map.addLayer(
  anillosSistema.style({
    color: 'FF8C00',
    fillColor: '00000000',
    width: 3
  }),
  {},
  'Anillos del sistema — periferia externa'
);
Map.addLayer(
  enclave.style({
    color: 'FF00FF',
    fillColor: 'FF00FF66',
    width: 2
  }),
  {},
  'Enclave SEDAPAL separado'
);
Map.addLayer(
  acr.style({
    color: 'FFFFFF',
    fillColor: '00000000',
    width: 1
  }),
  {},
  'ACR oficial'
);

print(
  'PASO 5F-R FINALIZADO — no se realizaron exportaciones'
);
