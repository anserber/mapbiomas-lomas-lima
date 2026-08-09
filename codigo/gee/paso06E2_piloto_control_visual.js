// PASO 6E2 — Piloto de control visual de transiciones prioritarias.
// Cambia únicamente el valor de CASO_ID para revisar otro caso.
// No exporta archivos ni convierte automáticamente una transición en pérdida.

var ASSET_ACR =
  'projects/mapbiomas-lomas-jhoreck/assets/inputs/acr_lomas_5_ambitos_gee';
var ASSET_ANILLOS_SISTEMA =
  'projects/mapbiomas-lomas-jhoreck/assets/inputs/' +
  'anillos_sistema_periferia_externa_gee';
var ASSET_CLASES =
  'projects/mapbiomas-public/assets/peru/collection3/' +
  'mapbiomas_peru_collection3_integration_v1';
var MOSAICOS_1985_2021 =
  'projects/nexgenmap/MapBiomas2/LANDSAT/PANAMAZON/mosaics-2';
var MOSAICOS_2022_2024 =
  'projects/mapbiomas-raisg/MOSAICOS/mosaics-2';

// Casos piloto:
// 1. villa_maria_2021_2022 — señal reciente loma→urbano dentro del ACR.
// 2. amancaes_2023_2024 — señal reciente loma→urbano dentro del ACR.
// 3. sistema_0_500_2022_2023 — presión inmediata alrededor del sistema.
// 4. ancon_2000_2001 — intercambio dominante 68↔70 para auditar ruido.
var CASO_ID = 'villa_maria_2021_2022';

var casos = {
  villa_maria_2021_2022: {
    nivel: 'acr',
    id_ambito: 'villa_maria',
    zona: 'interior_acr',
    nombre: 'Lomas de Villa María',
    year_start: 2021,
    year_end: 2022,
    esperado_loma_urbano_ha: 13.78764651465322,
    objetivo: 'Señal reciente 70→24 dentro del ACR'
  },
  amancaes_2023_2024: {
    nivel: 'acr',
    id_ambito: 'amancaes',
    zona: 'interior_acr',
    nombre: 'Lomas de Amancaes',
    year_start: 2023,
    year_end: 2024,
    esperado_loma_urbano_ha: 4.69080809307024,
    objetivo: 'Señal reciente 70→24 dentro del ACR'
  },
  sistema_0_500_2022_2023: {
    nivel: 'sistema',
    id_ambito: 'sistema',
    zona: '0_500',
    nombre: 'Sistema disuelto — periferia externa 0–500 m',
    year_start: 2022,
    year_end: 2023,
    esperado_loma_urbano_ha: 14.439724473398252,
    objetivo: 'Señal reciente 70→24 alrededor del sistema'
  },
  ancon_2000_2001: {
    nivel: 'acr',
    id_ambito: 'ancon',
    zona: 'interior_acr',
    nombre: 'Lomas de Ancón',
    year_start: 2000,
    year_end: 2001,
    esperado_loma_urbano_ha: 0,
    objetivo: 'Intercambio 68↔70; posible alternancia de clasificación'
  }
};

var caso = casos[CASO_ID];
if (!caso) {
  throw new Error('CASO_ID no reconocido: ' + CASO_ID);
}

var acr = ee.FeatureCollection(ASSET_ACR);
var anillosSistema = ee.FeatureCollection(ASSET_ANILLOS_SISTEMA);
var clases = ee.Image(ASSET_CLASES);

var unidad = caso.nivel === 'acr'
  ? acr.filter(ee.Filter.eq('id_ambito', caso.id_ambito))
  : anillosSistema.filter(ee.Filter.eq('zona', caso.zona));

var geometria = unidad.geometry();
var contexto = geometria.buffer(1500);

function coleccionMosaicos(year) {
  var asset = year <= 2021 ? MOSAICOS_1985_2021 : MOSAICOS_2022_2024;
  return ee.ImageCollection(asset)
    .filter(ee.Filter.eq('year', year))
    .filterBounds(contexto);
}

function mosaicoAnual(year) {
  return coleccionMosaicos(year)
    .select([
      'swir1_median',
      'nir_median',
      'red_median',
      'green_median',
      'blue_median'
    ])
    .mosaic()
    .clip(contexto);
}

function areaHa(mask) {
  var resultado = ee.Image.pixelArea()
    .divide(10000)
    .updateMask(mask)
    .reduceRegion({
      reducer: ee.Reducer.sum(),
      geometry: geometria,
      scale: 30,
      maxPixels: 1e9,
      tileScale: 4
    });
  return ee.Number(ee.Algorithms.If(
    resultado.contains('area'),
    resultado.get('area'),
    0
  ));
}

var inicio = clases.select('classification_' + caso.year_start);
var fin = clases.select('classification_' + caso.year_end);

var lomaInicio = inicio.eq(70);
var lomaFin = fin.eq(70);
var urbanoInicio = inicio.eq(24);
var urbanoFin = fin.eq(24);

var lomaAUrbano = lomaInicio.and(urbanoFin).clip(geometria);
var salidaLoma = lomaInicio.and(lomaFin.not()).clip(geometria);
var intercambio70a68 = lomaInicio.and(fin.eq(68)).clip(geometria);
var intercambio68a70 = inicio.eq(68).and(lomaFin).clip(geometria);

var mosaicoInicio = mosaicoAnual(caso.year_start);
var mosaicoFin = mosaicoAnual(caso.year_end);

var visNatural = {
  bands: ['red_median', 'green_median', 'blue_median'],
  min: 200,
  max: 2200,
  gamma: 1.15
};
var visFalsoColor = {
  bands: ['swir1_median', 'nir_median', 'red_median'],
  min: 200,
  max: 3200,
  gamma: 1.15
};

print('PASO 6E2 — PILOTO DE CONTROL VISUAL');
print('CASO_ID', CASO_ID);
print('Caso', caso);
print('Objetos de la unidad — esperado: 1', unidad.size());
print('Mosaicos del año inicial', coleccionMosaicos(caso.year_start).size());
print('Mosaicos del año final', coleccionMosaicos(caso.year_end).size());
print('Área 70→24 esperada desde la tabla — ha',
  caso.esperado_loma_urbano_ha);
print('Área 70→24 recalculada para control — ha',
  areaHa(lomaAUrbano));
print('Área de salida de clase 70 — ha',
  areaHa(salidaLoma));
print('Área 70→68 — ha',
  areaHa(intercambio70a68));
print('Área 68→70 — ha',
  areaHa(intercambio68a70));

Map.centerObject(unidad, caso.nivel === 'acr' ? 13 : 11);

Map.addLayer(mosaicoInicio, visNatural,
  caso.year_start + ' — color natural', false);
Map.addLayer(mosaicoFin, visNatural,
  caso.year_end + ' — color natural', true);
Map.addLayer(mosaicoInicio, visFalsoColor,
  caso.year_start + ' — falso color SWIR/NIR/R', false);
Map.addLayer(mosaicoFin, visFalsoColor,
  caso.year_end + ' — falso color SWIR/NIR/R', false);

Map.addLayer(lomaInicio.selfMask().clip(geometria),
  {palette: ['00A651']}, 'Clase 70 — ' + caso.year_start, false);
Map.addLayer(lomaFin.selfMask().clip(geometria),
  {palette: ['7CFC00']}, 'Clase 70 — ' + caso.year_end, false);
Map.addLayer(salidaLoma.selfMask(),
  {palette: ['FFD700']}, 'Salida de clase 70 — amarillo', false);
Map.addLayer(intercambio70a68.selfMask(),
  {palette: ['FF8C00']}, '70→68 — naranja', false);
Map.addLayer(intercambio68a70.selfMask(),
  {palette: ['00FFFF']}, '68→70 — cian', false);
Map.addLayer(lomaAUrbano.selfMask(),
  {palette: ['FF00FF']}, '70→24 — magenta', true);

Map.addLayer(
  unidad.style({color: 'FFFFFF', fillColor: '00000000', width: 2}),
  {},
  'Límite de la unidad',
  true
);

var panel = ui.Panel({
  style: {
    position: 'top-left',
    width: '390px',
    padding: '8px'
  }
});
panel.add(ui.Label('Paso 6E2 — control visual', {
  fontWeight: 'bold',
  fontSize: '16px'
}));
panel.add(ui.Label(caso.nombre));
panel.add(ui.Label(caso.year_start + ' → ' + caso.year_end));
panel.add(ui.Label(caso.objetivo));
panel.add(ui.Label(
  'Magenta = transición cartográfica 70→24. ' +
  'Debe contrastarse alternando los mosaicos inicial y final.'
));
panel.add(ui.Label(
  'No denominar pérdida ecológica hasta revisar forma, contexto y persistencia.'
));
Map.add(panel);

print('No se ejecutaron exportaciones.');
print('Revisa la Console y alterna las capas desde Layers.');
