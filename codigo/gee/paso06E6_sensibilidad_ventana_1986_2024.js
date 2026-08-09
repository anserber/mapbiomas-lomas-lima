// =====================================================================
// PASO 6E6 — Sensibilidad de los indicadores de persistencia a la
// exclusion del year 1985, para las ocho unidades publicas.
// ---------------------------------------------------------------------
// Origen:
//   6E4 demostro que 1985 es una ruptura de inicio de serie: 9 escenas
//        Landsat y 56.7 % de nubes en Ancon; el candidato 68->70 de
//        1242.401 ha ingresa completo en 1986, permanece congelado hasta
//        1990 y tiene 0 % de persistencia hasta 2024.
//   6E5 confirmo que 1985 es el peor year de la serie en las tres
//        metricas de insumo a la vez, con un deficit de -29.3 % de la
//        clase 70 en el ACR respecto de la meseta 1986-1990.
//
// Decision tomada: 1985 queda excluido de todo calculo de cambio y la
// serie se reporta 1986-2024.
//
// Pregunta de este paso: ¿cuanto cambian `siempre 70` y `alguna vez 70`
// al pasar de la ventana de 40 years a la de 39 years?
//
// Prediccion previa, a partir de 6E4: en Ancon el cambio debe ser cero,
// porque las 1242.401 ha que 1985 no detecto tampoco son clase 70 en
// 2024 y por tanto nunca calificaron para `siempre 70`. El cambio total
// del ACR deberia quedar por debajo de 60 ha, es decir menos del 1.8 %.
// Si el resultado se aleja mucho de esa cota, hay que revisar antes de
// actualizar la tabla maestra.
//
// Unidades: 5 ambitos del ACR + 3 anillos disueltos del sistema.
// La KBA restringida queda fuera por diseño.
//
// No exporta por defecto. Ver la constante EXPORTAR_CSV.
// =====================================================================

// ---------------------------------------------------------------------
// 1. Assets y constantes
// ---------------------------------------------------------------------

var ASSET_ACR =
  'projects/mapbiomas-lomas-jhoreck/assets/inputs/acr_lomas_5_ambitos_gee';
var ASSET_SISTEMA =
  'projects/mapbiomas-lomas-jhoreck/assets/inputs/' +
  'anillos_sistema_periferia_externa_gee';
var ASSET_CLASES =
  'projects/mapbiomas-public/assets/peru/collection3/' +
  'mapbiomas_peru_collection3_integration_v1';

var YEAR_INICIO_40 = 1985;
var YEAR_INICIO_39 = 1986;
var YEAR_FIN = 2024;
var CLASE_LOMA = 70;

var EXPORTAR_CSV = false;

var clases = ee.Image(ASSET_CLASES);
var pixelHa = ee.Image.pixelArea().divide(10000);

function clase(year) {
  return clases.select('classification_' + year);
}

function loma(year) {
  return clase(year).eq(CLASE_LOMA);
}

// ---------------------------------------------------------------------
// 2. Unidades publicas, con el mismo unidad_id de la tabla maestra
// ---------------------------------------------------------------------

var acrUnidades = ee.FeatureCollection(ASSET_ACR).map(function(feature) {
  return ee.Feature(feature.geometry(), {
    unidad_id: ee.String('acr|').cat(ee.String(feature.get('id_ambito'))),
    dominio: 'ACR'
  });
});

var anillosUnidades = ee.FeatureCollection(ASSET_SISTEMA)
  .map(function(feature) {
    return ee.Feature(feature.geometry(), {
      unidad_id: ee.String('sistema|').cat(ee.String(feature.get('zona'))),
      dominio: 'ANILLO_SISTEMA'
    });
  });

var unidades = acrUnidades.merge(anillosUnidades);

// ---------------------------------------------------------------------
// 3. Conteo de years en clase 70, con las dos ventanas
// ---------------------------------------------------------------------

var suma40 = ee.Image(0);
for (var y = YEAR_INICIO_40; y <= YEAR_FIN; y++) {
  suma40 = suma40.add(loma(y));
}

// La ventana de 39 years es la de 40 menos el aporte de 1985.
var suma39 = suma40.subtract(loma(YEAR_INICIO_40));

var N_YEARS_40 = YEAR_FIN - YEAR_INICIO_40 + 1;  // 40
var N_YEARS_39 = YEAR_FIN - YEAR_INICIO_39 + 1;  // 39

var siempre40 = suma40.eq(N_YEARS_40);
var siempre39 = suma39.eq(N_YEARS_39);
var alguna40 = suma40.gt(0);
var alguna39 = suma39.gt(0);

// Pixeles que solo la exclusion de 1985 incorpora a `siempre 70`.
var ganadosPorExcluir1985 = siempre39.and(siempre40.not());

// ---------------------------------------------------------------------
// 4. Bandas de superficie
// ---------------------------------------------------------------------

var mascaraGrilla = clase(YEAR_FIN).gte(0);

var bandas = pixelHa.updateMask(mascaraGrilla)
  .rename('area_grilla_ha')
  .addBands(pixelHa.updateMask(siempre40).rename('siempre70_40y_ha'))
  .addBands(pixelHa.updateMask(siempre39).rename('siempre70_39y_ha'))
  .addBands(pixelHa.updateMask(alguna40).rename('alguna_vez70_40y_ha'))
  .addBands(pixelHa.updateMask(alguna39).rename('alguna_vez70_39y_ha'))
  .addBands(pixelHa.updateMask(ganadosPorExcluir1985)
    .rename('ganados_por_excluir_1985_ha'))
  .addBands(pixelHa.updateMask(loma(1985)).rename('clase70_1985_ha'))
  .addBands(pixelHa.updateMask(loma(1986)).rename('clase70_1986_ha'))
  .addBands(pixelHa.updateMask(loma(2024)).rename('clase70_2024_ha'));

// ---------------------------------------------------------------------
// 5. Reduccion unica sobre las ocho unidades
// ---------------------------------------------------------------------

var resultados = bandas.reduceRegions({
  collection: unidades,
  reducer: ee.Reducer.sum(),
  scale: 30,
  tileScale: 8
});

var resultadosOrdenados = resultados.map(function(feature) {
  var s40 = ee.Number(feature.get('siempre70_40y_ha'));
  var s39 = ee.Number(feature.get('siempre70_39y_ha'));
  var a40 = ee.Number(feature.get('alguna_vez70_40y_ha'));
  var a39 = ee.Number(feature.get('alguna_vez70_39y_ha'));
  var grilla = ee.Number(feature.get('area_grilla_ha'));

  return ee.Feature(null, {
    unidad_id: feature.get('unidad_id'),
    dominio: feature.get('dominio'),
    area_grilla_ha: grilla,
    clase70_1985_ha: feature.get('clase70_1985_ha'),
    clase70_1986_ha: feature.get('clase70_1986_ha'),
    clase70_2024_ha: feature.get('clase70_2024_ha'),
    siempre70_40y_ha: s40,
    siempre70_39y_ha: s39,
    siempre70_delta_ha: s39.subtract(s40),
    siempre70_delta_pct: ee.Algorithms.If(
      s40.gt(0), s39.subtract(s40).divide(s40).multiply(100), null),
    ganados_por_excluir_1985_ha:
      feature.get('ganados_por_excluir_1985_ha'),
    alguna_vez70_40y_ha: a40,
    alguna_vez70_39y_ha: a39,
    alguna_vez70_delta_ha: a39.subtract(a40),
    siempre70_39y_pct_grilla: ee.Algorithms.If(
      grilla.gt(0), s39.divide(grilla).multiply(100), null)
  });
});

// ---------------------------------------------------------------------
// 6. Salidas
// ---------------------------------------------------------------------

print('===== PASO 6E6 — SENSIBILIDAD A LA EXCLUSION DE 1985 =====');

print('A. VERIFICACION DE UNIDADES', ee.Dictionary({
  n_unidades: unidades.size(),
  n_esperado: 8,
  unidad_id: unidades.aggregate_array('unidad_id').sort(),
  years_ventana_40: N_YEARS_40,
  years_ventana_39: N_YEARS_39
}));

print('B. RESULTADOS POR UNIDAD', resultadosOrdenados);

print('C. TOTALES DEL ACR', ee.Dictionary({
  area_grilla_ha: resultadosOrdenados
    .filter(ee.Filter.eq('dominio', 'ACR'))
    .aggregate_sum('area_grilla_ha'),
  area_grilla_esperada_tabla_maestra_ha: 13468.753,
  siempre70_40y_ha: resultadosOrdenados
    .filter(ee.Filter.eq('dominio', 'ACR'))
    .aggregate_sum('siempre70_40y_ha'),
  siempre70_40y_esperada_tabla_maestra_ha: 3542.972,
  siempre70_39y_ha: resultadosOrdenados
    .filter(ee.Filter.eq('dominio', 'ACR'))
    .aggregate_sum('siempre70_39y_ha'),
  ganados_por_excluir_1985_ha: resultadosOrdenados
    .filter(ee.Filter.eq('dominio', 'ACR'))
    .aggregate_sum('ganados_por_excluir_1985_ha'),
  clase70_1985_ha: resultadosOrdenados
    .filter(ee.Filter.eq('dominio', 'ACR'))
    .aggregate_sum('clase70_1985_ha'),
  clase70_1985_esperada_serie_ha: 3988.6,
  clase70_1986_ha: resultadosOrdenados
    .filter(ee.Filter.eq('dominio', 'ACR'))
    .aggregate_sum('clase70_1986_ha'),
  clase70_1986_esperada_serie_ha: 5262.2,
  clase70_2024_ha: resultadosOrdenados
    .filter(ee.Filter.eq('dominio', 'ACR'))
    .aggregate_sum('clase70_2024_ha'),
  clase70_2024_esperada_tabla_maestra_ha: 3547.650
}));

print('D. TOTALES DE LOS ANILLOS DISUELTOS', ee.Dictionary({
  area_grilla_ha: resultadosOrdenados
    .filter(ee.Filter.eq('dominio', 'ANILLO_SISTEMA'))
    .aggregate_sum('area_grilla_ha'),
  area_grilla_esperada_tabla_maestra_ha: 22846.929,
  siempre70_40y_ha: resultadosOrdenados
    .filter(ee.Filter.eq('dominio', 'ANILLO_SISTEMA'))
    .aggregate_sum('siempre70_40y_ha'),
  siempre70_39y_ha: resultadosOrdenados
    .filter(ee.Filter.eq('dominio', 'ANILLO_SISTEMA'))
    .aggregate_sum('siempre70_39y_ha'),
  ganados_por_excluir_1985_ha: resultadosOrdenados
    .filter(ee.Filter.eq('dominio', 'ANILLO_SISTEMA'))
    .aggregate_sum('ganados_por_excluir_1985_ha')
}));

print('E. LECTURA', ee.Dictionary({
  prediccion_ancon: 'siempre70_delta_ha debe ser 0.000 en acr|ancon. ' +
    'Las 1242.401 ha que 1985 no detecto tienen 0 % de persistencia ' +
    'hasta 2024, segun el paso 6E4.',
  cota_esperada_acr: 'siempre70_delta_ha del ACR por debajo de 60 ha, ' +
    'equivalente a menos del 1.8 % sobre 3542.972 ha.',
  si_se_cumple: 'Adoptar la ventana 1986-2024 como primaria y reportar ' +
    'la de 1985-2024 como sensibilidad. Actualizar la tabla maestra.',
  si_no_se_cumple: 'Detener la actualizacion y revisar antes de tocar ' +
    'la tabla maestra y las figuras F02.',
  nota: 'alguna_vez70 tambien puede bajar al excluir 1985, porque ' +
    'pierde los pixeles que solo fueron clase 70 en ese year.'
}));

// ---------------------------------------------------------------------
// 7. Exportacion opcional
// ---------------------------------------------------------------------

if (EXPORTAR_CSV) {
  Export.table.toDrive({
    collection: resultadosOrdenados,
    description: 'paso06E6_sensibilidad_ventana_1986_2024',
    fileNamePrefix: 'paso06E6_sensibilidad_ventana_1986_2024',
    fileFormat: 'CSV',
    selectors: [
      'unidad_id', 'dominio', 'area_grilla_ha',
      'clase70_1985_ha', 'clase70_1986_ha', 'clase70_2024_ha',
      'siempre70_40y_ha', 'siempre70_39y_ha', 'siempre70_delta_ha',
      'siempre70_delta_pct', 'ganados_por_excluir_1985_ha',
      'alguna_vez70_40y_ha', 'alguna_vez70_39y_ha',
      'alguna_vez70_delta_ha', 'siempre70_39y_pct_grilla'
    ]
  });
  print('EXPORTACION ACTIVADA. Revisar la pestaña Tasks.');
} else {
  print('No se ejecutaron exportaciones. ' +
    'Cambiar EXPORTAR_CSV a true si se prefiere el CSV.');
}

Map.centerObject(unidades, 10);
Map.addLayer(
  ee.FeatureCollection(ASSET_SISTEMA)
    .style({color: 'FFA500', fillColor: '00000000', width: 1}),
  {}, 'Anillos disueltos', false
);
Map.addLayer(
  ee.FeatureCollection(ASSET_ACR)
    .style({color: '00FFFF', fillColor: '00000000', width: 2}),
  {}, 'Cinco ambitos del ACR'
);
Map.addLayer(
  ganadosPorExcluir1985.selfMask(), {palette: ['FF00FF']},
  'Pixeles ganados al excluir 1985', false
);
