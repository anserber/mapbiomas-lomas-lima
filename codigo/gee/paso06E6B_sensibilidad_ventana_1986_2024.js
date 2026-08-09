// =====================================================================
// PASO 6E6-B — Sensibilidad de los indicadores de persistencia a la
// exclusion del year 1985. Version corregida de paso06E6.
// ---------------------------------------------------------------------
// Motivo de la correccion:
//   La version 6E6 mezclaba con merge() la coleccion del ACR y la de
//   anillos, que provienen de assets distintos y con esquemas de
//   propiedades distintos. Al materializar esa mezcla dentro de
//   reduceRegions, GEE devolvio:
//     "Collection.loadTable: Asset ... does not exist or doesn't allow
//      this operation"
//   El asset si existe: el paso 6E4 lo leyo correctamente. El fallo es
//   de la mezcla, no del asset.
//
//   Cambios respecto de 6E6, siguiendo el patron ya probado en 7D2:
//     1. Sin merge. Dos reduceRegions independientes.
//     2. feature.set() en lugar de reconstruir ee.Feature().
//     3. pixelHa.multiply(mascara) en lugar de updateMask().
//     4. tileScale 4 en lugar de 8.
//     5. Bloque de diagnostico previo que verifica cada asset por
//        separado antes de cualquier reduccion.
//
// Contexto metodologico:
//   6E4 demostro que 1985 es una ruptura de inicio de serie en Ancon.
//   6E5 confirmo que 1985 es el peor year de la serie en las tres
//       metricas de insumo a la vez, con -29.3 % de clase 70 en el ACR.
//   Decision tomada: 1985 excluido de todo calculo de cambio.
//
// Pregunta: ¿cuanto cambian `siempre 70` y `alguna vez 70` al pasar de
// la ventana de 40 years a la de 39 years?
//
// Predicciones hechas ANTES de ejecutar:
//   P1. siempre70_delta_ha en acr|ancon debe ser 0.000, porque las
//       1242.401 ha que 1985 no detecto tienen 0 % de persistencia
//       hasta 2024 segun 6E4.
//   P2. El delta total del ACR debe quedar por debajo de 60 ha, es
//       decir menos del 1.8 % sobre 3542.972 ha.
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
var N_YEARS_40 = YEAR_FIN - YEAR_INICIO_40 + 1;  // 40
var N_YEARS_39 = YEAR_FIN - YEAR_INICIO_39 + 1;  // 39

var EXPORTAR_CSV = false;

var clases = ee.Image(ASSET_CLASES);
var pixelHa = ee.Image.pixelArea().divide(10000);

var rawAcr = ee.FeatureCollection(ASSET_ACR);
var rawSistema = ee.FeatureCollection(ASSET_SISTEMA);

function clase(year) {
  return clases.select('classification_' + year);
}

function loma(year) {
  return clase(year).eq(CLASE_LOMA);
}

// ---------------------------------------------------------------------
// 2. Diagnostico previo de los assets, antes de cualquier reduccion
// ---------------------------------------------------------------------

print('===== PASO 6E6-B — SENSIBILIDAD A LA EXCLUSION DE 1985 =====');

print('A. DIAGNOSTICO DE ASSETS', ee.Dictionary({
  acr_n_objetos: rawAcr.size(),
  acr_n_esperado: 5,
  acr_propiedades: ee.Feature(rawAcr.first()).propertyNames().sort(),
  acr_id_ambito: rawAcr.aggregate_array('id_ambito').sort(),
  sistema_n_objetos: rawSistema.size(),
  sistema_n_esperado: 3,
  sistema_propiedades: ee.Feature(rawSistema.first()).propertyNames().sort(),
  sistema_zona: rawSistema.aggregate_array('zona').sort()
}));

// ---------------------------------------------------------------------
// 3. Unidades, con el mismo unidad_id de la tabla maestra
// ---------------------------------------------------------------------

var unidadesAcr = rawAcr.map(function(feature) {
  return feature.set({
    unidad_id: ee.String('acr|').cat(ee.String(feature.get('id_ambito'))),
    dominio: 'ACR'
  });
});

var unidadesSistema = rawSistema.map(function(feature) {
  return feature.set({
    unidad_id: ee.String('sistema|').cat(ee.String(feature.get('zona'))),
    dominio: 'ANILLO_SISTEMA'
  });
});

// ---------------------------------------------------------------------
// 4. Conteo de years en clase 70, con las dos ventanas
// ---------------------------------------------------------------------

var suma40 = ee.Image(0);
for (var y = YEAR_INICIO_40; y <= YEAR_FIN; y++) {
  suma40 = suma40.add(loma(y));
}

// La ventana de 39 years es la de 40 menos el aporte de 1985.
var suma39 = suma40.subtract(loma(YEAR_INICIO_40));

var siempre40 = suma40.eq(N_YEARS_40);
var siempre39 = suma39.eq(N_YEARS_39);
var alguna40 = suma40.gt(0);
var alguna39 = suma39.gt(0);

// Pixeles que solo la exclusion de 1985 incorpora a `siempre 70`.
var ganados = siempre39.and(siempre40.not());

var mascaraGrilla = clase(YEAR_FIN).gte(0);

// ---------------------------------------------------------------------
// 5. Bandas de superficie, patron pixelHa.multiply() como en 7D2
// ---------------------------------------------------------------------

var metricas = pixelHa.multiply(mascaraGrilla).rename('area_grilla_ha')
  .addBands(pixelHa.multiply(siempre40).rename('siempre70_40y_ha'))
  .addBands(pixelHa.multiply(siempre39).rename('siempre70_39y_ha'))
  .addBands(pixelHa.multiply(alguna40).rename('alguna_vez70_40y_ha'))
  .addBands(pixelHa.multiply(alguna39).rename('alguna_vez70_39y_ha'))
  .addBands(pixelHa.multiply(ganados).rename('ganados_por_excluir_1985_ha'))
  .addBands(pixelHa.multiply(loma(1985)).rename('clase70_1985_ha'))
  .addBands(pixelHa.multiply(loma(1986)).rename('clase70_1986_ha'))
  .addBands(pixelHa.multiply(loma(2024)).rename('clase70_2024_ha'));

// ---------------------------------------------------------------------
// 6. Dos reducciones independientes, sin merge
// ---------------------------------------------------------------------

function reducir(coleccion) {
  return metricas.reduceRegions({
    collection: coleccion,
    reducer: ee.Reducer.sum(),
    scale: 30,
    tileScale: 4
  });
}

function numero(feature, campo) {
  return ee.Number(ee.Algorithms.If(
    feature.propertyNames().contains(campo),
    feature.get(campo),
    0
  ));
}

function ordenar(coleccion) {
  return coleccion.map(function(feature) {
    var s40 = numero(feature, 'siempre70_40y_ha');
    var s39 = numero(feature, 'siempre70_39y_ha');
    var a40 = numero(feature, 'alguna_vez70_40y_ha');
    var a39 = numero(feature, 'alguna_vez70_39y_ha');
    var grilla = numero(feature, 'area_grilla_ha');

    return ee.Feature(null, {
      unidad_id: feature.get('unidad_id'),
      dominio: feature.get('dominio'),
      area_grilla_ha: grilla,
      clase70_1985_ha: numero(feature, 'clase70_1985_ha'),
      clase70_1986_ha: numero(feature, 'clase70_1986_ha'),
      clase70_2024_ha: numero(feature, 'clase70_2024_ha'),
      siempre70_40y_ha: s40,
      siempre70_39y_ha: s39,
      siempre70_delta_ha: s39.subtract(s40),
      siempre70_delta_pct: ee.Algorithms.If(
        s40.gt(0), s39.subtract(s40).divide(s40).multiply(100), null),
      ganados_por_excluir_1985_ha:
        numero(feature, 'ganados_por_excluir_1985_ha'),
      alguna_vez70_40y_ha: a40,
      alguna_vez70_39y_ha: a39,
      alguna_vez70_delta_ha: a39.subtract(a40),
      siempre70_39y_pct_grilla: ee.Algorithms.If(
        grilla.gt(0), s39.divide(grilla).multiply(100), null)
    });
  });
}

var resultadoAcr = ordenar(reducir(unidadesAcr));
var resultadoSistema = ordenar(reducir(unidadesSistema));

// ---------------------------------------------------------------------
// 7. Salidas
// ---------------------------------------------------------------------

print('B. RESULTADOS POR AMBITO DEL ACR', resultadoAcr);

print('C. RESULTADOS POR ANILLO DISUELTO', resultadoSistema);

print('D. TOTALES DEL ACR', ee.Dictionary({
  area_grilla_ha: resultadoAcr.aggregate_sum('area_grilla_ha'),
  area_grilla_esperada_ha: 13468.753,
  clase70_1985_ha: resultadoAcr.aggregate_sum('clase70_1985_ha'),
  clase70_1985_esperada_ha: 3988.6,
  clase70_1986_ha: resultadoAcr.aggregate_sum('clase70_1986_ha'),
  clase70_1986_esperada_ha: 5262.2,
  clase70_2024_ha: resultadoAcr.aggregate_sum('clase70_2024_ha'),
  clase70_2024_esperada_ha: 3547.650,
  siempre70_40y_ha: resultadoAcr.aggregate_sum('siempre70_40y_ha'),
  siempre70_40y_esperada_ha: 3542.972,
  siempre70_39y_ha: resultadoAcr.aggregate_sum('siempre70_39y_ha'),
  siempre70_delta_ha: resultadoAcr.aggregate_sum('siempre70_delta_ha'),
  ganados_por_excluir_1985_ha:
    resultadoAcr.aggregate_sum('ganados_por_excluir_1985_ha'),
  alguna_vez70_40y_ha: resultadoAcr.aggregate_sum('alguna_vez70_40y_ha'),
  alguna_vez70_40y_esperada_ha: 6587.570,
  alguna_vez70_39y_ha: resultadoAcr.aggregate_sum('alguna_vez70_39y_ha'),
  alguna_vez70_delta_ha:
    resultadoAcr.aggregate_sum('alguna_vez70_delta_ha')
}));

print('E. TOTALES DE LOS ANILLOS DISUELTOS', ee.Dictionary({
  area_grilla_ha: resultadoSistema.aggregate_sum('area_grilla_ha'),
  area_grilla_esperada_ha: 22846.929,
  siempre70_40y_ha: resultadoSistema.aggregate_sum('siempre70_40y_ha'),
  siempre70_39y_ha: resultadoSistema.aggregate_sum('siempre70_39y_ha'),
  siempre70_delta_ha:
    resultadoSistema.aggregate_sum('siempre70_delta_ha'),
  ganados_por_excluir_1985_ha:
    resultadoSistema.aggregate_sum('ganados_por_excluir_1985_ha'),
  alguna_vez70_40y_ha:
    resultadoSistema.aggregate_sum('alguna_vez70_40y_ha'),
  alguna_vez70_39y_ha:
    resultadoSistema.aggregate_sum('alguna_vez70_39y_ha')
}));

print('F. LECTURA', ee.Dictionary({
  P1: 'siempre70_delta_ha debe ser 0.000 en acr|ancon.',
  P2: 'siempre70_delta_ha del ACR por debajo de 60 ha, menos del 1.8 %.',
  si_se_cumplen: 'Adoptar la ventana 1986-2024 como primaria y reportar ' +
    'la de 1985-2024 como sensibilidad. Actualizar la tabla maestra.',
  si_no_se_cumplen: 'Detener la actualizacion y revisar antes de tocar ' +
    'la tabla maestra y la figura F02.',
  nota: 'alguna_vez70 solo puede bajar al excluir 1985, porque pierde ' +
    'los pixeles que unicamente fueron clase 70 en ese year.'
}));

// ---------------------------------------------------------------------
// 8. Exportacion opcional
// ---------------------------------------------------------------------

var SELECTORES = [
  'unidad_id', 'dominio', 'area_grilla_ha',
  'clase70_1985_ha', 'clase70_1986_ha', 'clase70_2024_ha',
  'siempre70_40y_ha', 'siempre70_39y_ha', 'siempre70_delta_ha',
  'siempre70_delta_pct', 'ganados_por_excluir_1985_ha',
  'alguna_vez70_40y_ha', 'alguna_vez70_39y_ha',
  'alguna_vez70_delta_ha', 'siempre70_39y_pct_grilla'
];

if (EXPORTAR_CSV) {
  Export.table.toDrive({
    collection: resultadoAcr,
    description: 'paso06E6B_sensibilidad_acr_1986_2024',
    fileNamePrefix: 'paso06E6B_sensibilidad_acr_1986_2024',
    fileFormat: 'CSV',
    selectors: SELECTORES
  });
  Export.table.toDrive({
    collection: resultadoSistema,
    description: 'paso06E6B_sensibilidad_anillos_1986_2024',
    fileNamePrefix: 'paso06E6B_sensibilidad_anillos_1986_2024',
    fileFormat: 'CSV',
    selectors: SELECTORES
  });
  print('EXPORTACION ACTIVADA. Dos tareas en la pestaña Tasks.');
} else {
  print('No se ejecutaron exportaciones. ' +
    'Cambiar EXPORTAR_CSV a true si se prefiere el CSV.');
}

// ---------------------------------------------------------------------
// 9. Contexto visual
// ---------------------------------------------------------------------

Map.centerObject(rawAcr, 10);
Map.addLayer(
  rawSistema.style({color: 'FFA500', fillColor: '00000000', width: 1}),
  {}, 'Anillos disueltos', false
);
Map.addLayer(
  rawAcr.style({color: '00FFFF', fillColor: '00000000', width: 2}),
  {}, 'Cinco ambitos del ACR'
);
Map.addLayer(
  ganados.selfMask(), {palette: ['FF00FF']},
  'Pixeles ganados al excluir 1985', false
);
