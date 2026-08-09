// =====================================================================
// PASO 12C — Exportación de las capas espaciales de los mapas M01 y M02.
// ---------------------------------------------------------------------
// Único paso del Paso 12 que necesita Google Earth Engine: la frecuencia
// por píxel y las huellas de transición no se pueden reconstruir desde un
// CSV. Todo lo demás del paso 12 sale de tablas ya exportadas.
//
// Produce dos GeoTIFF:
//
//   1. persistencia_clase70_frecuencia_1985_2024.tif
//      Número de años en que el píxel es clase 70, de 0 a 40. Alimenta M01.
//      El contorno de `siempre 70` se deriva en Python como frecuencia = 40,
//      de modo que no hace falta una segunda exportación.
//
//   2. huella_urbana_70_24.tif
//      Categórica: 0 sin señal, 1 salida estable W5 hacia clase 24
//      (1990-2020), 2 salida hacia clase 24 registrada en 2021-2024 y
//      censurada por el final de la serie. Alimenta M02.
//
// La lógica W5, la de censura y la exclusión de rupturas conocidas son las
// mismas del paso 07D1, copiadas literalmente para que los mapas reproduzcan
// las cifras de la tabla maestra. Si divergieran, el mapa y la tabla dirían
// cosas distintas sobre el mismo territorio.
//
// La región de exportación es la unión del ACR y de los tres anillos
// disueltos. NO se exporta ninguna geometría ni resultado de la KBA
// restringida.
//
// Antes de exportar, el script imprime áreas de control. Revisa el bloque A
// y solo entonces lanza las tareas.
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
var ASSET_TRANSICIONES =
  'projects/mapbiomas-public/assets/peru/collection3/' +
  'mapbiomas_peru_collection3_transitions_v1';

var YEAR_START = 1985;
var YEAR_END = 2024;
var N_YEARS = 40;

var W5_PRIMER_EVENTO = 1990;   // primer año con ventana W5 completa
var W5_ULTIMO_EVENTO = 2020;   // último año con ventana W5 completa
var CENSURA_PRIMER = 2021;     // desde aquí la ventana no puede completarse
var CENSURA_ULTIMO = 2024;

var CRS_SALIDA = 'EPSG:32718';
var ESCALA = 30;

var acr = ee.FeatureCollection(ASSET_ACR);
var sistema = ee.FeatureCollection(ASSET_SISTEMA);
var clases = ee.Image(ASSET_CLASES);
var transiciones = ee.Image(ASSET_TRANSICIONES);
var pixelHa = ee.Image.pixelArea().divide(10000);

// Región de exportación: ACR + anillos, con un margen de 300 m para que el
// mapa no quede recortado justo en el borde de la geometría.
var region = acr.geometry().union(sistema.geometry(), 1).bounds().buffer(300);

// ---------------------------------------------------------------------
// 2. Funciones del paso 07D1, sin modificar
// ---------------------------------------------------------------------

function clase(year) {
  return clases.select('classification_' + year);
}

function loma(year) {
  return clase(year).eq(70).rename('estado');
}

function codigoTransicion(year) {
  return transiciones.select('transitions_' + (year - 1) + '_' + year);
}

function todosEstado(yearStart, yearEnd, estado) {
  var resultado = ee.Image(1).rename('estado');
  for (var year = yearStart; year <= yearEnd; year++) {
    resultado = resultado.and(loma(year).eq(estado));
  }
  return resultado.rename('estado');
}

function perdidaEstable(year, ventana) {
  return todosEstado(year - ventana, year - 1, 1)
    .and(todosEstado(year, year + ventana - 1, 0))
    .rename('evento');
}

// Rupturas cartográficas conocidas, excluidas de todo evento interpretado.
var ancon = acr.filter(ee.Filter.eq('id_ambito', 'ancon'));
var carabayllo2 = acr.filter(ee.Filter.eq('id_ambito', 'carabayllo_2'));

var rupturaAncon = codigoTransicion(2001).eq(7068)
  .clip(ancon.geometry()).unmask(0).rename('ruptura');
var codigo2015 = codigoTransicion(2015);
var rupturaCarabayllo2 = codigo2015.eq(7013).or(codigo2015.eq(7068))
  .clip(carabayllo2.geometry()).unmask(0).rename('ruptura');
var rupturasConocidas = ee.ImageCollection.fromImages([
  rupturaAncon, rupturaCarabayllo2
]).max().unmask(0, false).rename('ruptura');
var fueraRuptura = rupturasConocidas.eq(0);

// ---------------------------------------------------------------------
// 3. Capa 1 — frecuencia de la clase 70
// ---------------------------------------------------------------------

var estados = [];
for (var y = YEAR_START; y <= YEAR_END; y++) {
  estados.push(loma(y));
}
var frecuencia70 = ee.ImageCollection.fromImages(estados).sum()
  .rename('frecuencia_70').toUint8();
var siempre70 = frecuencia70.eq(N_YEARS);

// ---------------------------------------------------------------------
// 4. Capa 2 — huella urbana confirmada y censurada
// ---------------------------------------------------------------------

var w5Urbano = ee.Image(0);
for (var eventYear = W5_PRIMER_EVENTO; eventYear <= W5_ULTIMO_EVENTO; eventYear++) {
  var lossW5 = perdidaEstable(eventYear, 5).and(fueraRuptura);
  var destino = codigoTransicion(eventYear).mod(100);
  w5Urbano = w5Urbano.or(lossW5.and(destino.eq(24)));
}

var censuraUrbano = ee.Image(0);
for (var recentYear = CENSURA_PRIMER; recentYear <= CENSURA_ULTIMO; recentYear++) {
  var codigo = codigoTransicion(recentYear);
  var origen = codigo.divide(100).floor();
  var destinoReciente = codigo.mod(100);
  var salidaReciente = origen.eq(70)
    .and(destinoReciente.neq(70))
    .and(fueraRuptura);
  censuraUrbano = censuraUrbano.or(
    salidaReciente.and(destinoReciente.eq(24)));
}

// Categórica de una sola banda. La confirmada prevalece sobre la censurada
// donde ambas coinciden: un píxel con evento W5 ya no es un candidato.
var huellaUrbana = ee.Image(0)
  .where(censuraUrbano, 2)
  .where(w5Urbano, 1)
  .rename('huella_70_24').toUint8();

// ---------------------------------------------------------------------
// 5. Controles antes de exportar
// ---------------------------------------------------------------------

function areaHa(mascara, geometria) {
  return pixelHa.multiply(mascara).reduceRegion({
    reducer: ee.Reducer.sum(),
    geometry: geometria,
    scale: ESCALA,
    maxPixels: 1e9,
    tileScale: 4
  }).values().get(0);
}

var geomAcr = acr.geometry();
var geomSistema = sistema.geometry();

print('===== PASO 12C — CONTROLES PREVIOS A LA EXPORTACIÓN =====');

print('A. CONTROL CONTRA LA TABLA MAESTRA', ee.Dictionary({
  siempre70_acr_ha: areaHa(siempre70, geomAcr),
  siempre70_acr_esperada_ha: 3542.972,
  w5_urbano_acr_ha: areaHa(w5Urbano, geomAcr),
  w5_urbano_acr_esperada_ha: 0.905,
  censura_urbano_acr_ha: areaHa(censuraUrbano, geomAcr),
  censura_urbano_acr_esperada_ha: 23.081,
  w5_urbano_anillos_ha: areaHa(w5Urbano, geomSistema),
  w5_urbano_anillos_esperada_ha: 21.833,
  censura_urbano_anillos_ha: areaHa(censuraUrbano, geomSistema),
  censura_urbano_anillos_esperada_ha: 44.882
}));

print('B. LECTURA', ee.Dictionary({
  nota_1: 'Las superficies de huella pueden ser algo menores que las de la ' +
    'tabla maestra: la tabla suma ha-evento, y un mismo pixel con dos ' +
    'eventos en años distintos cuenta dos veces. El mapa dibuja superficie ' +
    'unica. Diferencias pequeñas son esperables; una diferencia grande no.',
  nota_2: 'siempre70_acr_ha debe coincidir de forma exacta: es superficie ' +
    'unica en los dos casos.',
  si_cuadra: 'Ejecutar las dos tareas de la pestaña Tasks.',
  si_no_cuadra: 'No exportar y revisar antes de componer los mapas.'
}));

print('C. EXPORTACIONES PREVISTAS', ee.Dictionary({
  crs: CRS_SALIDA,
  escala_m: ESCALA,
  region: 'ACR + anillos disueltos, con margen de 300 m',
  archivo_1: 'persistencia_clase70_frecuencia_1985_2024 (0-40, uint8)',
  archivo_2: 'huella_urbana_70_24 (0 sin señal, 1 W5, 2 censurada, uint8)',
  kba: 'NO se exporta ninguna geometría ni resultado de la KBA restringida'
}));

// ---------------------------------------------------------------------
// 6. Exportaciones
// ---------------------------------------------------------------------

Export.image.toDrive({
  image: frecuencia70.clip(region),
  description: 'paso12C_persistencia_clase70_frecuencia_1985_2024',
  fileNamePrefix: 'persistencia_clase70_frecuencia_1985_2024',
  folder: 'mapbiomas_lomas_paso12',
  region: region,
  scale: ESCALA,
  crs: CRS_SALIDA,
  maxPixels: 1e9,
  fileFormat: 'GeoTIFF',
  formatOptions: {cloudOptimized: true}
});

Export.image.toDrive({
  image: huellaUrbana.clip(region),
  description: 'paso12C_huella_urbana_70_24',
  fileNamePrefix: 'huella_urbana_70_24',
  folder: 'mapbiomas_lomas_paso12',
  region: region,
  scale: ESCALA,
  crs: CRS_SALIDA,
  maxPixels: 1e9,
  fileFormat: 'GeoTIFF',
  formatOptions: {cloudOptimized: true}
});

// ---------------------------------------------------------------------
// 7. Vista previa
// ---------------------------------------------------------------------

Map.centerObject(acr, 10);
Map.addLayer(
  frecuencia70.updateMask(frecuencia70.gt(0)).clip(region),
  {min: 1, max: 40, palette: ['FFFFCC', 'C2E699', '78C679', '31A354', '006837']},
  'Frecuencia de clase 70 (1-40)'
);
Map.addLayer(
  huellaUrbana.updateMask(huellaUrbana.eq(2)).clip(region),
  {palette: ['E69F00']}, 'Huella censurada 2021-2024'
);
Map.addLayer(
  huellaUrbana.updateMask(huellaUrbana.eq(1)).clip(region),
  {palette: ['0072B2']}, 'Huella W5 confirmada 1990-2020'
);
Map.addLayer(
  sistema.style({color: 'FFA500', fillColor: '00000000', width: 1}),
  {}, 'Anillos disueltos'
);
Map.addLayer(
  acr.style({color: '000000', fillColor: '00000000', width: 2}),
  {}, 'Cinco ámbitos del ACR'
);

print('Revisa el bloque A antes de lanzar las tareas de la pestaña Tasks.');
