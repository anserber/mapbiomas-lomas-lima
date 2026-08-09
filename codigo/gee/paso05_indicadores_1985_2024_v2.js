// PASO 5E — Indicadores 1985–2024, versión optimizada
// Usa una sola reducción multibanda para evitar agregaciones concurrentes.
// Crea una tarea de exportación, pero no la inicia automáticamente.

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

function classificationForYear(year) {
  year = ee.Number(year);
  var bandName =
      ee.String('classification_').cat(year.format('%d'));
  return mapbiomas.select([bandName]).rename('class_id').unmask(0);
}

function propertyOrZero(feature, propertyName) {
  var value = feature.get(propertyName);
  return ee.Number(ee.Algorithms.If(value, value, 0));
}

var emptyImage = ee.Image(0).select([]);

var metricsStack = ee.Image(years.iterate(function(year, accumulator) {
  year = ee.Number(year);
  var suffix = year.format('%d');
  var classification = classificationForYear(year);

  var metricsYear = ee.Image.cat([
    pixelAreaHa
        .updateMask(classification.eq(70))
        .rename(ee.String('loma_').cat(suffix)),
    pixelAreaHa
        .updateMask(classification.eq(24))
        .rename(ee.String('urbano_').cat(suffix)),
    pixelAreaHa
        .updateMask(classification.neq(0))
        .rename(ee.String('clasificada_').cat(suffix)),
    pixelAreaHa
        .updateMask(classification.eq(0))
        .rename(ee.String('sin_dato_').cat(suffix))
  ]);

  return ee.Image(accumulator).addBands(metricsYear);
}, emptyImage));

var wide = metricsStack.reduceRegions({
  collection: acr,
  reducer: ee.Reducer.sum(),
  scale: scale,
  crs: nativeProjection,
  tileScale: 4
});

var nestedRows = wide.toList(wide.size()).map(function(item) {
  var feature = ee.Feature(item);
  var areaRef = ee.Number(feature.get('Area_Ha'));
  var areaUtm = feature.geometry().area(1, utm18s).divide(10000);

  return years.map(function(year) {
    year = ee.Number(year);
    var suffix = year.format('%d');
    var loma = propertyOrZero(
        feature,
        ee.String('loma_').cat(suffix)
    );
    var urbano = propertyOrZero(
        feature,
        ee.String('urbano_').cat(suffix)
    );
    var clasificada = propertyOrZero(
        feature,
        ee.String('clasificada_').cat(suffix)
    );
    var sinDato = propertyOrZero(
        feature,
        ee.String('sin_dato_').cat(suffix)
    );
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
});

var summaryFull =
    ee.FeatureCollection(ee.List(nestedRows).flatten());

print('PASO 5E — INDICADORES OPTIMIZADOS');
print('Bandas métricas — esperado: 160', metricsStack.bandNames().size());
print('Ámbitos reducidos — esperado: 5', wide.size());
print('Filas construidas — esperado: 200', summaryFull.size());
print('Vista previa — primeras 10 filas', summaryFull.limit(10));
print(
    'Control de ámbitos',
    summaryFull.aggregate_array('id_ambito').distinct().sort()
);
print(
    'Cantidad de años distintos — esperado: 40',
    summaryFull.aggregate_array('year').distinct().size()
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

print(
    'Se creó una tarea de indicadores. No iniciarla hasta aprobar Console.'
);
