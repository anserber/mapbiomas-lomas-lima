// PASO 7C3 — Auditoría focal de pérdidas W5 en Carabayllo 2.
// Descompone por año y clase de destino los eventos robustos de clase 70.
// Excluye la ruptura cartográfica conocida de 2014–2015 (70→13/68).
// No exporta ni denomina automáticamente estos cambios como pérdida ecológica.

var ASSET_ACR =
  'projects/mapbiomas-lomas-jhoreck/assets/inputs/acr_lomas_5_ambitos_gee';
var ASSET_CLASES =
  'projects/mapbiomas-public/assets/peru/collection3/' +
  'mapbiomas_peru_collection3_integration_v1';
var ASSET_TRANSICIONES =
  'projects/mapbiomas-public/assets/peru/collection3/' +
  'mapbiomas_peru_collection3_transitions_v1';

var acr = ee.FeatureCollection(ASSET_ACR);
var carabayllo2 = acr.filter(
  ee.Filter.eq('id_ambito', 'carabayllo_2')
);
var clases = ee.Image(ASSET_CLASES);
var transiciones = ee.Image(ASSET_TRANSICIONES);
var pixelHa = ee.Image.pixelArea().divide(10000);

var YEAR_START = 1985;
var YEAR_END = 2024;
var VENTANA = 5;
var PRIMER_EVENTO = YEAR_START + VENTANA;       // 1990
var ULTIMO_EVENTO = YEAR_END - VENTANA + 1;     // 2020

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
  var antes = todosEstado(year - VENTANA, year - 1, 1);
  var despues = todosEstado(year, year + VENTANA - 1, 0);
  return antes.and(despues).rename('evento');
}

function codigoTransicion(year) {
  return transiciones.select(
    'transitions_' + (year - 1) + '_' + year
  );
}

// Ruptura ya comprobada en el Paso 6: 2014–2015, 70→13/68.
var codigo2015 = codigoTransicion(2015);
var rupturaConocida = codigo2015.eq(7013)
  .or(codigo2015.eq(7068))
  .clip(carabayllo2.geometry())
  .unmask(0)
  .rename('ruptura');

function agregarArea(imagen, mascara, nombre) {
  return imagen.addBands(
    pixelHa.updateMask(mascara).rename(nombre)
  );
}

var bandas = ee.Image([]);
var years = [];

for (var year = PRIMER_EVENTO; year <= ULTIMO_EVENTO; year++) {
  years.push(year);

  var eventoBruto = perdidaW5(year);
  var eventoFiltrado = eventoBruto
    .and(rupturaConocida.eq(0))
    .rename('evento');
  var codigo = codigoTransicion(year);
  var destino = codigo.mod(100);

  var to68 = eventoFiltrado.and(destino.eq(68));
  var to13 = eventoFiltrado.and(destino.eq(13));
  var to24 = eventoFiltrado.and(destino.eq(24));
  var other = eventoFiltrado.and(
    destino.neq(68)
      .and(destino.neq(13))
      .and(destino.neq(24))
  );
  var excluida = eventoBruto.and(rupturaConocida.eq(1));

  bandas = agregarArea(bandas, eventoBruto, 'bruto_' + year);
  bandas = agregarArea(bandas, eventoFiltrado, 'filtrado_' + year);
  bandas = agregarArea(bandas, to68, 'to68_' + year);
  bandas = agregarArea(bandas, to13, 'to13_' + year);
  bandas = agregarArea(bandas, to24, 'to24_' + year);
  bandas = agregarArea(bandas, other, 'other_' + year);
  bandas = agregarArea(bandas, excluida, 'excluida_' + year);
}

var areas = bandas.reduceRegion({
  reducer: ee.Reducer.sum(),
  geometry: carabayllo2.geometry(),
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
  return ee.Number(parte)
    .divide(ee.Number(total).max(0.000001))
    .multiply(100);
}

var tabla = ee.FeatureCollection(years.map(function(year) {
  var bruto = valor('bruto_' + year);
  var filtrado = valor('filtrado_' + year);
  var to68 = valor('to68_' + year);
  var to13 = valor('to13_' + year);
  var to24 = valor('to24_' + year);
  var other = valor('other_' + year);
  var excluida = valor('excluida_' + year);

  return ee.Feature(null, {
    year_evento: year,
    year_inicio_transicion: year - 1,
    perdida_w5_bruta_ha: bruto,
    ruptura_excluida_ha: excluida,
    perdida_w5_filtrada_ha: filtrado,
    to68_ha: to68,
    to68_pct: porcentaje(to68, filtrado),
    to13_ha: to13,
    to13_pct: porcentaje(to13, filtrado),
    to24_ha: to24,
    to24_pct: porcentaje(to24, filtrado),
    other_ha: other,
    other_pct: porcentaje(other, filtrado)
  });
}));

var conEvento = tabla.filter(
  ee.Filter.gt('perdida_w5_filtrada_ha', 0.000001)
).sort('year_evento');

var totalFiltrado = ee.Number(
  tabla.aggregate_sum('perdida_w5_filtrada_ha')
);
var totalTo68 = ee.Number(tabla.aggregate_sum('to68_ha'));
var totalTo13 = ee.Number(tabla.aggregate_sum('to13_ha'));
var totalTo24 = ee.Number(tabla.aggregate_sum('to24_ha'));
var totalOther = ee.Number(tabla.aggregate_sum('other_ha'));
var totalExcluido = ee.Number(
  tabla.aggregate_sum('ruptura_excluida_ha')
);

var resumen = ee.Dictionary({
  ambito: 'carabayllo_2',
  periodo_evaluable_w5: '1990–2020',
  years_con_evento: conEvento.aggregate_array('year_evento'),
  perdida_w5_filtrada_total_ha: totalFiltrado,
  ruptura_conocida_excluida_total_ha: totalExcluido,
  destino_68_ha: totalTo68,
  destino_68_pct: porcentaje(totalTo68, totalFiltrado),
  destino_13_ha: totalTo13,
  destino_13_pct: porcentaje(totalTo13, totalFiltrado),
  destino_24_ha: totalTo24,
  destino_24_pct: porcentaje(totalTo24, totalFiltrado),
  otros_destinos_ha: totalOther,
  otros_destinos_pct: porcentaje(totalOther, totalFiltrado),
  suma_destinos_ha: totalTo68
    .add(totalTo13)
    .add(totalTo24)
    .add(totalOther),
  diferencia_control_ha: totalFiltrado.subtract(
    totalTo68.add(totalTo13).add(totalTo24).add(totalOther)
  ).abs()
});

print('PASO 7C3 — DESTINOS W5 EN CARABAYLLO 2');
print('Unidad — esperado: 1 objeto', carabayllo2.size());
print('Años evaluables W5 — esperado: 31', years.length);
print('Resumen focal', resumen);
print('Años con pérdida W5 filtrada', conEvento);
print(
  'Años con evento',
  conEvento.aggregate_array('year_evento')
);
print(
  'Pérdida filtrada por año — ha',
  conEvento.aggregate_array('perdida_w5_filtrada_ha')
);
print(
  'Destino 68 por año — %',
  conEvento.aggregate_array('to68_pct')
);
print(
  'Destino 13 por año — %',
  conEvento.aggregate_array('to13_pct')
);
print(
  'Destino 24 por año — %',
  conEvento.aggregate_array('to24_pct')
);
print(
  'Otros destinos por año — %',
  conEvento.aggregate_array('other_pct')
);

var mapaTo68 = ee.Image(0);
var mapaTo13 = ee.Image(0);
var mapaTo24 = ee.Image(0);
var mapaOther = ee.Image(0);

for (var mapYear = PRIMER_EVENTO;
     mapYear <= ULTIMO_EVENTO;
     mapYear++) {
  var mapEvento = perdidaW5(mapYear)
    .and(rupturaConocida.eq(0));
  var mapDestino = codigoTransicion(mapYear).mod(100);

  mapaTo68 = mapaTo68.or(mapEvento.and(mapDestino.eq(68)));
  mapaTo13 = mapaTo13.or(mapEvento.and(mapDestino.eq(13)));
  mapaTo24 = mapaTo24.or(mapEvento.and(mapDestino.eq(24)));
  mapaOther = mapaOther.or(
    mapEvento.and(
      mapDestino.neq(68)
        .and(mapDestino.neq(13))
        .and(mapDestino.neq(24))
    )
  );
}

Map.centerObject(carabayllo2, 13);
Map.addLayer(
  mapaTo68.selfMask().clip(carabayllo2.geometry()),
  {palette: ['8C6BB1']},
  'Carabayllo 2 — W5 con destino 68',
  true
);
Map.addLayer(
  mapaTo13.selfMask().clip(carabayllo2.geometry()),
  {palette: ['FDB863']},
  'Carabayllo 2 — W5 con destino 13',
  true
);
Map.addLayer(
  mapaTo24.selfMask().clip(carabayllo2.geometry()),
  {palette: ['D73027']},
  'Carabayllo 2 — W5 con destino 24',
  true
);
Map.addLayer(
  mapaOther.selfMask().clip(carabayllo2.geometry()),
  {palette: ['636363']},
  'Carabayllo 2 — W5 con otros destinos',
  false
);
Map.addLayer(
  rupturaConocida.selfMask(),
  {palette: ['00FFFF']},
  'Ruptura 2014–2015 excluida',
  false
);
Map.addLayer(
  carabayllo2.style({
    color: 'FFFFFF',
    fillColor: '00000000',
    width: 2
  }),
  {},
  'Límite Carabayllo 2',
  true
);

print('PASO 7C3 FINALIZADO — no se ejecutaron exportaciones.');
