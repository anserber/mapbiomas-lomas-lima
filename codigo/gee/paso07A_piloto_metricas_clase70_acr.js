// PASO 7A — Piloto de consistencia temporal de la clase 70.
// Unidad: cinco ámbitos del ACR Sistema de Lomas de Lima.
// Periodo: 1985–2024.
// No exporta archivos ni interpreta impacto ecológico.

var ASSET_ACR =
  'projects/mapbiomas-lomas-jhoreck/assets/inputs/acr_lomas_5_ambitos_gee';
var ASSET_CLASES =
  'projects/mapbiomas-public/assets/peru/collection3/' +
  'mapbiomas_peru_collection3_integration_v1';

var acr = ee.FeatureCollection(ASSET_ACR);
var clases = ee.Image(ASSET_CLASES);
var YEAR_START = 1985;
var YEAR_END = 2024;
var N_YEARS = YEAR_END - YEAR_START + 1;

// Serie binaria anual: 1 = clase 70; 0 = otra clase.
var lomaPorYear = [];
for (var year = YEAR_START; year <= YEAR_END; year++) {
  lomaPorYear.push(
    clases
      .select('classification_' + year)
      .eq(70)
      .rename('loma')
  );
}

var frecuencia70 = ee.ImageCollection.fromImages(lomaPorYear)
  .sum()
  .rename('frecuencia_70');

// Número de alternancias entre años consecutivos.
var cambiosEstado = ee.Image(0);
for (var i = 1; i < lomaPorYear.length; i++) {
  cambiosEstado = cambiosEstado.add(
    lomaPorYear[i].neq(lomaPorYear[i - 1])
  );
}
cambiosEstado = cambiosEstado.rename('cambios_estado');

// Reversiones inmediatas: 70-no70-70 y no70-70-no70.
var ausenciasAisladas = ee.Image(0);
var aparicionesAisladas = ee.Image(0);
for (var j = 1; j < lomaPorYear.length - 1; j++) {
  var anterior = lomaPorYear[j - 1];
  var actual = lomaPorYear[j];
  var siguiente = lomaPorYear[j + 1];

  ausenciasAisladas = ausenciasAisladas.add(
    anterior.eq(1).and(actual.eq(0)).and(siguiente.eq(1))
  );
  aparicionesAisladas = aparicionesAisladas.add(
    anterior.eq(0).and(actual.eq(1)).and(siguiente.eq(0))
  );
}
ausenciasAisladas = ausenciasAisladas.rename('ausencias_aisladas');
aparicionesAisladas = aparicionesAisladas.rename('apariciones_aisladas');

var eventosAislados = ausenciasAisladas
  .add(aparicionesAisladas)
  .rename('eventos_aislados');

// Racha máxima de presencia consecutiva de clase 70.
var rachaActual = ee.Image(0);
var rachaMaxima = ee.Image(0);
for (var k = 0; k < lomaPorYear.length; k++) {
  rachaActual = rachaActual.add(1).multiply(lomaPorYear[k]);
  rachaMaxima = rachaMaxima.max(rachaActual);
}
rachaMaxima = rachaMaxima.rename('racha_maxima_70');

var pixelHa = ee.Image.pixelArea().divide(10000);
var algunaVez70 = frecuencia70.gt(0);
var siempre70 = frecuencia70.eq(N_YEARS);
var ruido = eventosAislados.gt(0);
var clase70_2024 = lomaPorYear[lomaPorYear.length - 1];

// Bandas preponderadas para resumir todo con una sola reducción.
var metricasArea = pixelHa.rename('area_grilla_ha')
  .addBands(
    pixelHa.updateMask(algunaVez70).rename('area_alguna_vez_70_ha')
  )
  .addBands(
    pixelHa.updateMask(siempre70).rename('area_siempre_70_ha')
  )
  .addBands(
    pixelHa.updateMask(ruido).rename('area_con_ruido_ha')
  )
  .addBands(
    pixelHa.updateMask(clase70_2024).rename('area_70_2024_ha')
  )
  .addBands(
    pixelHa.multiply(frecuencia70).rename('frecuencia_year_ha')
  )
  .addBands(
    pixelHa.multiply(rachaMaxima).rename('racha_maxima_year_ha')
  )
  .addBands(
    pixelHa.multiply(cambiosEstado).rename('cambios_estado_evento_ha')
  )
  .addBands(
    pixelHa.multiply(ausenciasAisladas)
      .rename('ausencias_aisladas_evento_ha')
  )
  .addBands(
    pixelHa.multiply(aparicionesAisladas)
      .rename('apariciones_aisladas_evento_ha')
  )
  // Distribución transparente de frecuencia.
  .addBands(
    pixelHa.updateMask(frecuencia70.eq(0)).rename('freq_0_ha')
  )
  .addBands(
    pixelHa.updateMask(frecuencia70.gte(1).and(frecuencia70.lte(10)))
      .rename('freq_1_10_ha')
  )
  .addBands(
    pixelHa.updateMask(frecuencia70.gte(11).and(frecuencia70.lte(20)))
      .rename('freq_11_20_ha')
  )
  .addBands(
    pixelHa.updateMask(frecuencia70.gte(21).and(frecuencia70.lte(30)))
      .rename('freq_21_30_ha')
  )
  .addBands(
    pixelHa.updateMask(frecuencia70.gte(31).and(frecuencia70.lte(39)))
      .rename('freq_31_39_ha')
  )
  .addBands(
    pixelHa.updateMask(frecuencia70.eq(40)).rename('freq_40_ha')
  );

var resumenBruto = metricasArea.reduceRegions({
  collection: acr,
  reducer: ee.Reducer.sum(),
  scale: 30,
  tileScale: 4
});

function numero(feature, field) {
  var nombres = feature.propertyNames();
  return ee.Number(ee.Algorithms.If(
    nombres.contains(field),
    feature.get(field),
    0
  ));
}

var resumen = resumenBruto.map(function(feature) {
  var areaGrilla = numero(feature, 'area_grilla_ha');
  var areaEver = numero(feature, 'area_alguna_vez_70_ha');
  var freqYearHa = numero(feature, 'frecuencia_year_ha');
  var runYearHa = numero(feature, 'racha_maxima_year_ha');
  var changesEventHa = numero(feature, 'cambios_estado_evento_ha');
  var ruidoArea = numero(feature, 'area_con_ruido_ha');

  var denominadorEver = areaEver.max(0.000001);

  return ee.Feature(null, {
    id_ambito: feature.get('id_ambito'),
    nombre: feature.get('NOMBRE'),
    area_grilla_ha: areaGrilla,
    area_alguna_vez_70_ha: areaEver,
    area_siempre_70_ha: numero(feature, 'area_siempre_70_ha'),
    area_70_2024_ha: numero(feature, 'area_70_2024_ha'),
    area_con_ruido_ha: ruidoArea,
    ruido_pct_area_alguna_vez_70:
      ruidoArea.divide(denominadorEver).multiply(100),
    frecuencia_media_years_area_total:
      freqYearHa.divide(areaGrilla),
    frecuencia_media_years_area_alguna_vez_70:
      freqYearHa.divide(denominadorEver),
    frecuencia_media_pct_area_alguna_vez_70:
      freqYearHa.divide(denominadorEver).divide(N_YEARS).multiply(100),
    racha_maxima_media_years_area_alguna_vez_70:
      runYearHa.divide(denominadorEver),
    cambios_estado_medios_area_alguna_vez_70:
      changesEventHa.divide(denominadorEver),
    ausencias_aisladas_evento_ha:
      numero(feature, 'ausencias_aisladas_evento_ha'),
    apariciones_aisladas_evento_ha:
      numero(feature, 'apariciones_aisladas_evento_ha'),
    freq_0_ha: numero(feature, 'freq_0_ha'),
    freq_1_10_ha: numero(feature, 'freq_1_10_ha'),
    freq_11_20_ha: numero(feature, 'freq_11_20_ha'),
    freq_21_30_ha: numero(feature, 'freq_21_30_ha'),
    freq_31_39_ha: numero(feature, 'freq_31_39_ha'),
    freq_40_ha: numero(feature, 'freq_40_ha')
  });
});

var rangosBrutos = frecuencia70
  .addBands(rachaMaxima)
  .addBands(eventosAislados)
  .addBands(cambiosEstado)
  .reduceRegion({
    reducer: ee.Reducer.minMax(),
    geometry: acr.geometry(),
    scale: 30,
    maxPixels: 1e9,
    tileScale: 4
  });

var controlRangos = ee.Dictionary({
  frecuencia_min: rangosBrutos.get('frecuencia_70_min'),
  frecuencia_max: rangosBrutos.get('frecuencia_70_max'),
  racha_maxima_min: rangosBrutos.get('racha_maxima_70_min'),
  racha_maxima_max: rangosBrutos.get('racha_maxima_70_max'),
  eventos_aislados_max: rangosBrutos.get('eventos_aislados_max'),
  cambios_estado_max: rangosBrutos.get('cambios_estado_max')
});

print('PASO 7A — PILOTO MÉTRICAS CLASE 70');
print('Años — esperado: 40', N_YEARS);
print('Ámbitos — esperado: 5', acr.size());
print('Orden de ámbitos', resumen.aggregate_array('id_ambito'));
print('Control de rangos', controlRangos);
print('Resumen por ámbito — esperado: 5 filas', resumen);
print('Área de grilla por ámbito — ha',
  resumen.aggregate_array('area_grilla_ha'));
print('Área alguna vez clase 70 — ha',
  resumen.aggregate_array('area_alguna_vez_70_ha'));
print('Área siempre clase 70 — ha',
  resumen.aggregate_array('area_siempre_70_ha'));
print('Área con alguna reversión aislada — ha',
  resumen.aggregate_array('area_con_ruido_ha'));
print('Ruido respecto al área alguna vez clase 70 — %',
  resumen.aggregate_array('ruido_pct_area_alguna_vez_70'));
print('Frecuencia media — años, solo píxeles alguna vez clase 70',
  resumen.aggregate_array('frecuencia_media_years_area_alguna_vez_70'));
print('Racha máxima media — años, solo píxeles alguna vez clase 70',
  resumen.aggregate_array('racha_maxima_media_years_area_alguna_vez_70'));

Map.centerObject(acr, 10);
Map.addLayer(
  frecuencia70.clip(acr.geometry()),
  {
    min: 0,
    max: 40,
    palette: ['F5F5F5', 'FEE08B', 'FDAE61', '66BD63', '006837']
  },
  'Frecuencia clase 70 — 1985–2024'
);
Map.addLayer(
  eventosAislados.selfMask().clip(acr.geometry()),
  {
    min: 1,
    max: 8,
    palette: ['FFF7BC', 'FEC44F', 'D95F0E', '7F0000']
  },
  'Reversiones aisladas — ruido potencial',
  false
);
Map.addLayer(
  acr.style({color: '00FFFF', fillColor: '00000000', width: 2}),
  {},
  'Límites ACR',
  true
);

print('PASO 7A FINALIZADO — no se ejecutaron exportaciones.');
