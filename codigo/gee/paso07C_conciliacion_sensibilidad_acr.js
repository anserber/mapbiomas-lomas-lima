// PASO 7C — Conciliación y sensibilidad temporal.
// Compara ventanas estrictas W3 y W5, verifica soporte en el asset oficial
// de transiciones, separa rupturas conocidas y cuantifica censura final.
// No exporta archivos ni interpreta cambios cartográficos como impacto ecológico.

var ASSET_ACR =
  'projects/mapbiomas-lomas-jhoreck/assets/inputs/acr_lomas_5_ambitos_gee';
var ASSET_CLASES =
  'projects/mapbiomas-public/assets/peru/collection3/' +
  'mapbiomas_peru_collection3_integration_v1';
var ASSET_TRANSICIONES =
  'projects/mapbiomas-public/assets/peru/collection3/' +
  'mapbiomas_peru_collection3_transitions_v1';

var acr = ee.FeatureCollection(ASSET_ACR);
var clases = ee.Image(ASSET_CLASES);
var transiciones = ee.Image(ASSET_TRANSICIONES);
var pixelHa = ee.Image.pixelArea().divide(10000);
var YEAR_START = 1985;
var YEAR_END = 2024;

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

function eventosPorYear(ventana) {
  var eventos = {};
  var primerYear = YEAR_START + ventana;
  var ultimoYear = YEAR_END - ventana + 1;

  for (var year = primerYear; year <= ultimoYear; year++) {
    var antesLoma = todosEstado(year - ventana, year - 1, 1);
    var antesNoLoma = todosEstado(year - ventana, year - 1, 0);
    var despuesLoma = todosEstado(year, year + ventana - 1, 1);
    var despuesNoLoma = todosEstado(year, year + ventana - 1, 0);

    eventos[year] = {
      perdida: antesLoma.and(despuesNoLoma).rename('evento'),
      recuperacion: antesNoLoma.and(despuesLoma).rename('evento')
    };
  }

  return {
    ventana: ventana,
    primerYear: primerYear,
    ultimoYear: ultimoYear,
    eventos: eventos
  };
}

function transicionOficial(year) {
  return transiciones.select(
    'transitions_' + (year - 1) + '_' + year
  );
}

function perdidaOficial(year) {
  var codigo = transicionOficial(year);
  return codigo.divide(100).floor().eq(70)
    .and(codigo.mod(100).neq(70))
    .rename('evento');
}

function recuperacionOficial(year) {
  var codigo = transicionOficial(year);
  return codigo.divide(100).floor().neq(70)
    .and(codigo.mod(100).eq(70))
    .rename('evento');
}

var eventos3 = eventosPorYear(3);
var eventos5 = eventosPorYear(5);

// Rupturas comprobadas en el Paso 6.
var ancon = acr.filter(ee.Filter.eq('id_ambito', 'ancon'));
var carabayllo2 = acr.filter(ee.Filter.eq('id_ambito', 'carabayllo_2'));

var rupturaAncon = transicionOficial(2001).eq(7068)
  .clip(ancon.geometry())
  .unmask(0)
  .rename('ruptura');

var transicion2015 = transicionOficial(2015);
var rupturaCarabayllo2 = transicion2015.eq(7013)
  .or(transicion2015.eq(7068))
  .clip(carabayllo2.geometry())
  .unmask(0)
  .rename('ruptura');

var rupturasConocidas = ee.ImageCollection.fromImages([
  rupturaAncon,
  rupturaCarabayllo2
]).max().unmask(0).rename('ruptura');
var fueraRuptura = rupturasConocidas.eq(0).rename('evento');

// Años cuyas transiciones fueron auditadas específicamente en el Paso 6.
var YEARS_ADVERTIDOS = [
  1986, 1987, 2001, 2006, 2010, 2012,
  2014, 2015, 2020, 2022, 2023, 2024
];

var perdida3FiltradaConteo = ee.Image(0);
var perdida5FiltradaConteo = ee.Image(0);
var recuperacion3Conteo = ee.Image(0);
var recuperacion5Conteo = ee.Image(0);
var perdidaSolo3Conteo = ee.Image(0);
var recuperacionSolo3Conteo = ee.Image(0);
var perdidaExcluidaRupturaConteo = ee.Image(0);
var perdida3SinSoporteOficialConteo = ee.Image(0);
var recuperacion3SinSoporteOficialConteo = ee.Image(0);
var perdida5SinSoporteOficialConteo = ee.Image(0);
var recuperacion5SinSoporteOficialConteo = ee.Image(0);

var bandasAnuales = ee.Image([]);
var yearsW3 = [];

for (var year = eventos3.primerYear; year <= eventos3.ultimoYear; year++) {
  yearsW3.push(year);

  var perdida3 = eventos3.eventos[year].perdida;
  var recuperacion3 = eventos3.eventos[year].recuperacion;
  var perdida3Filtrada = perdida3.and(fueraRuptura).rename('evento');
  var oficialLoss = perdidaOficial(year);
  var oficialRecovery = recuperacionOficial(year);
  var perdida3SinSoporte = perdida3.and(oficialLoss.not());
  var recuperacion3SinSoporte = recuperacion3.and(oficialRecovery.not());

  var perdida5 = ee.Image(0).rename('evento');
  var recuperacion5 = ee.Image(0).rename('evento');
  var perdida5Filtrada = ee.Image(0).rename('evento');

  if (year >= eventos5.primerYear && year <= eventos5.ultimoYear) {
    perdida5 = eventos5.eventos[year].perdida;
    recuperacion5 = eventos5.eventos[year].recuperacion;
    perdida5Filtrada = perdida5.and(fueraRuptura).rename('evento');

    perdida5FiltradaConteo =
      perdida5FiltradaConteo.add(perdida5Filtrada);
    recuperacion5Conteo = recuperacion5Conteo.add(recuperacion5);
    perdida5SinSoporteOficialConteo =
      perdida5SinSoporteOficialConteo.add(
        perdida5.and(oficialLoss.not())
      );
    recuperacion5SinSoporteOficialConteo =
      recuperacion5SinSoporteOficialConteo.add(
        recuperacion5.and(oficialRecovery.not())
      );
  }

  perdida3FiltradaConteo =
    perdida3FiltradaConteo.add(perdida3Filtrada);
  recuperacion3Conteo = recuperacion3Conteo.add(recuperacion3);
  perdidaSolo3Conteo = perdidaSolo3Conteo.add(
    perdida3Filtrada.and(perdida5Filtrada.not())
  );
  recuperacionSolo3Conteo = recuperacionSolo3Conteo.add(
    recuperacion3.and(recuperacion5.not())
  );
  perdidaExcluidaRupturaConteo =
    perdidaExcluidaRupturaConteo.add(
      perdida3.and(rupturasConocidas.rename('evento'))
    );
  perdida3SinSoporteOficialConteo =
    perdida3SinSoporteOficialConteo.add(perdida3SinSoporte);
  recuperacion3SinSoporteOficialConteo =
    recuperacion3SinSoporteOficialConteo.add(recuperacion3SinSoporte);

  bandasAnuales = bandasAnuales
    .addBands(
      pixelHa.updateMask(perdida3Filtrada)
        .rename('loss_w3_' + year)
    )
    .addBands(
      pixelHa.updateMask(perdida5Filtrada)
        .rename('loss_w5_' + year)
    )
    .addBands(
      pixelHa.updateMask(recuperacion3)
        .rename('rec_w3_' + year)
    )
    .addBands(
      pixelHa.updateMask(recuperacion5)
        .rename('rec_w5_' + year)
    )
    .addBands(
      pixelHa.updateMask(
        perdida3.and(rupturasConocidas.rename('evento'))
      ).rename('excluded_' + year)
    );
}

// Transiciones recientes que aún no tienen seguimiento suficiente.
function sumarTransicionesCensuradas(yearStart, yearEnd, tipo) {
  var conteo = ee.Image(0);
  for (var year = yearStart; year <= yearEnd; year++) {
    conteo = conteo.add(
      tipo === 'perdida' ? perdidaOficial(year) : recuperacionOficial(year)
    );
  }
  return conteo;
}

var censuraPerdidaW3 =
  sumarTransicionesCensuradas(2023, 2024, 'perdida');
var censuraRecuperacionW3 =
  sumarTransicionesCensuradas(2023, 2024, 'recuperacion');
var censuraPerdidaW5 =
  sumarTransicionesCensuradas(2021, 2024, 'perdida');
var censuraRecuperacionW5 =
  sumarTransicionesCensuradas(2021, 2024, 'recuperacion');

var metricasResumen = pixelHa.rename('area_grilla_ha')
  .addBands(
    pixelHa.multiply(perdida3FiltradaConteo)
      .rename('perdida_w3_evento_ha')
  )
  .addBands(
    pixelHa.multiply(perdida5FiltradaConteo)
      .rename('perdida_w5_robusta_evento_ha')
  )
  .addBands(
    pixelHa.multiply(perdidaSolo3Conteo)
      .rename('perdida_solo_w3_evento_ha')
  )
  .addBands(
    pixelHa.multiply(recuperacion3Conteo)
      .rename('recuperacion_w3_evento_ha')
  )
  .addBands(
    pixelHa.multiply(recuperacion5Conteo)
      .rename('recuperacion_w5_robusta_evento_ha')
  )
  .addBands(
    pixelHa.multiply(recuperacionSolo3Conteo)
      .rename('recuperacion_solo_w3_evento_ha')
  )
  .addBands(
    pixelHa.multiply(perdidaExcluidaRupturaConteo)
      .rename('perdida_excluida_ruptura_evento_ha')
  )
  .addBands(
    pixelHa.multiply(perdida3SinSoporteOficialConteo)
      .rename('perdida_w3_sin_soporte_oficial_ha')
  )
  .addBands(
    pixelHa.multiply(recuperacion3SinSoporteOficialConteo)
      .rename('recuperacion_w3_sin_soporte_oficial_ha')
  )
  .addBands(
    pixelHa.multiply(perdida5SinSoporteOficialConteo)
      .rename('perdida_w5_sin_soporte_oficial_ha')
  )
  .addBands(
    pixelHa.multiply(recuperacion5SinSoporteOficialConteo)
      .rename('recuperacion_w5_sin_soporte_oficial_ha')
  )
  .addBands(
    pixelHa.multiply(censuraPerdidaW3)
      .rename('censura_perdida_w3_ha')
  )
  .addBands(
    pixelHa.multiply(censuraRecuperacionW3)
      .rename('censura_recuperacion_w3_ha')
  )
  .addBands(
    pixelHa.multiply(censuraPerdidaW5)
      .rename('censura_perdida_w5_ha')
  )
  .addBands(
    pixelHa.multiply(censuraRecuperacionW5)
      .rename('censura_recuperacion_w5_ha')
  );

var resumenPorAmbito = metricasResumen.reduceRegions({
  collection: acr,
  reducer: ee.Reducer.sum(),
  scale: 30,
  tileScale: 4
});

var totalesAnuales = bandasAnuales.reduceRegion({
  reducer: ee.Reducer.sum(),
  geometry: acr.geometry(),
  scale: 30,
  maxPixels: 1e9,
  tileScale: 4
});

function valorDiccionario(diccionario, field) {
  return ee.Number(ee.Algorithms.If(
    diccionario.contains(field),
    diccionario.get(field),
    0
  ));
}

var resumenAnual = ee.FeatureCollection(yearsW3.map(function(year) {
  return ee.Feature(null, {
    year_evento: year,
    year_inicio_transicion: year - 1,
    advertido_paso06: YEARS_ADVERTIDOS.indexOf(year) >= 0 ? 1 : 0,
    ruptura_conocida: (year === 2001 || year === 2015) ? 1 : 0,
    perdida_w3_filtrada_ha:
      valorDiccionario(totalesAnuales, 'loss_w3_' + year),
    perdida_w5_robusta_ha:
      valorDiccionario(totalesAnuales, 'loss_w5_' + year),
    recuperacion_w3_ha:
      valorDiccionario(totalesAnuales, 'rec_w3_' + year),
    recuperacion_w5_robusta_ha:
      valorDiccionario(totalesAnuales, 'rec_w5_' + year),
    perdida_excluida_ruptura_ha:
      valorDiccionario(totalesAnuales, 'excluded_' + year)
  });
}));

var topPerdidas = resumenAnual
  .sort('perdida_w5_robusta_ha', false)
  .limit(10);
var topRecuperaciones = resumenAnual
  .sort('recuperacion_w5_robusta_ha', false)
  .limit(10);

print('PASO 7C — CONCILIACIÓN Y SENSIBILIDAD');
print('Ámbitos — esperado: 5', acr.size());
print('Años evaluables W3 — esperado: 35', yearsW3.length);
print('Resumen por ámbito — esperado: 5 filas', resumenPorAmbito);
print('Eventos por año — esperado: 35 filas', resumenAnual);
print('Años con mayor pérdida robusta W5 — primeras 10 filas', topPerdidas);
print('TOP pérdida W5 — años',
  topPerdidas.aggregate_array('year_evento'));
print('TOP pérdida W5 — hectáreas',
  topPerdidas.aggregate_array('perdida_w5_robusta_ha'));
print('TOP pérdida W5 — pérdida W3 del mismo año, hectáreas',
  topPerdidas.aggregate_array('perdida_w3_filtrada_ha'));
print('TOP pérdida W5 — excluida como ruptura conocida, hectáreas',
  topPerdidas.aggregate_array('perdida_excluida_ruptura_ha'));
print('Años con mayor recuperación robusta W5 — primeras 10 filas',
  topRecuperaciones);
print('TOP recuperación W5 — años',
  topRecuperaciones.aggregate_array('year_evento'));
print('TOP recuperación W5 — hectáreas',
  topRecuperaciones.aggregate_array('recuperacion_w5_robusta_ha'));
print('TOP recuperación W5 — recuperación W3 del mismo año, hectáreas',
  topRecuperaciones.aggregate_array('recuperacion_w3_ha'));
print(
  'Años auditados en Paso 6 dentro del rango W3',
  resumenAnual.filter(ee.Filter.eq('advertido_paso06', 1))
);
print(
  'Pérdida W3 sin soporte del asset oficial — esperado: [0,0,0,0,0]',
  resumenPorAmbito.aggregate_array('perdida_w3_sin_soporte_oficial_ha')
);
print(
  'Recuperación W3 sin soporte del asset oficial — esperado: [0,0,0,0,0]',
  resumenPorAmbito.aggregate_array('recuperacion_w3_sin_soporte_oficial_ha')
);
print(
  'Pérdida W5 sin soporte del asset oficial — esperado: [0,0,0,0,0]',
  resumenPorAmbito.aggregate_array('perdida_w5_sin_soporte_oficial_ha')
);
print(
  'Recuperación W5 sin soporte del asset oficial — esperado: [0,0,0,0,0]',
  resumenPorAmbito.aggregate_array('recuperacion_w5_sin_soporte_oficial_ha')
);
print(
  'Pérdida robusta W5 por ámbito — ha-evento',
  resumenPorAmbito.aggregate_array('perdida_w5_robusta_evento_ha')
);
print(
  'Pérdida sensible solo W3 por ámbito — ha-evento',
  resumenPorAmbito.aggregate_array('perdida_solo_w3_evento_ha')
);
print(
  'Recuperación robusta W5 por ámbito — ha-evento',
  resumenPorAmbito.aggregate_array('recuperacion_w5_robusta_evento_ha')
);
print(
  'Recuperación sensible solo W3 por ámbito — ha-evento',
  resumenPorAmbito.aggregate_array('recuperacion_solo_w3_evento_ha')
);
print(
  'Eventos excluidos por ruptura conocida — ha-evento',
  resumenPorAmbito.aggregate_array('perdida_excluida_ruptura_evento_ha')
);
print(
  'Censura W3 — pérdidas 2023–2024, ha-evento',
  resumenPorAmbito.aggregate_array('censura_perdida_w3_ha')
);
print(
  'Censura W3 — recuperaciones 2023–2024, ha-evento',
  resumenPorAmbito.aggregate_array('censura_recuperacion_w3_ha')
);
print(
  'Censura W5 — pérdidas 2021–2024, ha-evento',
  resumenPorAmbito.aggregate_array('censura_perdida_w5_ha')
);
print(
  'Censura W5 — recuperaciones 2021–2024, ha-evento',
  resumenPorAmbito.aggregate_array('censura_recuperacion_w5_ha')
);

Map.centerObject(acr, 9);
Map.addLayer(
  perdida5FiltradaConteo.gt(0).selfMask().clip(acr.geometry()),
  {palette: ['7F0000']},
  'Pérdida robusta W5 — rupturas excluidas',
  true
);
Map.addLayer(
  perdidaSolo3Conteo.gt(0).selfMask().clip(acr.geometry()),
  {palette: ['FDAE61']},
  'Pérdida sensible — solo W3',
  false
);
Map.addLayer(
  recuperacion5Conteo.gt(0).selfMask().clip(acr.geometry()),
  {palette: ['006837']},
  'Recuperación robusta W5',
  false
);
Map.addLayer(
  recuperacionSolo3Conteo.gt(0).selfMask().clip(acr.geometry()),
  {palette: ['A6D96A']},
  'Recuperación sensible — solo W3',
  false
);
Map.addLayer(
  rupturasConocidas.selfMask().clip(acr.geometry()),
  {palette: ['FF00FF']},
  'Rupturas cartográficas excluidas',
  true
);
Map.addLayer(
  acr.style({color: '00FFFF', fillColor: '00000000', width: 2}),
  {},
  'Límites ACR',
  true
);

print('Lectura: W5 = señal cartográfica robusta; solo W3 = sensible.');
print('Los eventos censurados requieren años futuros y no son resultados estables.');
print('PASO 7C FINALIZADO — no se ejecutaron exportaciones.');
