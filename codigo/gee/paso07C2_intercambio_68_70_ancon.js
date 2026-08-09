// PASO 7C2 — Diagnóstico del intercambio entre clases en Ancón.
// Evalúa los 10 años principales de pérdida W5 y recuperación W5.
// No exporta ni interpreta los cambios como procesos ecológicos.

var ASSET_ACR =
  'projects/mapbiomas-lomas-jhoreck/assets/inputs/acr_lomas_5_ambitos_gee';
var ASSET_CLASES =
  'projects/mapbiomas-public/assets/peru/collection3/' +
  'mapbiomas_peru_collection3_integration_v1';
var ASSET_TRANSICIONES =
  'projects/mapbiomas-public/assets/peru/collection3/' +
  'mapbiomas_peru_collection3_transitions_v1';

var acr = ee.FeatureCollection(ASSET_ACR);
var ancon = acr.filter(ee.Filter.eq('id_ambito', 'ancon'));
var clases = ee.Image(ASSET_CLASES);
var transiciones = ee.Image(ASSET_TRANSICIONES);
var pixelHa = ee.Image.pixelArea().divide(10000);
var VENTANA = 5;

var LOSS_YEARS = [2006, 2003, 2007, 2009, 2008, 2010, 2002, 2005, 2004, 2012];
var RECOVERY_YEARS = [1990, 1996, 1997, 1999, 2002, 1991, 1998, 1995, 1994, 1992];

function clase(year) {
  return clases.select('classification_' + year);
}

function loma(year) {
  return clase(year).eq(70).rename('estado');
}

function todosEstado(yearStart, yearEnd, estado) {
  var resultado = ee.Image(1).rename('estado');
  for (var year = yearStart; year <= yearEnd; year++) {
    resultado = resultado.and(loma(year).eq(estado));
  }
  return resultado.rename('estado');
}

function perdidaW5(year) {
  return todosEstado(year - VENTANA, year - 1, 1)
    .and(todosEstado(year, year + VENTANA - 1, 0))
    .rename('evento');
}

function recuperacionW5(year) {
  return todosEstado(year - VENTANA, year - 1, 0)
    .and(todosEstado(year, year + VENTANA - 1, 1))
    .rename('evento');
}

function codigoTransicion(year) {
  return transiciones.select(
    'transitions_' + (year - 1) + '_' + year
  );
}

function agregarArea(bandas, mask, nombre) {
  return bandas.addBands(
    pixelHa.updateMask(mask).rename(nombre)
  );
}

var bandas = ee.Image([]);

LOSS_YEARS.forEach(function(year) {
  var evento = perdidaW5(year);
  var codigo = codigoTransicion(year);
  var destino = codigo.mod(100);

  var a68 = evento.and(destino.eq(68));
  var a24 = evento.and(destino.eq(24));
  var a13 = evento.and(destino.eq(13));
  var otro = evento.and(
    destino.neq(68).and(destino.neq(24)).and(destino.neq(13))
  );

  bandas = agregarArea(bandas, evento, 'loss_total_' + year);
  bandas = agregarArea(bandas, a68, 'loss_to68_' + year);
  bandas = agregarArea(bandas, a24, 'loss_to24_' + year);
  bandas = agregarArea(bandas, a13, 'loss_to13_' + year);
  bandas = agregarArea(bandas, otro, 'loss_other_' + year);
});

RECOVERY_YEARS.forEach(function(year) {
  var evento = recuperacionW5(year);
  var codigo = codigoTransicion(year);
  var origen = codigo.divide(100).floor();

  var de68 = evento.and(origen.eq(68));
  var de24 = evento.and(origen.eq(24));
  var de13 = evento.and(origen.eq(13));
  var otro = evento.and(
    origen.neq(68).and(origen.neq(24)).and(origen.neq(13))
  );

  bandas = agregarArea(bandas, evento, 'rec_total_' + year);
  bandas = agregarArea(bandas, de68, 'rec_from68_' + year);
  bandas = agregarArea(bandas, de24, 'rec_from24_' + year);
  bandas = agregarArea(bandas, de13, 'rec_from13_' + year);
  bandas = agregarArea(bandas, otro, 'rec_other_' + year);
});

var areas = bandas.reduceRegion({
  reducer: ee.Reducer.sum(),
  geometry: ancon.geometry(),
  scale: 30,
  maxPixels: 1e9,
  tileScale: 4
});

function valor(field) {
  return ee.Number(ee.Algorithms.If(
    areas.contains(field),
    areas.get(field),
    0
  ));
}

function porcentaje(parte, total) {
  return ee.Number(parte).divide(ee.Number(total).max(0.000001)).multiply(100);
}

var tablaPerdidas = ee.FeatureCollection(LOSS_YEARS.map(function(year) {
  var total = valor('loss_total_' + year);
  var to68 = valor('loss_to68_' + year);
  var to24 = valor('loss_to24_' + year);
  var to13 = valor('loss_to13_' + year);
  var other = valor('loss_other_' + year);

  return ee.Feature(null, {
    year_evento: year,
    total_ha: total,
    to68_ha: to68,
    to68_pct: porcentaje(to68, total),
    to24_ha: to24,
    to24_pct: porcentaje(to24, total),
    to13_ha: to13,
    to13_pct: porcentaje(to13, total),
    other_ha: other,
    other_pct: porcentaje(other, total)
  });
}));

var tablaRecuperaciones = ee.FeatureCollection(
  RECOVERY_YEARS.map(function(year) {
    var total = valor('rec_total_' + year);
    var from68 = valor('rec_from68_' + year);
    var from24 = valor('rec_from24_' + year);
    var from13 = valor('rec_from13_' + year);
    var other = valor('rec_other_' + year);

    return ee.Feature(null, {
      year_evento: year,
      total_ha: total,
      from68_ha: from68,
      from68_pct: porcentaje(from68, total),
      from24_ha: from24,
      from24_pct: porcentaje(from24, total),
      from13_ha: from13,
      from13_pct: porcentaje(from13, total),
      other_ha: other,
      other_pct: porcentaje(other, total)
    });
  })
);

print('PASO 7C2 — INTERCAMBIO DE CLASES EN ANCÓN');
print('Ámbito Ancón — esperado: 1', ancon.size());
print('Años de pérdida auditados — esperado: 10', LOSS_YEARS);
print('Años de recuperación auditados — esperado: 10', RECOVERY_YEARS);
print('Tabla de pérdidas W5', tablaPerdidas);
print('PÉRDIDAS — años', tablaPerdidas.aggregate_array('year_evento'));
print('PÉRDIDAS — total ha', tablaPerdidas.aggregate_array('total_ha'));
print('PÉRDIDAS — destino 68 %', tablaPerdidas.aggregate_array('to68_pct'));
print('PÉRDIDAS — destino 24 %', tablaPerdidas.aggregate_array('to24_pct'));
print('PÉRDIDAS — destino 13 %', tablaPerdidas.aggregate_array('to13_pct'));
print('PÉRDIDAS — otros destinos %', tablaPerdidas.aggregate_array('other_pct'));
print('Tabla de recuperaciones W5', tablaRecuperaciones);
print('RECUPERACIONES — años',
  tablaRecuperaciones.aggregate_array('year_evento'));
print('RECUPERACIONES — total ha',
  tablaRecuperaciones.aggregate_array('total_ha'));
print('RECUPERACIONES — origen 68 %',
  tablaRecuperaciones.aggregate_array('from68_pct'));
print('RECUPERACIONES — origen 24 %',
  tablaRecuperaciones.aggregate_array('from24_pct'));
print('RECUPERACIONES — origen 13 %',
  tablaRecuperaciones.aggregate_array('from13_pct'));
print('RECUPERACIONES — otros orígenes %',
  tablaRecuperaciones.aggregate_array('other_pct'));

var perdida2006 = perdidaW5(2006);
var rec1990 = recuperacionW5(1990);
Map.centerObject(ancon, 9);
Map.addLayer(
  perdida2006.selfMask().clip(ancon.geometry()),
  {palette: ['D73027']},
  'Ancón — pérdida W5 de 2006',
  true
);
Map.addLayer(
  rec1990.selfMask().clip(ancon.geometry()),
  {palette: ['1A9850']},
  'Ancón — recuperación W5 de 1990',
  false
);
Map.addLayer(
  ancon.style({color: '00FFFF', fillColor: '00000000', width: 2}),
  {},
  'Límite Ancón',
  true
);

print('PASO 7C2 FINALIZADO — no se ejecutaron exportaciones.');
