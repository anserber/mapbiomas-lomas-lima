// PASO 7B — Piloto de eventos estables de la clase 70.
// Unidad: cinco ámbitos del ACR Sistema de Lomas de Lima.
// Periodo: 1985–2024.
// Ventanas estrictas de 3 y 5 años.
// Las rupturas cartográficas comprobadas en el Paso 6 se separan de las
// pérdidas filtradas. No se interpreta impacto ecológico.

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
var YEAR_START = 1985;
var YEAR_END = 2024;
var N_YEARS = YEAR_END - YEAR_START + 1;
var pixelHa = ee.Image.pixelArea().divide(10000);

function clase(year) {
  return clases.select('classification_' + year);
}

function loma(year) {
  return clase(year).eq(70);
}

// Devuelve 1 donde todos los años del intervalo cumplen el estado solicitado.
function todosEstado(yearStart, yearEnd, estado) {
  var resultado = ee.Image(1);
  for (var year = yearStart; year <= yearEnd; year++) {
    resultado = resultado.and(loma(year).eq(estado));
  }
  return resultado;
}

function construirEventos(ventana) {
  var perdidasConteo = ee.Image(0);
  var recuperacionesConteo = ee.Image(0);
  var perdidaYear = ee.Image(0);
  var recuperacionYear = ee.Image(0);

  // El año del evento es el primer año del nuevo estado.
  var primerYear = YEAR_START + ventana;
  var ultimoYear = YEAR_END - ventana + 1;

  for (var year = primerYear; year <= ultimoYear; year++) {
    var antesLoma = todosEstado(year - ventana, year - 1, 1);
    var antesNoLoma = todosEstado(year - ventana, year - 1, 0);
    var despuesLoma = todosEstado(year, year + ventana - 1, 1);
    var despuesNoLoma = todosEstado(year, year + ventana - 1, 0);

    var perdida = antesLoma.and(despuesNoLoma);
    var recuperacion = antesNoLoma.and(despuesLoma);

    perdidasConteo = perdidasConteo.add(perdida);
    recuperacionesConteo = recuperacionesConteo.add(recuperacion);
    perdidaYear = perdidaYear.where(perdida, year);
    recuperacionYear = recuperacionYear.where(recuperacion, year);
  }

  return {
    ventana: ventana,
    primerYear: primerYear,
    ultimoYear: ultimoYear,
    perdidaConteo: perdidasConteo.rename('perdida_conteo_' + ventana),
    recuperacionConteo:
      recuperacionesConteo.rename('recuperacion_conteo_' + ventana),
    perdidaMask:
      perdidasConteo.gt(0).rename('perdida_mask_' + ventana),
    recuperacionMask:
      recuperacionesConteo.gt(0).rename('recuperacion_mask_' + ventana),
    perdidaYear: perdidaYear.rename('perdida_year_' + ventana),
    recuperacionYear: recuperacionYear.rename('recuperacion_year_' + ventana)
  };
}

var eventos3 = construirEventos(3);
var eventos5 = construirEventos(5);

// Rupturas cartográficas comprobadas en el Paso 6.
var ancon = acr.filter(ee.Filter.eq('id_ambito', 'ancon'));
var carabayllo2 = acr.filter(ee.Filter.eq('id_ambito', 'carabayllo_2'));

var rupturaAncon = transiciones
  .select('transitions_2000_2001')
  .eq(7068)
  .clip(ancon.geometry())
  .rename('ruptura_ancon_70_68');

var transicionCarabayllo2 = transiciones
  .select('transitions_2014_2015');
var rupturaCarabayllo2 = transicionCarabayllo2.eq(7013)
  .or(transicionCarabayllo2.eq(7068))
  .clip(carabayllo2.geometry())
  .rename('ruptura_carabayllo2_70_13_68');

var rupturasConocidas = ee.ImageCollection.fromImages([
  rupturaAncon.unmask(0).rename('ruptura'),
  rupturaCarabayllo2.unmask(0).rename('ruptura')
]).max()
  .unmask(0)
  .rename('rupturas_conocidas');

function perdidaFiltrada(eventos) {
  var perdida = eventos.perdidaMask.rename('mask');
  var fueraRuptura = rupturasConocidas.eq(0).rename('mask');
  return perdida
    .and(fueraRuptura)
    .rename('perdida_filtrada_' + eventos.ventana);
}

var perdidaFiltrada3 = perdidaFiltrada(eventos3);
var perdidaFiltrada5 = perdidaFiltrada(eventos5);

// Sensibilidad: acuerdo y eventos adicionales de la ventana de 3 años.
var perdidaComun = eventos3.perdidaMask
  .and(eventos5.perdidaMask)
  .rename('perdida_comun_3_5');
var perdidaSolo3 = eventos3.perdidaMask
  .and(eventos5.perdidaMask.not())
  .rename('perdida_solo_3');
var recuperacionComun = eventos3.recuperacionMask
  .and(eventos5.recuperacionMask)
  .rename('recuperacion_comun_3_5');
var recuperacionSolo3 = eventos3.recuperacionMask
  .and(eventos5.recuperacionMask.not())
  .rename('recuperacion_solo_3');

// Bandas preponderadas para una sola reducción sobre los cinco ámbitos.
var metricasArea = pixelHa.rename('area_grilla_ha')
  .addBands(
    pixelHa.updateMask(eventos3.perdidaMask)
      .rename('perdida_raw_w3_ha')
  )
  .addBands(
    pixelHa.updateMask(perdidaFiltrada3)
      .rename('perdida_filtrada_w3_ha')
  )
  .addBands(
    pixelHa.updateMask(eventos3.recuperacionMask)
      .rename('recuperacion_w3_ha')
  )
  .addBands(
    pixelHa.multiply(eventos3.perdidaConteo)
      .rename('perdida_evento_w3_ha')
  )
  .addBands(
    pixelHa.multiply(eventos3.recuperacionConteo)
      .rename('recuperacion_evento_w3_ha')
  )
  .addBands(
    pixelHa.updateMask(eventos5.perdidaMask)
      .rename('perdida_raw_w5_ha')
  )
  .addBands(
    pixelHa.updateMask(perdidaFiltrada5)
      .rename('perdida_filtrada_w5_ha')
  )
  .addBands(
    pixelHa.updateMask(eventos5.recuperacionMask)
      .rename('recuperacion_w5_ha')
  )
  .addBands(
    pixelHa.multiply(eventos5.perdidaConteo)
      .rename('perdida_evento_w5_ha')
  )
  .addBands(
    pixelHa.multiply(eventos5.recuperacionConteo)
      .rename('recuperacion_evento_w5_ha')
  )
  .addBands(
    pixelHa.updateMask(rupturasConocidas)
      .rename('rupturas_conocidas_ha')
  )
  .addBands(
    pixelHa.updateMask(rupturaAncon)
      .rename('ruptura_ancon_ha')
  )
  .addBands(
    pixelHa.updateMask(rupturaCarabayllo2)
      .rename('ruptura_carabayllo2_ha')
  )
  .addBands(
    pixelHa.updateMask(
      eventos3.perdidaMask.and(rupturasConocidas)
    ).rename('perdida_w3_en_ruptura_ha')
  )
  .addBands(
    pixelHa.updateMask(
      eventos5.perdidaMask.and(rupturasConocidas)
    ).rename('perdida_w5_en_ruptura_ha')
  )
  .addBands(
    pixelHa.updateMask(perdidaComun).rename('perdida_comun_3_5_ha')
  )
  .addBands(
    pixelHa.updateMask(perdidaSolo3).rename('perdida_solo_3_ha')
  )
  .addBands(
    pixelHa.updateMask(recuperacionComun)
      .rename('recuperacion_comun_3_5_ha')
  )
  .addBands(
    pixelHa.updateMask(recuperacionSolo3)
      .rename('recuperacion_solo_3_ha')
  );

var resumenBruto = metricasArea.reduceRegions({
  collection: acr,
  reducer: ee.Reducer.sum(),
  scale: 30,
  tileScale: 4
});

function numero(feature, field) {
  return ee.Number(ee.Algorithms.If(
    feature.propertyNames().contains(field),
    feature.get(field),
    0
  ));
}

var resumen = resumenBruto.map(function(feature) {
  var area = numero(feature, 'area_grilla_ha');
  return ee.Feature(null, {
    id_ambito: feature.get('id_ambito'),
    nombre: feature.get('NOMBRE'),
    area_grilla_ha: area,
    perdida_raw_w3_ha: numero(feature, 'perdida_raw_w3_ha'),
    perdida_filtrada_w3_ha:
      numero(feature, 'perdida_filtrada_w3_ha'),
    recuperacion_w3_ha: numero(feature, 'recuperacion_w3_ha'),
    perdida_evento_w3_ha: numero(feature, 'perdida_evento_w3_ha'),
    recuperacion_evento_w3_ha:
      numero(feature, 'recuperacion_evento_w3_ha'),
    perdida_raw_w5_ha: numero(feature, 'perdida_raw_w5_ha'),
    perdida_filtrada_w5_ha:
      numero(feature, 'perdida_filtrada_w5_ha'),
    recuperacion_w5_ha: numero(feature, 'recuperacion_w5_ha'),
    perdida_evento_w5_ha: numero(feature, 'perdida_evento_w5_ha'),
    recuperacion_evento_w5_ha:
      numero(feature, 'recuperacion_evento_w5_ha'),
    rupturas_conocidas_ha: numero(feature, 'rupturas_conocidas_ha'),
    ruptura_ancon_ha: numero(feature, 'ruptura_ancon_ha'),
    ruptura_carabayllo2_ha:
      numero(feature, 'ruptura_carabayllo2_ha'),
    perdida_w3_en_ruptura_ha:
      numero(feature, 'perdida_w3_en_ruptura_ha'),
    perdida_w5_en_ruptura_ha:
      numero(feature, 'perdida_w5_en_ruptura_ha'),
    perdida_comun_3_5_ha: numero(feature, 'perdida_comun_3_5_ha'),
    perdida_solo_3_ha: numero(feature, 'perdida_solo_3_ha'),
    recuperacion_comun_3_5_ha:
      numero(feature, 'recuperacion_comun_3_5_ha'),
    recuperacion_solo_3_ha:
      numero(feature, 'recuperacion_solo_3_ha')
  });
});

var rangos = eventos3.perdidaConteo
  .addBands(eventos3.recuperacionConteo)
  .addBands(eventos5.perdidaConteo)
  .addBands(eventos5.recuperacionConteo)
  .reduceRegion({
    reducer: ee.Reducer.minMax(),
    geometry: acr.geometry(),
    scale: 30,
    maxPixels: 1e9,
    tileScale: 4
  });

print('PASO 7B — PILOTO DE EVENTOS ESTABLES');
print('Años de la serie — esperado: 40', N_YEARS);
print('Ámbitos — esperado: 5', acr.size());
print(
  'Ventana 3 — años evaluables; 2023–2024 quedan censurados a la derecha',
  [eventos3.primerYear, eventos3.ultimoYear]
);
print(
  'Ventana 5 — años evaluables; 2021–2024 quedan censurados a la derecha',
  [eventos5.primerYear, eventos5.ultimoYear]
);
print('Control de rangos de conteos', rangos);
print('Resumen por ámbito — esperado: 5 filas', resumen);
print('Orden de ámbitos', resumen.aggregate_array('id_ambito'));
print('Pérdida bruta W3 — ha',
  resumen.aggregate_array('perdida_raw_w3_ha'));
print('Pérdida W3 filtrada de rupturas conocidas — ha',
  resumen.aggregate_array('perdida_filtrada_w3_ha'));
print('Recuperación W3 — ha',
  resumen.aggregate_array('recuperacion_w3_ha'));
print('Pérdida bruta W5 — ha',
  resumen.aggregate_array('perdida_raw_w5_ha'));
print('Pérdida W5 filtrada de rupturas conocidas — ha',
  resumen.aggregate_array('perdida_filtrada_w5_ha'));
print('Recuperación W5 — ha',
  resumen.aggregate_array('recuperacion_w5_ha'));
print('Rupturas conocidas — ha',
  resumen.aggregate_array('rupturas_conocidas_ha'));
print('Ruptura Ancón 2000–2001, 70→68 — esperado ≈ 532.735 ha',
  resumen.aggregate_array('ruptura_ancon_ha'));
print('Ruptura Carabayllo 2 2014–2015, 70→13/68 — esperado ≈ 10.734 ha',
  resumen.aggregate_array('ruptura_carabayllo2_ha'));
print('Pérdida W3 intersectada con rupturas conocidas — ha',
  resumen.aggregate_array('perdida_w3_en_ruptura_ha'));
print('Pérdida W5 intersectada con rupturas conocidas — ha',
  resumen.aggregate_array('perdida_w5_en_ruptura_ha'));
print('Sensibilidad — pérdida común W3 y W5 — ha',
  resumen.aggregate_array('perdida_comun_3_5_ha'));
print('Sensibilidad — pérdida adicional solo W3 — ha',
  resumen.aggregate_array('perdida_solo_3_ha'));
print('Sensibilidad — recuperación común W3 y W5 — ha',
  resumen.aggregate_array('recuperacion_comun_3_5_ha'));
print('Sensibilidad — recuperación adicional solo W3 — ha',
  resumen.aggregate_array('recuperacion_solo_3_ha'));

Map.centerObject(acr, 9);
Map.addLayer(
  perdidaFiltrada3.selfMask().clip(acr.geometry()),
  {palette: ['D73027']},
  'Pérdida estable W3 — filtrada',
  true
);
Map.addLayer(
  eventos3.recuperacionMask.selfMask().clip(acr.geometry()),
  {palette: ['1A9850']},
  'Recuperación estable W3',
  false
);
Map.addLayer(
  perdidaFiltrada5.selfMask().clip(acr.geometry()),
  {palette: ['7F0000']},
  'Pérdida estable W5 — filtrada',
  false
);
Map.addLayer(
  eventos5.recuperacionMask.selfMask().clip(acr.geometry()),
  {palette: ['006837']},
  'Recuperación estable W5',
  false
);
Map.addLayer(
  rupturasConocidas.selfMask().clip(acr.geometry()),
  {palette: ['FF00FF']},
  'Rupturas cartográficas conocidas — Paso 6',
  true
);
Map.addLayer(
  acr.style({color: '00FFFF', fillColor: '00000000', width: 2}),
  {},
  'Límites ACR',
  true
);

print('Lectura obligatoria: “pérdida estable” es cambio cartográfico persistente');
print('de clase 70, no pérdida ecológica confirmada.');
print('PASO 7B FINALIZADO — no se ejecutaron exportaciones.');
