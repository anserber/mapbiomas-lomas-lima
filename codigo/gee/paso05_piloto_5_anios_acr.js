// PASO 5C — Extracción piloto MapBiomas en los cinco ámbitos del ACR
// Años: 1985, 2000, 2009, 2010 y 2024
// Este script no ejecuta exportaciones.

var ACR_ASSET =
    'projects/mapbiomas-lomas-jhoreck/assets/inputs/acr_lomas_5_ambitos_gee';

var MAPBIOMAS_ASSET =
    'projects/mapbiomas-public/assets/peru/collection3/' +
    'mapbiomas_peru_collection3_integration_v1';

var acr = ee.FeatureCollection(ACR_ASSET);
var mapbiomas = ee.Image(MAPBIOMAS_ASSET);
var years = ee.List([1985, 2000, 2009, 2010, 2024]);
var scale = 30;
var nativeProjection =
    mapbiomas.select('classification_2024').projection();
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
    var areaUtm = feature.geometry()
        .area(1, ee.Projection('EPSG:32718'))
        .divide(10000);
    var loma = zeroIfNull(feature.get('loma_ha'));
    var urbano = zeroIfNull(feature.get('urbano_ha'));
    var clasificada = zeroIfNull(feature.get('clasificada_ha'));
    var sinDato = zeroIfNull(feature.get('sin_dato_ha'));
    var areaPixeles = clasificada.add(sinDato);

    return ee.Feature(null, {
      id_ambito: feature.get('id_ambito'),
      nombre: feature.get('NOMBRE'),
      year: year,
      area_ref_ha: areaRef,
      area_utm_ha: areaUtm,
      area_pixeles_ha: areaPixeles,
      loma_ha: loma,
      loma_pct_ambito: loma.divide(areaUtm).multiply(100),
      urbano_ha: urbano,
      urbano_pct_ambito: urbano.divide(areaUtm).multiply(100),
      clasificada_ha: clasificada,
      sin_dato_ha: sinDato,
      sin_dato_pct: sinDato.divide(areaPixeles).multiply(100)
    });
  });
}

function groupedClassesForYear(year) {
  year = ee.Number(year);
  var classification = classificationForYear(year);
  var image = pixelAreaHa
      .rename('area_ha')
      .addBands(classification.rename('class_id'));

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

  return reduced.map(function(feature) {
    return ee.Feature(null, {
      id_ambito: feature.get('id_ambito'),
      nombre: feature.get('NOMBRE'),
      year: year,
      groups: feature.get('groups')
    });
  });
}

var summaryPilot =
    ee.FeatureCollection(years.map(summarizeYear)).flatten();

var groupedPilot =
    ee.FeatureCollection(years.map(groupedClassesForYear)).flatten();

print('PASO 5C — Años piloto', years);
print('Filas resumen — esperado: 25', summaryPilot.size());
print(
    'Ámbitos únicos — esperado: 5',
    summaryPilot.aggregate_array('id_ambito').distinct().sort()
);
print(
    'Años únicos — esperado: 5',
    summaryPilot.aggregate_array('year').distinct().sort()
);
print('Resumen piloto — 25 filas', summaryPilot);
print(
    'Sin dato máximo — porcentaje',
    summaryPilot.aggregate_max('sin_dato_pct')
);
print(
    'Loma máxima — porcentaje del ámbito',
    summaryPilot.aggregate_max('loma_pct_ambito')
);
print(
    'Urbano máximo — porcentaje del ámbito',
    summaryPilot.aggregate_max('urbano_pct_ambito')
);
print(
    'Registro responsable del máximo de loma',
    ee.Feature(summaryPilot.sort('loma_pct_ambito', false).first())
        .toDictionary([
          'id_ambito',
          'nombre',
          'year',
          'loma_ha',
          'loma_pct_ambito'
        ])
);
print(
    'Registro responsable del máximo urbano',
    ee.Feature(summaryPilot.sort('urbano_pct_ambito', false).first())
        .toDictionary([
          'id_ambito',
          'nombre',
          'year',
          'urbano_ha',
          'urbano_pct_ambito'
        ])
);
print(
    'Composición completa por clases — propiedad groups',
    groupedPilot
);

var classification2024 = classificationForYear(2024);

Map.centerObject(acr, 10);
Map.addLayer(
    classification2024.eq(70).selfMask(),
    {palette: ['FFD700']},
    'Clase 70 — Loma 2024'
);
Map.addLayer(
    classification2024.eq(24).selfMask(),
    {palette: ['E31A1C']},
    'Clase 24 — Urbano 2024'
);
Map.addLayer(
    acr.style({
      color: '00FFFF',
      fillColor: '00000000',
      width: 3
    }),
    {},
    'ACR — 5 ámbitos'
);

print('PASO 5C FINALIZADO — no se ejecutaron exportaciones');
