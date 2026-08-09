// =====================================================================
// PASO 6E5 — Auditoria del insumo Landsat de los mosaicos oficiales,
// 1985-2024, sobre los cinco ambitos del ACR Sistema de Lomas de Lima.
// ---------------------------------------------------------------------
// Origen: el paso 6E4 demostro que la ruptura 1985-1986 de Ancon se
// explica por la pobreza del mosaico de inicio de serie (9 escenas y
// 56.7 % de nubes en 1985 frente a 27 en 1986 y 57 en 1988).
//
// Pregunta de este paso: ¿esa relacion se sostiene a lo largo de los
// 40 years, o 1985 es un caso aislado?
//
// Diseño: auditoria de METADATOS unicamente. No hay reduceRegion, no se
// tocan pixeles y no se recalcula ninguna superficie. Las superficies
// anuales de clase 70 ya estan validadas en:
//   04_extraccion_series/02_resultados/00_raw/
//   serie_indicadores_acr_1985_2024.csv
// El cruce entre insumo y superficie se hace fuera de GEE, en Python.
//
// Colecciones de mosaicos, segun paso06E1B_resolver_versiones_mosaicos:
//   1985-2021 -> projects/nexgenmap/MapBiomas2/LANDSAT/PANAMAZON/mosaics-2
//   2022-2024 -> projects/mapbiomas-raisg/MOSAICOS/mosaics-2
//
// No exporta por defecto. Ver la constante EXPORTAR_CSV.
// =====================================================================

// ---------------------------------------------------------------------
// 1. Assets y constantes
// ---------------------------------------------------------------------

var ASSET_ACR =
  'projects/mapbiomas-lomas-jhoreck/assets/inputs/acr_lomas_5_ambitos_gee';
var MOSAICOS_1985_2021 =
  'projects/nexgenmap/MapBiomas2/LANDSAT/PANAMAZON/mosaics-2';
var MOSAICOS_2022_2024 =
  'projects/mapbiomas-raisg/MOSAICOS/mosaics-2';

var YEAR_INICIO = 1985;
var YEAR_FIN = 2024;
var YEAR_CORTE_COLECCION = 2021;
var REGIONES = [703, 704, 705];

// Poner en true solo si copiar 40 years desde la consola resulta
// incomodo. Genera una tarea en la pestaña Tasks; no altera resultados.
var EXPORTAR_CSV = false;

var acr = ee.FeatureCollection(ASSET_ACR);
var contexto = acr.geometry().buffer(1000);
var years = ee.List.sequence(YEAR_INICIO, YEAR_FIN);

// ---------------------------------------------------------------------
// 2. Coleccion unificada, sin solapamiento entre las dos fuentes
// ---------------------------------------------------------------------

var antiguos = ee.ImageCollection(MOSAICOS_1985_2021)
  .filterBounds(contexto)
  .filter(ee.Filter.lte('year', YEAR_CORTE_COLECCION));

var recientes = ee.ImageCollection(MOSAICOS_2022_2024)
  .filterBounds(contexto)
  .filter(ee.Filter.gt('year', YEAR_CORTE_COLECCION));

var todos = antiguos.merge(recientes);

function subsetAnual(year) {
  return todos.filter(ee.Filter.eq('year', year));
}

function subsetAnualRegion(year, region) {
  return subsetAnual(year).filter(ee.Filter.eq('region_code', region));
}

// Devuelve null cuando la coleccion esta vacia, en lugar de fallar.
function reducirSeguro(coleccion, propiedad, reducer) {
  var valores = coleccion.aggregate_array(propiedad);
  return ee.Algorithms.If(
    valores.size().gt(0),
    valores.reduce(reducer),
    null
  );
}

// ---------------------------------------------------------------------
// 3. Series agregadas para el conjunto del ACR
// ---------------------------------------------------------------------

var serieTeselas = years.map(function(year) {
  return subsetAnual(year).size();
});

var serieNimagesTotal = years.map(function(year) {
  return reducirSeguro(subsetAnual(year), 'nimages', ee.Reducer.sum());
});

var serieNimagesMin = years.map(function(year) {
  return reducirSeguro(subsetAnual(year), 'nimages', ee.Reducer.min());
});

var serieNimagesMax = years.map(function(year) {
  return reducirSeguro(subsetAnual(year), 'nimages', ee.Reducer.max());
});

var serieCloudMedio = years.map(function(year) {
  return reducirSeguro(subsetAnual(year), 'cloud_cover', ee.Reducer.mean());
});

var serieCloudMax = years.map(function(year) {
  return reducirSeguro(subsetAnual(year), 'cloud_cover', ee.Reducer.max());
});

var serieSatelites = years.map(function(year) {
  return subsetAnual(year).aggregate_array('satellite').distinct().sort();
});

var serieVersiones = years.map(function(year) {
  return subsetAnual(year).aggregate_array('version').distinct().sort();
});

// ---------------------------------------------------------------------
// 4. Series por region, para asociar cada ambito con su tesela
// ---------------------------------------------------------------------

function serieNimagesRegion(region) {
  return years.map(function(year) {
    return reducirSeguro(
      subsetAnualRegion(year, region), 'nimages', ee.Reducer.sum()
    );
  });
}

function serieCloudRegion(region) {
  return years.map(function(year) {
    return reducirSeguro(
      subsetAnualRegion(year, region), 'cloud_cover', ee.Reducer.mean()
    );
  });
}

// ---------------------------------------------------------------------
// 5. Correspondencia entre ambitos y regiones de mosaico
// ---------------------------------------------------------------------

var ambitosRegiones = acr.map(function(feature) {
  var geom = feature.geometry();
  var regionesQueIntersecan = todos
    .filterBounds(geom)
    .aggregate_array('region_code')
    .distinct()
    .sort();
  return ee.Feature(null, {
    id_ambito: feature.get('id_ambito'),
    regiones: regionesQueIntersecan
  });
});

// ---------------------------------------------------------------------
// 6. Salidas
// ---------------------------------------------------------------------

print('===== PASO 6E5 — INSUMO LANDSAT 1985-2024 =====');

print('A. VERIFICACION DE LA COLECCION', ee.Dictionary({
  imagenes_1985_2021: antiguos.size(),
  imagenes_2022_2024: recientes.size(),
  imagenes_total: todos.size(),
  years_disponibles: todos.aggregate_array('year').distinct().sort(),
  regiones_disponibles: todos.aggregate_array('region_code')
    .distinct().sort(),
  regiones_esperadas: REGIONES
}));

print('B. SERIE AGREGADA DEL ACR — copiar estas listas', ee.Dictionary({
  year: years,
  n_teselas: serieTeselas,
  nimages_total: serieNimagesTotal,
  nimages_min_tesela: serieNimagesMin,
  nimages_max_tesela: serieNimagesMax,
  cloud_cover_medio: serieCloudMedio,
  cloud_cover_max: serieCloudMax
}));

print('C. SATELITES Y VERSIONES POR YEAR', ee.Dictionary({
  year: years,
  satelites: serieSatelites,
  versiones: serieVersiones
}));

print('D. NIMAGES POR REGION', ee.Dictionary({
  year: years,
  region_703: serieNimagesRegion(703),
  region_704: serieNimagesRegion(704),
  region_705: serieNimagesRegion(705)
}));

print('E. CLOUD COVER MEDIO POR REGION', ee.Dictionary({
  year: years,
  region_703: serieCloudRegion(703),
  region_704: serieCloudRegion(704),
  region_705: serieCloudRegion(705)
}));

print('F. AMBITOS Y SUS REGIONES DE MOSAICO', ambitosRegiones);

print('G. LECTURA', ee.Dictionary({
  proposito: 'Cruzar nimages_total y cloud_cover_medio contra el delta ' +
    'anual de clase 70 de serie_indicadores_acr_1985_2024.csv.',
  hipotesis: 'Los years con menos observaciones utiles producen ' +
    'subdeteccion de la clase beta 70 y saltos artificiales al year ' +
    'siguiente.',
  control_6E4: '1985 tuvo 9 escenas y 56.7 % de nubes; 1986 tuvo 27. ' +
    'El salto fue de +31.9 % en el total del ACR.',
  limite: 'Una correlacion no demuestra causalidad por si sola. Los ' +
    'saltos que coincidan con years de insumo pobre deben confirmarse ' +
    'con el mismo protocolo de cuatro criterios del paso 6E4.'
}));

// ---------------------------------------------------------------------
// 7. Exportacion opcional
// ---------------------------------------------------------------------

if (EXPORTAR_CSV) {
  var tabla = ee.FeatureCollection(years.map(function(year) {
    year = ee.Number(year);
    var subset = subsetAnual(year);
    return ee.Feature(null, {
      year: year,
      n_teselas: subset.size(),
      nimages_total: reducirSeguro(subset, 'nimages', ee.Reducer.sum()),
      nimages_min_tesela: reducirSeguro(subset, 'nimages', ee.Reducer.min()),
      nimages_max_tesela: reducirSeguro(subset, 'nimages', ee.Reducer.max()),
      cloud_cover_medio: reducirSeguro(
        subset, 'cloud_cover', ee.Reducer.mean()),
      cloud_cover_max: reducirSeguro(
        subset, 'cloud_cover', ee.Reducer.max()),
      nimages_region_703: reducirSeguro(
        subsetAnualRegion(year, 703), 'nimages', ee.Reducer.sum()),
      nimages_region_704: reducirSeguro(
        subsetAnualRegion(year, 704), 'nimages', ee.Reducer.sum()),
      nimages_region_705: reducirSeguro(
        subsetAnualRegion(year, 705), 'nimages', ee.Reducer.sum()),
      satelites: subset.aggregate_array('satellite').distinct().sort()
        .join('|'),
      versiones: subset.aggregate_array('version').distinct().sort()
        .join('|')
    });
  }));

  Export.table.toDrive({
    collection: tabla,
    description: 'paso06E5_insumo_landsat_acr_1985_2024',
    fileNamePrefix: 'paso06E5_insumo_landsat_acr_1985_2024',
    fileFormat: 'CSV',
    selectors: [
      'year', 'n_teselas', 'nimages_total', 'nimages_min_tesela',
      'nimages_max_tesela', 'cloud_cover_medio', 'cloud_cover_max',
      'nimages_region_703', 'nimages_region_704', 'nimages_region_705',
      'satelites', 'versiones'
    ]
  });

  print('EXPORTACION ACTIVADA. Revisar la pestaña Tasks.');
} else {
  print('No se ejecutaron exportaciones. ' +
    'Cambiar EXPORTAR_CSV a true si se prefiere el CSV.');
}

Map.centerObject(acr, 9);
Map.addLayer(
  acr.style({color: '00FFFF', fillColor: '00000000', width: 2}),
  {},
  'Cinco ambitos del ACR'
);
