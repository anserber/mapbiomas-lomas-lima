// PASO 5B — Control métrico del asset del ACR
// Script independiente. No ejecuta exportaciones.

var ACR_ASSET =
    'projects/mapbiomas-lomas-jhoreck/assets/inputs/acr_lomas_5_ambitos_gee';

var acr = ee.FeatureCollection(ACR_ASSET);
var utm18s = ee.Projection('EPSG:32718');

var control = acr.map(function(feature) {
  var referencia = ee.Number(feature.get('Area_Ha'));
  var geodesica = feature.geometry().area(1).divide(10000);
  var utm = feature.geometry().area(1, utm18s).divide(10000);
  var diferencia = utm.subtract(referencia);
  var diferenciaPct =
      diferencia.abs().divide(referencia).multiply(100);

  return ee.Feature(null, {
    id_ambito: feature.get('id_ambito'),
    nombre: feature.get('NOMBRE'),
    area_ref_ha: referencia,
    area_geodesica_ha: geodesica,
    area_utm_ha: utm,
    dif_utm_ha: diferencia,
    dif_utm_abs_pct: diferenciaPct
  });
});

print('PASO 5B — CONTROL MÉTRICO');
print('Número de objetos — esperado: 5', control.size());
print('Orden de los resultados', control.aggregate_array('id_ambito'));
print('Área de referencia — ha', control.aggregate_array('area_ref_ha'));
print('Área geodésica — ha', control.aggregate_array('area_geodesica_ha'));
print('Área UTM 18S — ha', control.aggregate_array('area_utm_ha'));
print('Diferencia UTM — ha', control.aggregate_array('dif_utm_ha'));
print(
    'Diferencia UTM absoluta — %',
    control.aggregate_array('dif_utm_abs_pct')
);
print(
    'Diferencia UTM porcentual máxima',
    control.aggregate_max('dif_utm_abs_pct')
);
print('CONTROL FINALIZADO — no se ejecutaron exportaciones');
