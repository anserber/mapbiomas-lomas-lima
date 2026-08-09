// =====================================================================
// PASO 12D — Capas de contexto para el mapa M00 (localización y diseño
// analítico), que se compone en QGIS.
// ---------------------------------------------------------------------
// M00 dibuja los cinco ámbitos del ACR y los tres anillos de periferia
// externa. Entre unos y otros queda más de la mitad de la hoja en blanco,
// porque el sistema son cuatro racimos dispersos a lo largo de 64 km.
// Ese blanco es Lima. Rellenarlo con la cobertura de MapBiomas convierte
// el espacio muerto en el argumento del mapa: las lomas son islas dentro
// de una metrópoli, y por eso los anillos de distancia miden presión.
//
// Produce hasta tres GeoTIFF:
//
//   1. contexto_mapbiomas_2024_agrupado.tif      [siempre]
//      Categórica de una banda, uint8:
//        0 otras coberturas    1 infraestructura urbana (clase 24)
//        2 mosaico agropecuario (clase 21)       3 agua (clase 33)
//      Para el fondo de M00, en grises. El valor 1 aislado da la capa
//      urbana limpia si prefieres estilizar solo esa.
//
//   2. dem_nasadem_30m.tif                       [siempre]
//      Elevación NASADEM en metros, para el relieve sombreado en QGIS o
//      en Blender. Región ampliada 2 km para que el sombreado no se
//      corte en el borde del mapa.
//
//   3. contexto_urbano_1986_2024.tif             [opcional, apagado]
//      Categórica: 1 urbano ya en 1986, 2 urbano nuevo entre 1986 y 2024.
//      Enciéndela solo si decides que M00 muestre el crecimiento urbano.
//      Ojo: eso lo acerca al terreno de M02 y deja de ser contexto.
//
// NO se exporta ninguna geometría ni resultado de la KBA restringida.
//
// Revisa el bloque de control antes de lanzar las tareas.
// =====================================================================

// ---------------------------------------------------------------------
// 1. Constantes
// ---------------------------------------------------------------------

var ASSET_ACR =
  'projects/mapbiomas-lomas-jhoreck/assets/inputs/acr_lomas_5_ambitos_gee';
var ASSET_SISTEMA =
  'projects/mapbiomas-lomas-jhoreck/assets/inputs/' +
  'anillos_sistema_periferia_externa_gee';
var ASSET_CLASES =
  'projects/mapbiomas-public/assets/peru/collection3/' +
  'mapbiomas_peru_collection3_integration_v1';

var CRS_SALIDA = 'EPSG:32718';
var ESCALA = 30;
var CARPETA_DRIVE = 'mapbiomas_lomas_paso12';

// Clases de MapBiomas Perú Colección 3 usadas como contexto.
var CLASE_URBANO = 24;    // Infraestructura urbana
var CLASE_AGRO = 21;      // Mosaico agropecuario
var CLASE_AGUA = 33;      // Río, lago y océano

var ANIO_BASE = 1986;     // línea base del estudio (adenda v1.1)
var ANIO_FIN = 2024;

var EXPORTAR_CRECIMIENTO_URBANO = false;   // ver nota 3 de la cabecera

// Extensión exacta del marco de M00: envolvente de los tres anillos con
// un margen del 3 %, la misma que calculó `mapa_00_wireframe.py`. Se fija
// como constante para que el raster y el marco de QGIS coincidan al metro
// y no haya que recortar nada después.
var REGION = ee.Geometry.Rectangle(
  [259167, 8651878, 295330, 8716248], CRS_SALIDA, false);

// El relieve necesita 2 km de más por lado: un sombreado calculado justo
// hasta el borde produce un artefacto de iluminación en el margen.
var REGION_DEM = ee.Geometry.Rectangle(
  [257167, 8649878, 297330, 8718248], CRS_SALIDA, false);

var acr = ee.FeatureCollection(ASSET_ACR);
var sistema = ee.FeatureCollection(ASSET_SISTEMA);
var clases = ee.Image(ASSET_CLASES);
var pixelHa = ee.Image.pixelArea().divide(10000);

function clase(year) {
  return clases.select('classification_' + year);
}

// ---------------------------------------------------------------------
// 2. Capa 1 — contexto de cobertura agrupado, 2024
// ---------------------------------------------------------------------

var c2024 = clase(ANIO_FIN);

var contexto = ee.Image(0)
  .where(c2024.eq(CLASE_AGUA), 3)
  .where(c2024.eq(CLASE_AGRO), 2)
  .where(c2024.eq(CLASE_URBANO), 1)
  .rename('contexto_2024')
  .toUint8()
  .clip(REGION);

// ---------------------------------------------------------------------
// 3. Capa 2 — elevación para el relieve
// ---------------------------------------------------------------------

var dem = ee.Image('NASA/NASADEM_HGT/001').select('elevation')
  .rename('elevacion_m')
  .toInt16()
  .clip(REGION_DEM);

// Vista previa del sombreado, solo para juzgar en pantalla si el relieve
// aporta. El sombreado final se calcula en QGIS o en Blender sobre el DEM
// exportado, no aquí.
var sombreado = ee.Terrain.hillshade(
  dem.reproject({crs: CRS_SALIDA, scale: ESCALA}), 315, 45);

// ---------------------------------------------------------------------
// 4. Capa 3 — crecimiento urbano, opcional
// ---------------------------------------------------------------------

var urbano1986 = clase(ANIO_BASE).eq(CLASE_URBANO);
var urbano2024 = c2024.eq(CLASE_URBANO);

var crecimiento = ee.Image(0)
  .where(urbano2024.and(urbano1986.not()), 2)
  .where(urbano1986, 1)
  .rename('urbano_1986_2024')
  .toUint8()
  .clip(REGION);

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

print('===== PASO 12D — CONTROLES PREVIOS =====');

print('A. EXTENSIÓN', ee.Dictionary({
  crs: CRS_SALIDA,
  region_mapa_m: '259167, 8651878, 295330, 8716248',
  ancho_km: 36.16,
  alto_km: 64.37,
  relacion_alto_ancho: 1.780,
  escala_del_marco_de_117_mm: '1:309 000',
  nota: 'Coincide con el marco definido en mapa_00_wireframe.py. Si cambias ' +
    'la extension del marco en QGIS, cambia tambien esta constante o el ' +
    'raster dejara de encajar.'
}));

print('B. SUPERFICIES DE CONTEXTO DENTRO DEL MARCO', ee.Dictionary({
  urbano_2024_ha: areaHa(contexto.eq(1), REGION),
  agropecuario_2024_ha: areaHa(contexto.eq(2), REGION),
  agua_2024_ha: areaHa(contexto.eq(3), REGION),
  urbano_1986_ha: areaHa(urbano1986, REGION),
  lectura: 'Estas cifras son de CONTEXTO y no entran en la tabla maestra ni ' +
    'en el texto de resultados. Se calculan sobre el rectangulo del marco, ' +
    'cuya extension es una decision de composicion, no una unidad de analisis.'
}));

print('C. EXPORTACIONES PREVISTAS', ee.Dictionary({
  archivo_1: 'contexto_mapbiomas_2024_agrupado (0 otras, 1 urbano, ' +
    '2 agropecuario, 3 agua; uint8)',
  archivo_2: 'dem_nasadem_30m (elevacion en metros; int16; region +2 km)',
  archivo_3: EXPORTAR_CRECIMIENTO_URBANO ?
    'contexto_urbano_1986_2024 (1 urbano en 1986, 2 nuevo 1986-2024)' :
    'contexto_urbano_1986_2024 — DESACTIVADO',
  carpeta_drive: CARPETA_DRIVE,
  kba: 'NO se exporta ninguna geometria ni resultado de la KBA restringida'
}));

// ---------------------------------------------------------------------
// 6. Exportaciones
// ---------------------------------------------------------------------

Export.image.toDrive({
  image: contexto,
  description: 'paso12D_contexto_mapbiomas_2024_agrupado',
  fileNamePrefix: 'contexto_mapbiomas_2024_agrupado',
  folder: CARPETA_DRIVE,
  region: REGION,
  scale: ESCALA,
  crs: CRS_SALIDA,
  maxPixels: 1e9,
  fileFormat: 'GeoTIFF',
  formatOptions: {cloudOptimized: true}
});

Export.image.toDrive({
  image: dem,
  description: 'paso12D_dem_nasadem_30m',
  fileNamePrefix: 'dem_nasadem_30m',
  folder: CARPETA_DRIVE,
  region: REGION_DEM,
  scale: ESCALA,
  crs: CRS_SALIDA,
  maxPixels: 1e9,
  fileFormat: 'GeoTIFF',
  formatOptions: {cloudOptimized: true}
});

if (EXPORTAR_CRECIMIENTO_URBANO) {
  Export.image.toDrive({
    image: crecimiento,
    description: 'paso12D_contexto_urbano_1986_2024',
    fileNamePrefix: 'contexto_urbano_1986_2024',
    folder: CARPETA_DRIVE,
    region: REGION,
    scale: ESCALA,
    crs: CRS_SALIDA,
    maxPixels: 1e9,
    fileFormat: 'GeoTIFF',
    formatOptions: {cloudOptimized: true}
  });
}

// ---------------------------------------------------------------------
// 7. Vista previa
// ---------------------------------------------------------------------

Map.centerObject(sistema, 10);

Map.addLayer(sombreado, {min: 0, max: 255}, 'Relieve sombreado (vista previa)',
  false);
Map.addLayer(contexto.updateMask(contexto.eq(3)), {palette: ['C6DBEF']}, 'Agua');
Map.addLayer(contexto.updateMask(contexto.eq(2)), {palette: ['E8E0C8']},
  'Agropecuario');
Map.addLayer(contexto.updateMask(contexto.eq(1)), {palette: ['9E9E9E']},
  'Urbano 2024');
Map.addLayer(
  sistema.style({color: '807DBA', fillColor: '00000000', width: 1}),
  {}, 'Anillos de periferia externa');
Map.addLayer(
  acr.style({color: '1B7837', fillColor: '00000000', width: 2}),
  {}, 'Cinco ámbitos del ACR');
Map.addLayer(
  ee.FeatureCollection([ee.Feature(REGION)])
    .style({color: 'CC0000', fillColor: '00000000', width: 1}),
  {}, 'Marco de M00');

print('Revisa los bloques A y B, y solo entonces lanza las tareas de Tasks.');
