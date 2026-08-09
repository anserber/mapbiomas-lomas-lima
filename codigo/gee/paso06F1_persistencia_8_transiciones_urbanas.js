// PASO 6F1 — Persistencia de ocho transiciones urbanas pendientes.
// Versión corregida: reduce por periodo y por geometría de cada unidad.
// El candidato usa directamente el asset oficial de transiciones.
// No exporta archivos ni confirma impactos ecológicos automáticamente.

var ASSET_ACR =
  'projects/mapbiomas-lomas-jhoreck/assets/inputs/acr_lomas_5_ambitos_gee';
var ASSET_ANILLOS =
  'projects/mapbiomas-lomas-jhoreck/assets/inputs/' +
  'anillos_sistema_periferia_externa_gee';
var ASSET_CLASES =
  'projects/mapbiomas-public/assets/peru/collection3/' +
  'mapbiomas_peru_collection3_integration_v1';
var ASSET_TRANSICIONES =
  'projects/mapbiomas-public/assets/peru/collection3/' +
  'mapbiomas_peru_collection3_transitions_v1';

var acr = ee.FeatureCollection(ASSET_ACR);
var anillos = ee.FeatureCollection(ASSET_ANILLOS);
var clases = ee.Image(ASSET_CLASES);
var transiciones = ee.Image(ASSET_TRANSICIONES);

var casos = [
  {
    id: 'CV-009', nivel: 'sistema', id_ambito: 'sistema', zona: '0_500',
    nombre: 'Sistema disuelto 0–500 m',
    inicio: 2021, fin: 2022, esperado_ha: 12.932611665182671
  },
  {
    id: 'CV-012', nivel: 'sistema', id_ambito: 'sistema', zona: '0_500',
    nombre: 'Sistema disuelto 0–500 m',
    inicio: 2014, fin: 2015, esperado_ha: 4.158759704757392
  },
  {
    id: 'CV-014', nivel: 'sistema', id_ambito: 'sistema',
    zona: '500_1000', nombre: 'Sistema disuelto 500–1,000 m',
    inicio: 2021, fin: 2022, esperado_ha: 2.697715224441827
  },
  {
    id: 'CV-017', nivel: 'acr', id_ambito: 'villa_maria',
    zona: 'interior_acr', nombre: 'Lomas de Villa María',
    inicio: 2022, fin: 2023, esperado_ha: 1.5217137626618031
  },
  {
    id: 'CV-018', nivel: 'acr', id_ambito: 'amancaes',
    zona: 'interior_acr', nombre: 'Lomas de Amancaes',
    inicio: 2021, fin: 2022, esperado_ha: 1.093521100212546
  },
  {
    id: 'CV-023', nivel: 'acr', id_ambito: 'amancaes',
    zona: 'interior_acr', nombre: 'Lomas de Amancaes',
    inicio: 2019, fin: 2020, esperado_ha: 0.2364026879882812
  },
  {
    id: 'CV-024', nivel: 'acr', id_ambito: 'villa_maria',
    zona: 'interior_acr', nombre: 'Lomas de Villa María',
    inicio: 2019, fin: 2020, esperado_ha: 0.2044056182502297
  },
  {
    id: 'CV-027', nivel: 'acr', id_ambito: 'amancaes',
    zona: 'interior_acr', nombre: 'Lomas de Amancaes',
    inicio: 2022, fin: 2023, esperado_ha: 0.1444494666724111
  }
];

function unidad(caso) {
  return caso.nivel === 'acr'
    ? ee.Feature(acr.filter(
        ee.Filter.eq('id_ambito', caso.id_ambito)
      ).first())
    : ee.Feature(anillos.filter(
        ee.Filter.eq('zona', caso.zona)
      ).first());
}

function clase(year) {
  return clases.select('classification_' + year);
}

function coleccionCasos(lista) {
  return ee.FeatureCollection(lista.map(function(caso) {
    return ee.Feature(unidad(caso).geometry(), {
      id_control: caso.id,
      nivel: caso.nivel,
      id_ambito: caso.id_ambito,
      zona: caso.zona,
      nombre: caso.nombre,
      year_start: caso.inicio,
      year_end: caso.fin,
      area_esperada_ha: caso.esperado_ha
    });
  }));
}

function reducirPeriodo(inicio, fin, listaCasos) {
  var banda = 'transitions_' + inicio + '_' + fin;
  var candidato = transiciones.select(banda).eq(7024);
  var finCorto = Math.min(fin + 2, 2024);
  var persisteCorto = candidato;
  var persisteHasta2024 = candidato;

  for (var year = fin + 1; year <= finCorto; year++) {
    persisteCorto = persisteCorto.and(clase(year).eq(24));
  }
  for (var yearAll = fin + 1; yearAll <= 2024; yearAll++) {
    persisteHasta2024 =
      persisteHasta2024.and(clase(yearAll).eq(24));
  }

  var en2024 = candidato.and(clase(2024).eq(24));
  var pixelHa = ee.Image.pixelArea().divide(10000);
  var metricas = pixelHa.updateMask(candidato)
    .rename('area_candidata_ha')
    .addBands(
      pixelHa.updateMask(persisteCorto)
        .rename('persiste_corto_ha')
    )
    .addBands(
      pixelHa.updateMask(persisteHasta2024)
        .rename('persiste_continuamente_hasta_2024_ha')
    )
    .addBands(
      pixelHa.updateMask(en2024).rename('clase24_en_2024_ha')
    );

  var reducidos = metricas.reduceRegions({
    collection: coleccionCasos(listaCasos),
    reducer: ee.Reducer.sum(),
    scale: 30,
    tileScale: 4
  });

  return reducidos.map(function(feature) {
    function numeroPropiedad(nombre) {
      var valor = feature.get(nombre);
      return ee.Number(ee.Algorithms.If(
        ee.Algorithms.IsEqual(valor, null),
        0,
        valor
      ));
    }

    var candidatoHa = numeroPropiedad('area_candidata_ha');
    var esperado = ee.Number(feature.get('area_esperada_ha'));
    var corto = numeroPropiedad('persiste_corto_ha');
    var continuo = numeroPropiedad(
      'persiste_continuamente_hasta_2024_ha'
    );
    var clase24 = numeroPropiedad('clase24_en_2024_ha');

    return feature.set({
      years_post_corto: Math.min(2, 2024 - fin),
      diferencia_area_ha: candidatoHa.subtract(esperado),
      diferencia_area_abs_pct: candidatoHa
        .subtract(esperado).abs().divide(esperado).multiply(100),
      persiste_corto_pct:
        corto.divide(candidatoHa).multiply(100),
      persiste_continuamente_hasta_2024_pct:
        continuo.divide(candidatoHa).multiply(100),
      clase24_en_2024_pct:
        clase24.divide(candidatoHa).multiply(100)
    });
  });
}

function filtrarCasos(inicio, fin) {
  return casos.filter(function(caso) {
    return caso.inicio === inicio && caso.fin === fin;
  });
}

// Cuatro reducciones agrupadas, ninguna dentro de un map servidor.
var bloque2014 = reducirPeriodo(
  2014, 2015, filtrarCasos(2014, 2015)
);
var bloque2019 = reducirPeriodo(
  2019, 2020, filtrarCasos(2019, 2020)
);
var bloque2021 = reducirPeriodo(
  2021, 2022, filtrarCasos(2021, 2022)
);
var bloque2022 = reducirPeriodo(
  2022, 2023, filtrarCasos(2022, 2023)
);

var resultados = bloque2014
  .merge(bloque2019)
  .merge(bloque2021)
  .merge(bloque2022)
  .sort('id_control');

print('PASO 6F1 — RESULTADO CORREGIDO', ee.Dictionary({
  registros: resultados.size(),
  orden_controles: resultados.aggregate_array('id_control'),
  area_candidata_ha: resultados.aggregate_array('area_candidata_ha'),
  diferencia_area_abs_pct:
    resultados.aggregate_array('diferencia_area_abs_pct'),
  diferencia_area_abs_pct_max:
    resultados.aggregate_max('diferencia_area_abs_pct'),
  persistencia_corta_pct:
    resultados.aggregate_array('persiste_corto_pct'),
  persistencia_continua_hasta_2024_pct:
    resultados.aggregate_array(
      'persiste_continuamente_hasta_2024_pct'
    ),
  clase24_en_2024_pct:
    resultados.aggregate_array('clase24_en_2024_pct'),
  tabla: resultados
}));

Map.centerObject(acr, 9);
Map.addLayer(
  acr.style({color: '00FFFF', fillColor: '00000000', width: 2}),
  {},
  'Cinco ámbitos del ACR'
);
Map.addLayer(
  anillos.style({color: 'FFFF00', fillColor: '00000000', width: 1}),
  {},
  'Anillos externos',
  false
);

print('No se ejecutaron exportaciones.');
