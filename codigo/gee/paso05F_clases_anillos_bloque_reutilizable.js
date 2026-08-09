// PASO 5F-R — Composición por clases de anillos de periferia externa.
// Revisión del 28-07-2026. No incluye el enclave interno de Carabayllo 2.
// Una fila por unidad espacial, año y clase MapBiomas.
// Crea una tarea de exportación que no se inicia automáticamente.
// Modificar únicamente START_YEAR y END_YEAR para cada ejecución.

var START_YEAR = 1985;
var END_YEAR = 1989;
var BLOCK_LABEL = START_YEAR + '_' + END_YEAR;
var EXPORT_NAME =
    'serie_clases_anillos_periferia_externa_' + BLOCK_LABEL;

var ASSET_AMBITOS =
    'projects/mapbiomas-lomas-jhoreck/assets/inputs/' +
    'anillos_por_ambito_periferia_externa_gee';
var ASSET_SISTEMA =
    'projects/mapbiomas-lomas-jhoreck/assets/inputs/' +
    'anillos_sistema_periferia_externa_gee';

var MAPBIOMAS_ASSET =
    'projects/mapbiomas-public/assets/peru/collection3/' +
    'mapbiomas_peru_collection3_integration_v1';

var anillosAmbitosRaw = ee.FeatureCollection(ASSET_AMBITOS);
var anillosSistemaRaw = ee.FeatureCollection(ASSET_SISTEMA);
var mapbiomas = ee.Image(MAPBIOMAS_ASSET);
var years = ee.List.sequence(START_YEAR, END_YEAR);
var scale = 30;
var nativeProjection =
    mapbiomas.select('classification_2024').projection();
var utm18s = ee.Projection('EPSG:32718');
var pixelAreaHa = ee.Image.pixelArea().divide(10000);

var anillosAmbitos = anillosAmbitosRaw.map(function(feature) {
  var id = ee.String(feature.get('id_ambito'));
  var zona = ee.String(feature.get('zona'));
  return feature.set({
    nivel: 'ambito',
    unidad_id: id.cat('|').cat(zona),
    area_ref_ha: feature.get('area_ha')
  });
});

var anillosSistema = anillosSistemaRaw.map(function(feature) {
  var zona = ee.String(feature.get('zona'));
  return feature.set({
    nivel: 'sistema',
    unidad_id: ee.String('sistema|').cat(zona),
    id_ambito: 'sistema',
    nombre: 'Sistema disuelto',
    area_ref_ha: feature.get('area_ha')
  });
});

var unidades = anillosAmbitos.merge(anillosSistema);

var classNames = ee.Dictionary({
  '0': 'Sin dato',
  '3': 'Bosque',
  '4': 'Bosque seco',
  '5': 'Manglar',
  '6': 'Bosque inundable',
  '9': 'Plantación forestal',
  '11': 'Zona pantanosa o pastizal inundable',
  '12': 'Pastizal / herbazal',
  '13': 'Otra formación no boscosa',
  '15': 'Pasto',
  '18': 'Agricultura',
  '21': 'Mosaico agropecuario',
  '23': 'Playa',
  '24': 'Infraestructura urbana',
  '25': 'Otra área antrópica sin vegetación',
  '27': 'No observado',
  '29': 'Afloramiento rocoso',
  '30': 'Minería',
  '31': 'Acuicultura',
  '32': 'Salina costera',
  '33': 'Río, lago u océano',
  '34': 'Glaciar',
  '35': 'Palma aceitera',
  '40': 'Arroz',
  '61': 'Salar',
  '66': 'Matorral',
  '68': 'Otra área natural sin vegetación',
  '70': 'Loma costera',
  '72': 'Otros cultivos'
});

var classOrigins = ee.Dictionary({
  '0': 'No definido',
  '3': 'Natural',
  '4': 'Natural',
  '5': 'Natural',
  '6': 'Natural',
  '9': 'Antrópico',
  '11': 'Natural',
  '12': 'Natural',
  '13': 'Natural',
  '15': 'Antrópico',
  '18': 'Antrópico',
  '21': 'Antrópico',
  '23': 'Natural',
  '24': 'Antrópico',
  '25': 'Antrópico',
  '27': 'No definido',
  '29': 'Natural',
  '30': 'Antrópico',
  '31': 'Antrópico',
  '32': 'Natural',
  '33': 'Natural',
  '34': 'Natural',
  '35': 'Antrópico',
  '40': 'Antrópico',
  '61': 'Natural',
  '66': 'Natural',
  '68': 'Natural',
  '70': 'Natural',
  '72': 'Antrópico'
});

function classificationForYear(year) {
  year = ee.Number(year);
  var bandName =
      ee.String('classification_').cat(year.format('%d'));
  return mapbiomas.select([bandName]).rename('class_id').unmask(0);
}

function extractClassesForYear(year) {
  year = ee.Number(year);
  var classification = classificationForYear(year);
  var image = pixelAreaHa
      .rename('area_ha')
      .addBands(classification);

  var grouped = image.reduceRegions({
    collection: unidades,
    reducer: ee.Reducer.sum().group({
      groupField: 1,
      groupName: 'class_id'
    }),
    scale: scale,
    crs: nativeProjection,
    tileScale: 4
  });

  var nestedRows = grouped.toList(grouped.size()).map(function(item) {
    var feature = ee.Feature(item);
    var areaRef = ee.Number(feature.get('area_ref_ha'));
    var areaUtm = feature.geometry().area({
      maxError: 1,
      proj: utm18s
    }).divide(10000);
    var groups = ee.List(feature.get('groups'));

    return groups.map(function(groupItem) {
      var group = ee.Dictionary(groupItem);
      var classId = ee.Number(group.get('class_id'));
      var classKey = classId.format('%d');
      var area = ee.Number(group.get('sum'));

      return ee.Feature(null, {
        nivel: feature.get('nivel'),
        unidad_id: feature.get('unidad_id'),
        id_ambito: feature.get('id_ambito'),
        nombre: feature.get('nombre'),
        zona: feature.get('zona'),
        dist_min_m: feature.get('dmin_m'),
        dist_max_m: feature.get('dmax_m'),
        year: year,
        class_id: classId,
        class_name: classNames.get(classKey, 'Clase no documentada'),
        class_origin: classOrigins.get(classKey, 'No definido'),
        area_ref_ha: areaRef,
        area_utm_ha: areaUtm,
        area_ha: area,
        area_pct_unidad: area.divide(areaUtm).multiply(100)
      });
    });
  });

  return ee.FeatureCollection(ee.List(nestedRows).flatten());
}

var listsByYear = years.map(function(year) {
  var collection = extractClassesForYear(year);
  return collection.toList(collection.size());
});

var classesBlock =
    ee.FeatureCollection(ee.List(listsByYear).flatten());

print(
    'PASO 5F-R — CLASES DE ANILLOS CORREGIDOS ' +
    START_YEAR + '–' + END_YEAR
);
print(
    'Longitud del bloque — esperado: 5',
    ee.Number(END_YEAR).subtract(START_YEAR).add(1)
);
print('Años — esperado: 5', years);
print('Filas del bloque', classesBlock.size());
print(
    'Unidades espaciales — esperado: 18',
    classesBlock.aggregate_array('unidad_id').distinct().size()
);
print(
    'Unidades por ámbito — esperado: 15',
    classesBlock
        .filter(ee.Filter.eq('nivel', 'ambito'))
        .aggregate_array('unidad_id')
        .distinct()
        .size()
);
print(
    'Unidades del sistema — esperado: 3',
    classesBlock
        .filter(ee.Filter.eq('nivel', 'sistema'))
        .aggregate_array('unidad_id')
        .distinct()
        .size()
);
print(
    'Cantidad de años distintos — esperado: 5',
    classesBlock.aggregate_array('year').distinct().size()
);
print(
    'Códigos de clase presentes',
    classesBlock.aggregate_array('class_id').distinct().sort()
);
print(
    'Clases no documentadas — esperado: 0',
    classesBlock
        .filter(ee.Filter.eq('class_name', 'Clase no documentada'))
        .size()
);
print('Vista previa — primeras 10 filas', classesBlock.limit(10));

Export.table.toDrive({
  collection: classesBlock,
  description: EXPORT_NAME,
  folder: 'MAPBIOMAS_LOMAS',
  fileNamePrefix: EXPORT_NAME,
  fileFormat: 'CSV',
  selectors: [
    'nivel',
    'unidad_id',
    'id_ambito',
    'nombre',
    'zona',
    'dist_min_m',
    'dist_max_m',
    'year',
    'class_id',
    'class_name',
    'class_origin',
    'area_ref_ha',
    'area_utm_ha',
    'area_ha',
    'area_pct_unidad'
  ]
});

print(
    'Se creó la tarea ' + EXPORT_NAME +
    '. No iniciarla hasta aprobar Console.'
);
