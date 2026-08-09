// PASO 5F — Composición completa por clases, bloque 1985–1989
// Una fila por ámbito, año y clase MapBiomas.
// Crea una tarea de exportación que no se inicia automáticamente.

var ACR_ASSET =
    'projects/mapbiomas-lomas-jhoreck/assets/inputs/acr_lomas_5_ambitos_gee';

var MAPBIOMAS_ASSET =
    'projects/mapbiomas-public/assets/peru/collection3/' +
    'mapbiomas_peru_collection3_integration_v1';

var acr = ee.FeatureCollection(ACR_ASSET);
var mapbiomas = ee.Image(MAPBIOMAS_ASSET);
var years = ee.List.sequence(1985, 1989);
var scale = 30;
var nativeProjection =
    mapbiomas.select('classification_2024').projection();
var utm18s = ee.Projection('EPSG:32718');
var pixelAreaHa = ee.Image.pixelArea().divide(10000);

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
    collection: acr,
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
    var areaRef = ee.Number(feature.get('Area_Ha'));
    var areaUtm = feature.geometry().area(1, utm18s).divide(10000);
    var groups = ee.List(feature.get('groups'));

    return groups.map(function(groupItem) {
      var group = ee.Dictionary(groupItem);
      var classId = ee.Number(group.get('class_id'));
      var classKey = classId.format('%d');
      var area = ee.Number(group.get('sum'));

      return ee.Feature(null, {
        id_ambito: feature.get('id_ambito'),
        nombre: feature.get('NOMBRE'),
        year: year,
        class_id: classId,
        class_name: classNames.get(classKey, 'Clase no documentada'),
        class_origin: classOrigins.get(classKey, 'No definido'),
        area_ref_ha: areaRef,
        area_utm_ha: areaUtm,
        area_ha: area,
        area_pct_ambito: area.divide(areaUtm).multiply(100)
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

print('PASO 5F — CLASES 1985–1989');
print('Años — esperado: 5', years);
print('Filas del bloque', classesBlock.size());
print(
    'Ámbitos — esperado: 5',
    classesBlock.aggregate_array('id_ambito').distinct().sort()
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
  description: 'serie_clases_acr_1985_1989',
  folder: 'MAPBIOMAS_LOMAS',
  fileNamePrefix: 'serie_clases_acr_1985_1989',
  fileFormat: 'CSV',
  selectors: [
    'id_ambito',
    'nombre',
    'year',
    'class_id',
    'class_name',
    'class_origin',
    'area_ref_ha',
    'area_utm_ha',
    'area_ha',
    'area_pct_ambito'
  ]
});

print(
    'Se creó una tarea para 1985–1989. No iniciarla hasta aprobar Console.'
);
