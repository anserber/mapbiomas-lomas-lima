// PASO 5E — Serie completa MapBiomas 1985–2024 por ámbito del ACR
// Crea dos tareas de exportación. Iniciar primero solo la tabla de indicadores.

var ACR_ASSET =
    'projects/mapbiomas-lomas-jhoreck/assets/inputs/acr_lomas_5_ambitos_gee';

var MAPBIOMAS_ASSET =
    'projects/mapbiomas-public/assets/peru/collection3/' +
    'mapbiomas_peru_collection3_integration_v1';

var acr = ee.FeatureCollection(ACR_ASSET);
var mapbiomas = ee.Image(MAPBIOMAS_ASSET);
var years = ee.List.sequence(1985, 2024);
var scale = 30;
var nativeProjection =
    mapbiomas.select('classification_2024').projection();
var utm18s = ee.Projection('EPSG:32718');
var pixelAreaHa = ee.Image.pixelArea().divide(10000);

function zeroIfNull(value) {
  return ee.Number(ee.Algorithms.If(value, value, 0));
}

function classificationForYear(year) {
  year = ee.Number(year);
  var bandName =
      ee.String('classification_').cat(year.format('%d'));
  return mapbiomas.select([bandName]).rename('class_id').unmask(0);
}

function summarizeYear(year) {
  year = ee.Number(year);
  var classification = classificationForYear(year);

  var metrics = ee.Image.cat([
    pixelAreaHa
        .updateMask(classification.eq(70))
        .rename('loma_ha'),
    pixelAreaHa
        .updateMask(classification.eq(24))
        .rename('urbano_ha'),
    pixelAreaHa
        .updateMask(classification.neq(0))
        .rename('clasificada_ha'),
    pixelAreaHa
        .updateMask(classification.eq(0))
        .rename('sin_dato_ha')
  ]);

  var reduced = metrics.reduceRegions({
    collection: acr,
    reducer: ee.Reducer.sum(),
    scale: scale,
    crs: nativeProjection,
    tileScale: 4
  });

  return reduced.map(function(feature) {
    var areaRef = ee.Number(feature.get('Area_Ha'));
    var areaUtm = feature.geometry().area(1, utm18s).divide(10000);
    var loma = zeroIfNull(feature.get('loma_ha'));
    var urbano = zeroIfNull(feature.get('urbano_ha'));
    var clasificada = zeroIfNull(feature.get('clasificada_ha'));
    var sinDato = zeroIfNull(feature.get('sin_dato_ha'));
    var areaPixeles = clasificada.add(sinDato);
    var otras = clasificada.subtract(loma).subtract(urbano);
    var diferenciaPixeles = areaPixeles.subtract(areaUtm);

    return ee.Feature(null, {
      id_ambito: feature.get('id_ambito'),
      nombre: feature.get('NOMBRE'),
      year: year,
      area_ref_ha: areaRef,
      area_utm_ha: areaUtm,
      area_pixeles_ha: areaPixeles,
      dif_pix_utm_ha: diferenciaPixeles,
      dif_pix_utm_abs_pct:
          diferenciaPixeles.abs().divide(areaUtm).multiply(100),
      loma_ha: loma,
      loma_pct_ambito: loma.divide(areaUtm).multiply(100),
      urbano_ha: urbano,
      urbano_pct_ambito: urbano.divide(areaUtm).multiply(100),
      otras_clases_ha: otras,
      otras_clases_pct_ambito:
          otras.divide(areaUtm).multiply(100),
      clasificada_ha: clasificada,
      sin_dato_ha: sinDato,
      sin_dato_pct:
          ee.Number(ee.Algorithms.If(
              areaPixeles.gt(0),
              sinDato.divide(areaPixeles).multiply(100),
              0
          ))
    });
  });
}

function groupedClassesForYear(year) {
  year = ee.Number(year);
  var classification = classificationForYear(year);
  var image = pixelAreaHa
      .rename('area_ha')
      .addBands(classification);

  var reduced = image.reduceRegions({
    collection: acr,
    reducer: ee.Reducer.sum().group({
      groupField: 1,
      groupName: 'class_id'
    }),
    scale: scale,
    crs: nativeProjection,
    tileScale: 4
  });

  var nestedRows = reduced.toList(reduced.size()).map(function(item) {
    var feature = ee.Feature(item);
    var areaUtm = feature.geometry().area(1, utm18s).divide(10000);
    var groups = ee.List(feature.get('groups'));

    return groups.map(function(groupItem) {
      var group = ee.Dictionary(groupItem);
      var area = ee.Number(group.get('sum'));

      return ee.Feature(null, {
        id_ambito: feature.get('id_ambito'),
        nombre: feature.get('NOMBRE'),
        year: year,
        class_id: group.get('class_id'),
        area_ha: area,
        area_pct_ambito: area.divide(areaUtm).multiply(100),
        area_utm_ha: areaUtm
      });
    });
  });

  return ee.FeatureCollection(ee.List(nestedRows).flatten());
}

var summaryLists = years.map(function(year) {
  var collection = summarizeYear(year);
  return collection.toList(collection.size());
});

var classLists = years.map(function(year) {
  var collection = groupedClassesForYear(year);
  return collection.toList(collection.size());
});

var summaryFull =
    ee.FeatureCollection(ee.List(summaryLists).flatten());

var classesFull =
    ee.FeatureCollection(ee.List(classLists).flatten());

print('PASO 5E — SERIE COMPLETA 1985–2024');
print('Años — esperado: 40', years.size());
print('Filas de indicadores — esperado: 200', summaryFull.size());
print(
    'Ámbitos en indicadores — esperado: 5',
    summaryFull.aggregate_array('id_ambito').distinct().sort()
);
print(
    'Años en indicadores — esperado: 40',
    summaryFull.aggregate_array('year').distinct().size()
);
print('Vista previa de indicadores', summaryFull.limit(10));
print('Filas de composición por clases', classesFull.size());
print('Vista previa de composición', classesFull.limit(10));
print(
    'Máximo sin dato — %',
    summaryFull.aggregate_max('sin_dato_pct')
);
print(
    'Máxima diferencia píxeles frente a área UTM — %',
    summaryFull.aggregate_max('dif_pix_utm_abs_pct')
);

Export.table.toDrive({
  collection: summaryFull,
  description: 'serie_indicadores_acr_1985_2024',
  folder: 'MAPBIOMAS_LOMAS',
  fileNamePrefix: 'serie_indicadores_acr_1985_2024',
  fileFormat: 'CSV',
  selectors: [
    'id_ambito',
    'nombre',
    'year',
    'area_ref_ha',
    'area_utm_ha',
    'area_pixeles_ha',
    'dif_pix_utm_ha',
    'dif_pix_utm_abs_pct',
    'loma_ha',
    'loma_pct_ambito',
    'urbano_ha',
    'urbano_pct_ambito',
    'otras_clases_ha',
    'otras_clases_pct_ambito',
    'clasificada_ha',
    'sin_dato_ha',
    'sin_dato_pct'
  ]
});

Export.table.toDrive({
  collection: classesFull,
  description: 'serie_clases_acr_1985_2024',
  folder: 'MAPBIOMAS_LOMAS',
  fileNamePrefix: 'serie_clases_acr_1985_2024',
  fileFormat: 'CSV',
  selectors: [
    'id_ambito',
    'nombre',
    'year',
    'class_id',
    'area_ha',
    'area_pct_ambito',
    'area_utm_ha'
  ]
});

print(
    'Se crearon dos tareas. Ejecutar primero solo ' +
    'serie_indicadores_acr_1985_2024.'
);
