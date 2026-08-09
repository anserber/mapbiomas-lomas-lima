// PASO 7D2 — Resultados temporales finales de anillos externos.
// Unidades: 15 anillos por ámbito + 3 anillos del sistema disuelto.
// Usa únicamente los assets corregidos de periferia externa.
// W5 = resultado robusto; W3 = sensibilidad; 2021–2024 = censura derecha.
// No sumar los anillos por ámbito para obtener totales del sistema.

var ASSET_AMBITOS =
  'projects/mapbiomas-lomas-jhoreck/assets/inputs/' +
  'anillos_por_ambito_periferia_externa_gee';
var ASSET_SISTEMA =
  'projects/mapbiomas-lomas-jhoreck/assets/inputs/' +
  'anillos_sistema_periferia_externa_gee';
var ASSET_CLASES =
  'projects/mapbiomas-public/assets/peru/collection3/' +
  'mapbiomas_peru_collection3_integration_v1';
var ASSET_TRANSICIONES =
  'projects/mapbiomas-public/assets/peru/collection3/' +
  'mapbiomas_peru_collection3_transitions_v1';

var rawAmbitos = ee.FeatureCollection(ASSET_AMBITOS);
var rawSistema = ee.FeatureCollection(ASSET_SISTEMA);
var clases = ee.Image(ASSET_CLASES);
var transiciones = ee.Image(ASSET_TRANSICIONES);
var pixelHa = ee.Image.pixelArea().divide(10000);
var YEAR_START = 1985;
var YEAR_END = 2024;
var N_YEARS = 40;

var anillosAmbitos = rawAmbitos.map(function(feature) {
  var id = ee.String(feature.get('id_ambito'));
  var zona = ee.String(feature.get('zona'));
  return feature.set({
    nivel: 'ambito',
    unidad_id: id.cat('|').cat(zona),
    area_ref_ha: feature.get('area_ha')
  });
});

var anillosSistema = rawSistema.map(function(feature) {
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

function clase(year) {
  return clases.select('classification_' + year);
}

function loma(year) {
  return clase(year).eq(70).rename('estado');
}

function codigoTransicion(year) {
  return transiciones.select(
    'transitions_' + (year - 1) + '_' + year
  );
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

function recuperacionEstable(year, ventana) {
  return todosEstado(year - ventana, year - 1, 0)
    .and(todosEstado(year, year + ventana - 1, 1))
    .rename('evento');
}

function esUnaDe(image, values) {
  var resultado = ee.Image(0);
  values.forEach(function(value) {
    resultado = resultado.or(image.eq(value));
  });
  return resultado;
}

var CLASES_AGRO = [18, 21];
var CLASES_OTRAS_ANTROPICAS = [25, 30];

// ---------------------------------------------------------------------------
// 1. Persistencia y ruido de la clase 70.
// ---------------------------------------------------------------------------

var estados = [];
for (var y = YEAR_START; y <= YEAR_END; y++) {
  estados.push(loma(y));
}

var frecuencia70 = ee.ImageCollection.fromImages(estados)
  .sum()
  .rename('frecuencia_70');
var algunaVez70 = frecuencia70.gt(0);
var siempre70 = frecuencia70.eq(N_YEARS);

var ausenciasAisladas = ee.Image(0);
var aparicionesAisladas = ee.Image(0);
for (var i = 1; i < estados.length - 1; i++) {
  ausenciasAisladas = ausenciasAisladas.add(
    estados[i - 1].eq(1)
      .and(estados[i].eq(0))
      .and(estados[i + 1].eq(1))
  );
  aparicionesAisladas = aparicionesAisladas.add(
    estados[i - 1].eq(0)
      .and(estados[i].eq(1))
      .and(estados[i + 1].eq(0))
  );
}
var ruido = ausenciasAisladas.add(aparicionesAisladas).gt(0);

var rachaActual = ee.Image(0);
var rachaMaxima = ee.Image(0);
for (var j = 0; j < estados.length; j++) {
  rachaActual = rachaActual.add(1).multiply(estados[j]);
  rachaMaxima = rachaMaxima.max(rachaActual);
}

// ---------------------------------------------------------------------------
// 2. Eventos W3 y W5 clasificados por origen o destino.
// ---------------------------------------------------------------------------

var w3LossTotal = ee.Image(0);
var w3RecoveryTotal = ee.Image(0);

var w5LossTotal = ee.Image(0);
var w5LossTo68 = ee.Image(0);
var w5LossTo13 = ee.Image(0);
var w5LossTo24 = ee.Image(0);
var w5LossToAgro = ee.Image(0);
var w5LossToOtherAnthropic = ee.Image(0);
var w5LossToOther = ee.Image(0);

var w5RecoveryTotal = ee.Image(0);
var w5RecoveryFrom68 = ee.Image(0);
var w5RecoveryFrom13 = ee.Image(0);
var w5RecoveryFrom24 = ee.Image(0);
var w5RecoveryFromAgro = ee.Image(0);
var w5RecoveryFromOtherAnthropic = ee.Image(0);
var w5RecoveryFromOther = ee.Image(0);

for (var eventYear = 1988; eventYear <= 2022; eventYear++) {
  w3LossTotal = w3LossTotal.add(
    perdidaEstable(eventYear, 3)
  );
  w3RecoveryTotal = w3RecoveryTotal.add(
    recuperacionEstable(eventYear, 3)
  );

  if (eventYear >= 1990 && eventYear <= 2020) {
    var loss = perdidaEstable(eventYear, 5);
    var recovery = recuperacionEstable(eventYear, 5);
    var code = codigoTransicion(eventYear);
    var destination = code.mod(100);
    var origin = code.divide(100).floor();

    var loss68 = loss.and(destination.eq(68));
    var loss13 = loss.and(destination.eq(13));
    var loss24 = loss.and(destination.eq(24));
    var lossAgro = loss.and(esUnaDe(destination, CLASES_AGRO));
    var lossOtherAnthropic = loss.and(
      esUnaDe(destination, CLASES_OTRAS_ANTROPICAS)
    );
    var lossKnown = loss68
      .or(loss13)
      .or(loss24)
      .or(lossAgro)
      .or(lossOtherAnthropic);

    var rec68 = recovery.and(origin.eq(68));
    var rec13 = recovery.and(origin.eq(13));
    var rec24 = recovery.and(origin.eq(24));
    var recAgro = recovery.and(esUnaDe(origin, CLASES_AGRO));
    var recOtherAnthropic = recovery.and(
      esUnaDe(origin, CLASES_OTRAS_ANTROPICAS)
    );
    var recKnown = rec68
      .or(rec13)
      .or(rec24)
      .or(recAgro)
      .or(recOtherAnthropic);

    w5LossTotal = w5LossTotal.add(loss);
    w5LossTo68 = w5LossTo68.add(loss68);
    w5LossTo13 = w5LossTo13.add(loss13);
    w5LossTo24 = w5LossTo24.add(loss24);
    w5LossToAgro = w5LossToAgro.add(lossAgro);
    w5LossToOtherAnthropic =
      w5LossToOtherAnthropic.add(lossOtherAnthropic);
    w5LossToOther = w5LossToOther.add(loss.and(lossKnown.not()));

    w5RecoveryTotal = w5RecoveryTotal.add(recovery);
    w5RecoveryFrom68 = w5RecoveryFrom68.add(rec68);
    w5RecoveryFrom13 = w5RecoveryFrom13.add(rec13);
    w5RecoveryFrom24 = w5RecoveryFrom24.add(rec24);
    w5RecoveryFromAgro = w5RecoveryFromAgro.add(recAgro);
    w5RecoveryFromOtherAnthropic =
      w5RecoveryFromOtherAnthropic.add(recOtherAnthropic);
    w5RecoveryFromOther =
      w5RecoveryFromOther.add(recovery.and(recKnown.not()));
  }
}

// ---------------------------------------------------------------------------
// 3. Censura derecha 2021–2024.
// ---------------------------------------------------------------------------

var censoredLossTotal = ee.Image(0);
var censoredLossTo68 = ee.Image(0);
var censoredLossTo13 = ee.Image(0);
var censoredLossTo24 = ee.Image(0);
var censoredLossToAgro = ee.Image(0);
var censoredLossToOtherAnthropic = ee.Image(0);
var censoredLossToOther = ee.Image(0);

for (var recentYear = 2021; recentYear <= 2024; recentYear++) {
  var recentCode = codigoTransicion(recentYear);
  var recentOrigin = recentCode.divide(100).floor();
  var recentDestination = recentCode.mod(100);
  var recentLoss = recentOrigin.eq(70)
    .and(recentDestination.neq(70));
  var recent68 = recentLoss.and(recentDestination.eq(68));
  var recent13 = recentLoss.and(recentDestination.eq(13));
  var recent24 = recentLoss.and(recentDestination.eq(24));
  var recentAgro = recentLoss.and(
    esUnaDe(recentDestination, CLASES_AGRO)
  );
  var recentOtherAnthropic = recentLoss.and(
    esUnaDe(recentDestination, CLASES_OTRAS_ANTROPICAS)
  );
  var recentKnown = recent68
    .or(recent13)
    .or(recent24)
    .or(recentAgro)
    .or(recentOtherAnthropic);

  censoredLossTotal = censoredLossTotal.add(recentLoss);
  censoredLossTo68 = censoredLossTo68.add(recent68);
  censoredLossTo13 = censoredLossTo13.add(recent13);
  censoredLossTo24 = censoredLossTo24.add(recent24);
  censoredLossToAgro = censoredLossToAgro.add(recentAgro);
  censoredLossToOtherAnthropic =
    censoredLossToOtherAnthropic.add(recentOtherAnthropic);
  censoredLossToOther =
    censoredLossToOther.add(recentLoss.and(recentKnown.not()));
}

// ---------------------------------------------------------------------------
// 4. Una sola reducción multibanda.
// ---------------------------------------------------------------------------

var metricas = pixelHa.rename('area_grilla_ha')
  .addBands(
    pixelHa.updateMask(algunaVez70)
      .rename('area_alguna_vez_70_ha')
  )
  .addBands(
    pixelHa.updateMask(siempre70)
      .rename('area_siempre_70_ha')
  )
  .addBands(
    pixelHa.updateMask(estados[39])
      .rename('area_70_2024_ha')
  )
  .addBands(
    pixelHa.updateMask(ruido)
      .rename('area_ruido_aislado_ha')
  )
  .addBands(
    pixelHa.multiply(frecuencia70)
      .rename('frecuencia_70_year_ha')
  )
  .addBands(
    pixelHa.multiply(rachaMaxima)
      .rename('racha_maxima_year_ha')
  )
  .addBands(
    pixelHa.multiply(w3LossTotal)
      .rename('w3_loss_total_evento_ha')
  )
  .addBands(
    pixelHa.multiply(w3RecoveryTotal)
      .rename('w3_recovery_total_evento_ha')
  )
  .addBands(
    pixelHa.multiply(w5LossTotal)
      .rename('w5_loss_total_evento_ha')
  )
  .addBands(
    pixelHa.multiply(w5LossTo68)
      .rename('w5_loss_to68_evento_ha')
  )
  .addBands(
    pixelHa.multiply(w5LossTo13)
      .rename('w5_loss_to13_evento_ha')
  )
  .addBands(
    pixelHa.multiply(w5LossTo24)
      .rename('w5_loss_to24_evento_ha')
  )
  .addBands(
    pixelHa.multiply(w5LossToAgro)
      .rename('w5_loss_to_agro_evento_ha')
  )
  .addBands(
    pixelHa.multiply(w5LossToOtherAnthropic)
      .rename('w5_loss_to_otra_antropica_evento_ha')
  )
  .addBands(
    pixelHa.multiply(w5LossToOther)
      .rename('w5_loss_to_other_evento_ha')
  )
  .addBands(
    pixelHa.multiply(w5RecoveryTotal)
      .rename('w5_recovery_total_evento_ha')
  )
  .addBands(
    pixelHa.multiply(w5RecoveryFrom68)
      .rename('w5_recovery_from68_evento_ha')
  )
  .addBands(
    pixelHa.multiply(w5RecoveryFrom13)
      .rename('w5_recovery_from13_evento_ha')
  )
  .addBands(
    pixelHa.multiply(w5RecoveryFrom24)
      .rename('w5_recovery_from24_evento_ha')
  )
  .addBands(
    pixelHa.multiply(w5RecoveryFromAgro)
      .rename('w5_recovery_from_agro_evento_ha')
  )
  .addBands(
    pixelHa.multiply(w5RecoveryFromOtherAnthropic)
      .rename('w5_recovery_from_otra_antropica_evento_ha')
  )
  .addBands(
    pixelHa.multiply(w5RecoveryFromOther)
      .rename('w5_recovery_from_other_evento_ha')
  )
  .addBands(
    pixelHa.multiply(censoredLossTotal)
      .rename('censura_loss_total_evento_ha')
  )
  .addBands(
    pixelHa.multiply(censoredLossTo68)
      .rename('censura_loss_to68_evento_ha')
  )
  .addBands(
    pixelHa.multiply(censoredLossTo13)
      .rename('censura_loss_to13_evento_ha')
  )
  .addBands(
    pixelHa.multiply(censoredLossTo24)
      .rename('censura_loss_to24_evento_ha')
  )
  .addBands(
    pixelHa.multiply(censoredLossToAgro)
      .rename('censura_loss_to_agro_evento_ha')
  )
  .addBands(
    pixelHa.multiply(censoredLossToOtherAnthropic)
      .rename('censura_loss_to_otra_antropica_evento_ha')
  )
  .addBands(
    pixelHa.multiply(censoredLossToOther)
      .rename('censura_loss_to_other_evento_ha')
  );

var reducido = metricas.reduceRegions({
  collection: unidades,
  reducer: ee.Reducer.sum(),
  scale: 30,
  tileScale: 4
});

function numero(feature, field) {
  return ee.Number(ee.Algorithms.If(
    feature.propertyNames().contains(field),
    feature.get(field),
    0
  ));
}

var finalAnillos = reducido.map(function(feature) {
  var ever = numero(feature, 'area_alguna_vez_70_ha');
  var loss = numero(feature, 'w5_loss_total_evento_ha');
  var lossParts = numero(feature, 'w5_loss_to68_evento_ha')
    .add(numero(feature, 'w5_loss_to13_evento_ha'))
    .add(numero(feature, 'w5_loss_to24_evento_ha'))
    .add(numero(feature, 'w5_loss_to_agro_evento_ha'))
    .add(numero(
      feature, 'w5_loss_to_otra_antropica_evento_ha'
    ))
    .add(numero(feature, 'w5_loss_to_other_evento_ha'));
  var recovery = numero(feature, 'w5_recovery_total_evento_ha');
  var recoveryParts = numero(
    feature, 'w5_recovery_from68_evento_ha'
  )
    .add(numero(feature, 'w5_recovery_from13_evento_ha'))
    .add(numero(feature, 'w5_recovery_from24_evento_ha'))
    .add(numero(feature, 'w5_recovery_from_agro_evento_ha'))
    .add(numero(
      feature, 'w5_recovery_from_otra_antropica_evento_ha'
    ))
    .add(numero(feature, 'w5_recovery_from_other_evento_ha'));

  return ee.Feature(null, {
    nivel: feature.get('nivel'),
    unidad_id: feature.get('unidad_id'),
    id_ambito: feature.get('id_ambito'),
    nombre: feature.get('nombre'),
    zona: feature.get('zona'),
    dist_min_m: feature.get('dmin_m'),
    dist_max_m: feature.get('dmax_m'),
    area_ref_ha: feature.get('area_ref_ha'),
    periodo: '1985–2024',
    metodo_principal: 'W5',
    area_grilla_ha: numero(feature, 'area_grilla_ha'),
    area_alguna_vez_70_ha: ever,
    area_siempre_70_ha: numero(feature, 'area_siempre_70_ha'),
    area_70_2024_ha: numero(feature, 'area_70_2024_ha'),
    area_ruido_aislado_ha:
      numero(feature, 'area_ruido_aislado_ha'),
    ruido_pct_alguna_vez_70:
      numero(feature, 'area_ruido_aislado_ha')
        .divide(ever.max(0.000001)).multiply(100),
    frecuencia_media_years_alguna_vez_70:
      numero(feature, 'frecuencia_70_year_ha')
        .divide(ever.max(0.000001)),
    racha_maxima_media_years_alguna_vez_70:
      numero(feature, 'racha_maxima_year_ha')
        .divide(ever.max(0.000001)),
    w3_loss_total_evento_ha:
      numero(feature, 'w3_loss_total_evento_ha'),
    w3_recovery_total_evento_ha:
      numero(feature, 'w3_recovery_total_evento_ha'),
    w5_loss_total_evento_ha: loss,
    w5_loss_to68_intercambio_evento_ha:
      numero(feature, 'w5_loss_to68_evento_ha'),
    w5_loss_to13_natural_pendiente_evento_ha:
      numero(feature, 'w5_loss_to13_evento_ha'),
    w5_loss_to24_urbano_evento_ha:
      numero(feature, 'w5_loss_to24_evento_ha'),
    w5_loss_to_agro_evento_ha:
      numero(feature, 'w5_loss_to_agro_evento_ha'),
    w5_loss_to_otra_antropica_evento_ha:
      numero(feature, 'w5_loss_to_otra_antropica_evento_ha'),
    w5_loss_to_other_pendiente_evento_ha:
      numero(feature, 'w5_loss_to_other_evento_ha'),
    w5_loss_control_diferencia_ha:
      loss.subtract(lossParts).abs(),
    w5_recovery_total_evento_ha: recovery,
    w5_recovery_from68_intercambio_evento_ha:
      numero(feature, 'w5_recovery_from68_evento_ha'),
    w5_recovery_from13_natural_pendiente_evento_ha:
      numero(feature, 'w5_recovery_from13_evento_ha'),
    w5_recovery_from24_evento_ha:
      numero(feature, 'w5_recovery_from24_evento_ha'),
    w5_recovery_from_agro_evento_ha:
      numero(feature, 'w5_recovery_from_agro_evento_ha'),
    w5_recovery_from_otra_antropica_evento_ha:
      numero(
        feature, 'w5_recovery_from_otra_antropica_evento_ha'
      ),
    w5_recovery_from_other_pendiente_evento_ha:
      numero(feature, 'w5_recovery_from_other_evento_ha'),
    w5_recovery_control_diferencia_ha:
      recovery.subtract(recoveryParts).abs(),
    censura_2021_2024_loss_total_evento_ha:
      numero(feature, 'censura_loss_total_evento_ha'),
    censura_loss_to68_evento_ha:
      numero(feature, 'censura_loss_to68_evento_ha'),
    censura_loss_to13_evento_ha:
      numero(feature, 'censura_loss_to13_evento_ha'),
    censura_loss_to24_evento_ha:
      numero(feature, 'censura_loss_to24_evento_ha'),
    censura_loss_to_agro_evento_ha:
      numero(feature, 'censura_loss_to_agro_evento_ha'),
    censura_loss_to_otra_antropica_evento_ha:
      numero(
        feature, 'censura_loss_to_otra_antropica_evento_ha'
      ),
    censura_loss_to_other_evento_ha:
      numero(feature, 'censura_loss_to_other_evento_ha')
  });
});

var finalAmbitos = finalAnillos.filter(
  ee.Filter.eq('nivel', 'ambito')
);
var finalSistema = finalAnillos.filter(
  ee.Filter.eq('nivel', 'sistema')
);

print('PASO 7D2 — RESULTADOS FINALES DE ANILLOS');
print('Unidades totales — esperado: 18', finalAnillos.size());
print('Anillos por ámbito — esperado: 15', finalAmbitos.size());
print('Anillos del sistema — esperado: 3', finalSistema.size());
print(
  'Unidades únicas — esperado: 18',
  finalAnillos.aggregate_array('unidad_id').distinct().size()
);
print(
  'Zonas del sistema — esperado: 3',
  finalSistema.aggregate_array('zona').sort()
);
print(
  'Control pérdida W5 — diferencia máxima; esperado ≈ 0',
  finalAnillos.aggregate_max('w5_loss_control_diferencia_ha')
);
print(
  'Control recuperación W5 — diferencia máxima; esperado ≈ 0',
  finalAnillos.aggregate_max('w5_recovery_control_diferencia_ha')
);
print('Tabla final — sistema disuelto', finalSistema.sort('dist_min_m'));
print(
  'Sistema — pérdida W5 hacia urbano por zona',
  finalSistema.sort('dist_min_m')
    .aggregate_array('w5_loss_to24_urbano_evento_ha')
);
print(
  'Sistema — intercambio W5 70→68 por zona',
  finalSistema.sort('dist_min_m')
    .aggregate_array('w5_loss_to68_intercambio_evento_ha')
);
print(
  'Sistema — candidatos censurados hacia urbano por zona',
  finalSistema.sort('dist_min_m')
    .aggregate_array('censura_loss_to24_evento_ha')
);
print(
  'Tabla final — anillos por ámbito',
  finalAmbitos.sort('unidad_id')
);

Export.table.toDrive({
  collection: finalAnillos,
  description:
    'paso07D2_resultados_finales_anillos_periferia_externa_1985_2024',
  folder: 'MAPBIOMAS_LOMAS',
  fileNamePrefix:
    'paso07D2_resultados_finales_anillos_periferia_externa_1985_2024',
  fileFormat: 'CSV'
});

Map.centerObject(unidades, 9);
Map.addLayer(
  w5LossTo24.gt(0).selfMask().clip(unidades.geometry()),
  {palette: ['D73027']},
  'W5 robusta 70→24 — anillos',
  true
);
Map.addLayer(
  censoredLossTo24.gt(0).selfMask().clip(unidades.geometry()),
  {palette: ['FF00FF']},
  'Censura 2021–2024 70→24 — anillos',
  false
);
Map.addLayer(
  anillosSistema.style({
    color: '00FFFF',
    fillColor: '00000000',
    width: 2
  }),
  {},
  'Anillos del sistema',
  true
);

print(
  'PASO 7D2 LISTO — revisar controles antes de ejecutar el Task.'
);
