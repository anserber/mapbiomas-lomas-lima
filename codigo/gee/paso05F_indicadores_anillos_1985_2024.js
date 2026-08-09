// PASO 5F-R — Indicadores de anillos de periferia externa 1985–2024.
// Revisión del 28-07-2026. No incluye el enclave interno de Carabayllo 2.
// Usa una reducción multibanda para ambos niveles espaciales.
// Crea una tarea de exportación, pero no la inicia automáticamente.

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
var years = ee.List.sequence(1985, 2024);
var scale = 30;
var nativeProjection =
  mapbiomas.select('classification_2024').projection();
var utm18s = ee.Projection('EPSG:32718');
var pixelAreaHa = ee.Image.pixelArea().divide(10000);

var anillosAmbitos = anillosAmbitosRaw.map(function (feature) {
  var id = ee.String(feature.get('id_ambito'));
  var zona = ee.String(feature.get('zona'));
  return feature.set({
    nivel: 'ambito',
    unidad_id: id.cat('|').cat(zona),
    area_ref_ha: feature.get('area_ha')
  });
});

var anillosSistema = anillosSistemaRaw.map(function (feature) {
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

function classificationForYear(year) {
  year = ee.Number(year);
  var bandName =
    ee.String('classification_').cat(year.format('%d'));
  return mapbiomas.select([bandName]).rename('class_id').unmask(0);
}

function propertyOrZero(feature, propertyName) {
  var value = feature.get(propertyName);
  return ee.Number(ee.Algorithms.If(
    ee.Algorithms.IsEqual(value, null),
    0,
    value
  ));
}

var emptyImage = ee.Image(0).select([]);
var metricsStack = ee.Image(years.iterate(function (year, accumulator) {
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
  collection: unidades,
  reducer: ee.Reducer.sum(),
  scale: scale,
  crs: nativeProjection,
  tileScale: 4
});

var nestedRows = wide.toList(wide.size()).map(function (item) {
  var feature = ee.Feature(item);
  var areaRef = ee.Number(feature.get('area_ref_ha'));
  var areaUtm = feature.geometry().area({
    maxError: 1,
    proj: utm18s
  }).divide(10000);

  return years.map(function (year) {
    year = ee.Number(year);
    var suffix = year.format('%d');
    var loma = propertyOrZero(
      feature, ee.String('loma_').cat(suffix)
    );
    var urbano = propertyOrZero(
      feature, ee.String('urbano_').cat(suffix)
    );
    var clasificada = propertyOrZero(
      feature, ee.String('clasificada_').cat(suffix)
    );
    var sinDato = propertyOrZero(
      feature, ee.String('sin_dato_').cat(suffix)
    );
    var areaPixeles = clasificada.add(sinDato);
    var otras = clasificada.subtract(loma).subtract(urbano);
    var diferenciaPixeles = areaPixeles.subtract(areaUtm);

    return ee.Feature(null, {
      nivel: feature.get('nivel'),
      unidad_id: feature.get('unidad_id'),
      id_ambito: feature.get('id_ambito'),
      nombre: feature.get('nombre'),
      zona: feature.get('zona'),
      dist_min_m: feature.get('dmin_m'),
      dist_max_m: feature.get('dmax_m'),
      year: year,
      area_ref_ha: areaRef,
      area_utm_ha: areaUtm,
      area_pixeles_ha: areaPixeles,
      dif_pix_utm_abs_pct:
        diferenciaPixeles.abs().divide(areaUtm).multiply(100),
      loma_ha: loma,
      loma_pct_unidad: loma.divide(areaUtm).multiply(100),
      urbano_ha: urbano,
      urbano_pct_unidad: urbano.divide(areaUtm).multiply(100),
      otras_clases_ha: otras,
      otras_clases_pct_unidad:
        otras.divide(areaUtm).multiply(100),
      clasificada_ha: clasificada,
      sin_dato_ha: sinDato,
      sin_dato_pct: ee.Number(ee.Algorithms.If(
        areaPixeles.gt(0),
        sinDato.divide(areaPixeles).multiply(100),
        0
      ))
    });
  });
});

var indicadores = ee.FeatureCollection(ee.List(nestedRows).flatten());
var indicadoresAmbitos =
  indicadores.filter(ee.Filter.eq('nivel', 'ambito'));
var indicadoresSistema =
  indicadores.filter(ee.Filter.eq('nivel', 'sistema'));

print(
  'PASO 5F-R — INDICADORES DE ANILLOS CORREGIDOS 1985–2024'
);
print('Cantidad de años — esperado: 40', years.size());
print('Bandas métricas — esperado: 160', metricsStack.bandNames().size());
print('Unidades espaciales — esperado: 18', wide.size());
print('Filas totales — esperado: 720', indicadores.size());
print(
  'Filas por ámbito — esperado: 600',
  indicadoresAmbitos.size()
);
print(
  'Filas del sistema — esperado: 120',
  indicadoresSistema.size()
);
print(
  'Unidades únicas — esperado: 18',
  indicadores.aggregate_array('unidad_id').distinct().size()
);
print(
  'Años únicos — esperado: 40',
  indicadores.aggregate_array('year').distinct().size()
);
print(
  'Sin dato máximo — porcentaje',
  indicadores.aggregate_max('sin_dato_pct')
);
print(
  'Diferencia píxeles frente a área UTM — máxima, %',
  indicadores.aggregate_max('dif_pix_utm_abs_pct')
);
print(
  'Vista previa — anillos por ámbito',
  indicadoresAmbitos.limit(10)
);
print(
  'Vista previa — sistema disuelto',
  indicadoresSistema.limit(10)
);

Export.table.toDrive({
  collection: indicadores,
  description: 'serie_indicadores_anillos_periferia_externa_1985_2024',
  folder: 'MAPBIOMAS_LOMAS',
  fileNamePrefix: 'serie_indicadores_anillos_periferia_externa_1985_2024',
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
    'area_ref_ha',
    'area_utm_ha',
    'area_pixeles_ha',
    'dif_pix_utm_abs_pct',
    'loma_ha',
    'loma_pct_unidad',
    'urbano_ha',
    'urbano_pct_unidad',
    'otras_clases_ha',
    'otras_clases_pct_unidad',
    'clasificada_ha',
    'sin_dato_ha',
    'sin_dato_pct'
  ]
});

Map.centerObject(unidades, 9);
Map.addLayer(
  anillosAmbitos.style({color: '00BFFF', fillColor: '00000000', width: 2}),
  {},
  'Anillos por ámbito — periferia externa'
);
Map.addLayer(
  anillosSistema.style({color: 'FF8C00', fillColor: '00000000', width: 3}),
  {},
  'Anillos del sistema — periferia externa'
);
Map.addLayer(
  classificationForYear(2024).selfMask(),
  {min: 1, max: 70, palette: ['cccccc', '00aa00', 'ff0000']},
  'Clasificación 2024 — referencia',
  false
);

print(
  'Se creó una tarea. No iniciarla hasta aprobar los controles de Console.'
);
