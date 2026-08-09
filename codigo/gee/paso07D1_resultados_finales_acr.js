// PASO 7D1 — Resultados temporales finales para los cinco ámbitos ACR.
// Periodo 1985–2024. Unidad: ámbito ACR.
// Aplica las decisiones aprobadas en 7A–7C3:
// - W5 = resultado robusto principal;
// - W3 = sensibilidad;
// - excluye rupturas cartográficas conocidas;
// - separa intercambios naturales, cambios naturales pendientes y presiones;
// - conserva 2021–2024 como candidatos censurados, no como eventos W5.

var ASSET_ACR =
  'projects/mapbiomas-lomas-jhoreck/assets/inputs/acr_lomas_5_ambitos_gee';
var ASSET_CLASES =
  'projects/mapbiomas-public/assets/peru/collection3/' +
  'mapbiomas_peru_collection3_integration_v1';
var ASSET_TRANSICIONES =
  'projects/mapbiomas-public/assets/peru/collection3/' +
  'mapbiomas_peru_collection3_transitions_v1';

var acr = ee.FeatureCollection(ASSET_ACR);
var clases = ee.Image(ASSET_CLASES);
var transiciones = ee.Image(ASSET_TRANSICIONES);
var pixelHa = ee.Image.pixelArea().divide(10000);

var YEAR_START = 1985;
var YEAR_END = 2024;
var N_YEARS = 40;

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

// Clases antrópicas o transformadas previstas en el protocolo.
var CLASES_AGRO = [18, 21];
var CLASES_OTRAS_ANTROPICAS = [25, 30];

// Rupturas conocidas y comprobadas en el Paso 6.
var ancon = acr.filter(ee.Filter.eq('id_ambito', 'ancon'));
var carabayllo2 = acr.filter(
  ee.Filter.eq('id_ambito', 'carabayllo_2')
);

var rupturaAncon = codigoTransicion(2001).eq(7068)
  .clip(ancon.geometry())
  .unmask(0)
  .rename('ruptura');
var codigo2015 = codigoTransicion(2015);
var rupturaCarabayllo2 = codigo2015.eq(7013)
  .or(codigo2015.eq(7068))
  .clip(carabayllo2.geometry())
  .unmask(0)
  .rename('ruptura');
// ImageCollection.max() conserva la unión de las huellas enmascaradas.
// Las dos imágenes ya tienen el mismo nombre de banda, por lo que la
// colección es homogénea y fuera de ambas rupturas se completa con cero.
var rupturasConocidas = ee.ImageCollection.fromImages([
  rupturaAncon,
  rupturaCarabayllo2
]).max().unmask(0, false).rename('ruptura');
var fueraRuptura = rupturasConocidas.eq(0);

// ---------------------------------------------------------------------------
// 1. Persistencia y consistencia de clase 70.
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
// 2. Eventos robustos W5 y sensibilidad W3.
// ---------------------------------------------------------------------------

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

var w3LossTotal = ee.Image(0);
var w3RecoveryTotal = ee.Image(0);

for (var eventYear = 1988; eventYear <= 2022; eventYear++) {
  var lossW3 = perdidaEstable(eventYear, 3).and(fueraRuptura);
  var recoveryW3 = recuperacionEstable(eventYear, 3);
  w3LossTotal = w3LossTotal.add(lossW3);
  w3RecoveryTotal = w3RecoveryTotal.add(recoveryW3);

  if (eventYear >= 1990 && eventYear <= 2020) {
    var lossW5 = perdidaEstable(eventYear, 5).and(fueraRuptura);
    var recoveryW5 = recuperacionEstable(eventYear, 5);
    var code = codigoTransicion(eventYear);
    var destination = code.mod(100);
    var origin = code.divide(100).floor();

    var loss68 = lossW5.and(destination.eq(68));
    var loss13 = lossW5.and(destination.eq(13));
    var loss24 = lossW5.and(destination.eq(24));
    var lossAgro = lossW5.and(esUnaDe(destination, CLASES_AGRO));
    var lossOtherAnthropic = lossW5.and(
      esUnaDe(destination, CLASES_OTRAS_ANTROPICAS)
    );
    var lossKnown = loss68
      .or(loss13)
      .or(loss24)
      .or(lossAgro)
      .or(lossOtherAnthropic);
    var lossOther = lossW5.and(lossKnown.not());

    var rec68 = recoveryW5.and(origin.eq(68));
    var rec13 = recoveryW5.and(origin.eq(13));
    var rec24 = recoveryW5.and(origin.eq(24));
    var recAgro = recoveryW5.and(esUnaDe(origin, CLASES_AGRO));
    var recOtherAnthropic = recoveryW5.and(
      esUnaDe(origin, CLASES_OTRAS_ANTROPICAS)
    );
    var recKnown = rec68
      .or(rec13)
      .or(rec24)
      .or(recAgro)
      .or(recOtherAnthropic);
    var recOther = recoveryW5.and(recKnown.not());

    w5LossTotal = w5LossTotal.add(lossW5);
    w5LossTo68 = w5LossTo68.add(loss68);
    w5LossTo13 = w5LossTo13.add(loss13);
    w5LossTo24 = w5LossTo24.add(loss24);
    w5LossToAgro = w5LossToAgro.add(lossAgro);
    w5LossToOtherAnthropic =
      w5LossToOtherAnthropic.add(lossOtherAnthropic);
    w5LossToOther = w5LossToOther.add(lossOther);

    w5RecoveryTotal = w5RecoveryTotal.add(recoveryW5);
    w5RecoveryFrom68 = w5RecoveryFrom68.add(rec68);
    w5RecoveryFrom13 = w5RecoveryFrom13.add(rec13);
    w5RecoveryFrom24 = w5RecoveryFrom24.add(rec24);
    w5RecoveryFromAgro = w5RecoveryFromAgro.add(recAgro);
    w5RecoveryFromOtherAnthropic =
      w5RecoveryFromOtherAnthropic.add(recOtherAnthropic);
    w5RecoveryFromOther = w5RecoveryFromOther.add(recOther);
  }
}

// ---------------------------------------------------------------------------
// 3. Censura derecha: transiciones 2021–2024, sin confirmación W5.
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
    .and(recentDestination.neq(70))
    .and(fueraRuptura);

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
// 4. Reducción única y tabla final.
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
      .rename('w5_loss_total_filtrado_evento_ha')
  )
  .addBands(
    pixelHa.multiply(w5LossTo68)
      .rename('w5_loss_to68_intercambio_evento_ha')
  )
  .addBands(
    pixelHa.multiply(w5LossTo13)
      .rename('w5_loss_to13_natural_pendiente_evento_ha')
  )
  .addBands(
    pixelHa.multiply(w5LossTo24)
      .rename('w5_loss_to24_urbano_evento_ha')
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
      .rename('w5_loss_to_other_pendiente_evento_ha')
  )
  .addBands(
    pixelHa.multiply(w5RecoveryTotal)
      .rename('w5_recovery_total_evento_ha')
  )
  .addBands(
    pixelHa.multiply(w5RecoveryFrom68)
      .rename('w5_recovery_from68_intercambio_evento_ha')
  )
  .addBands(
    pixelHa.multiply(w5RecoveryFrom13)
      .rename('w5_recovery_from13_natural_pendiente_evento_ha')
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
      .rename('w5_recovery_from_other_pendiente_evento_ha')
  )
  .addBands(
    pixelHa.multiply(censoredLossTotal)
      .rename('censura_2021_2024_loss_total_evento_ha')
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
  )
  .addBands(
    pixelHa.updateMask(rupturasConocidas)
      .rename('ruptura_conocida_area_ha')
  );

var reducido = metricas.reduceRegions({
  collection: acr,
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

var finalAcr = reducido.map(function(feature) {
  var ever = numero(feature, 'area_alguna_vez_70_ha');
  var w5Loss = numero(
    feature, 'w5_loss_total_filtrado_evento_ha'
  );
  var lossParts = numero(
    feature, 'w5_loss_to68_intercambio_evento_ha'
  ).add(numero(
    feature, 'w5_loss_to13_natural_pendiente_evento_ha'
  )).add(numero(
    feature, 'w5_loss_to24_urbano_evento_ha'
  )).add(numero(
    feature, 'w5_loss_to_agro_evento_ha'
  )).add(numero(
    feature, 'w5_loss_to_otra_antropica_evento_ha'
  )).add(numero(
    feature, 'w5_loss_to_other_pendiente_evento_ha'
  ));

  var w5Recovery = numero(
    feature, 'w5_recovery_total_evento_ha'
  );
  var recoveryParts = numero(
    feature, 'w5_recovery_from68_intercambio_evento_ha'
  ).add(numero(
    feature, 'w5_recovery_from13_natural_pendiente_evento_ha'
  )).add(numero(
    feature, 'w5_recovery_from24_evento_ha'
  )).add(numero(
    feature, 'w5_recovery_from_agro_evento_ha'
  )).add(numero(
    feature, 'w5_recovery_from_otra_antropica_evento_ha'
  )).add(numero(
    feature, 'w5_recovery_from_other_pendiente_evento_ha'
  ));

  return ee.Feature(null, {
    id_ambito: feature.get('id_ambito'),
    nombre: feature.get('NOMBRE'),
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
    w5_loss_total_filtrado_evento_ha: w5Loss,
    w5_loss_to68_intercambio_evento_ha:
      numero(feature, 'w5_loss_to68_intercambio_evento_ha'),
    w5_loss_to13_natural_pendiente_evento_ha:
      numero(
        feature, 'w5_loss_to13_natural_pendiente_evento_ha'
      ),
    w5_loss_to24_urbano_evento_ha:
      numero(feature, 'w5_loss_to24_urbano_evento_ha'),
    w5_loss_to_agro_evento_ha:
      numero(feature, 'w5_loss_to_agro_evento_ha'),
    w5_loss_to_otra_antropica_evento_ha:
      numero(
        feature, 'w5_loss_to_otra_antropica_evento_ha'
      ),
    w5_loss_to_other_pendiente_evento_ha:
      numero(
        feature, 'w5_loss_to_other_pendiente_evento_ha'
      ),
    w5_loss_control_diferencia_ha:
      w5Loss.subtract(lossParts).abs(),
    w5_recovery_total_evento_ha: w5Recovery,
    w5_recovery_from68_intercambio_evento_ha:
      numero(
        feature, 'w5_recovery_from68_intercambio_evento_ha'
      ),
    w5_recovery_from13_natural_pendiente_evento_ha:
      numero(
        feature, 'w5_recovery_from13_natural_pendiente_evento_ha'
      ),
    w5_recovery_from24_evento_ha:
      numero(feature, 'w5_recovery_from24_evento_ha'),
    w5_recovery_from_agro_evento_ha:
      numero(feature, 'w5_recovery_from_agro_evento_ha'),
    w5_recovery_from_otra_antropica_evento_ha:
      numero(
        feature, 'w5_recovery_from_otra_antropica_evento_ha'
      ),
    w5_recovery_from_other_pendiente_evento_ha:
      numero(
        feature, 'w5_recovery_from_other_pendiente_evento_ha'
      ),
    w5_recovery_control_diferencia_ha:
      w5Recovery.subtract(recoveryParts).abs(),
    censura_2021_2024_loss_total_evento_ha:
      numero(
        feature, 'censura_2021_2024_loss_total_evento_ha'
      ),
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
      numero(feature, 'censura_loss_to_other_evento_ha'),
    ruptura_conocida_area_ha:
      numero(feature, 'ruptura_conocida_area_ha')
  });
});

print('PASO 7D1 — RESULTADOS FINALES ACR');
print('Ámbitos — esperado: 5', finalAcr.size());
print(
  'Orden de ámbitos',
  finalAcr.aggregate_array('id_ambito')
);
print('Tabla final ACR', finalAcr);
print(
  'Control pérdida W5 — diferencia máxima; esperado ≈ 0',
  finalAcr.aggregate_max('w5_loss_control_diferencia_ha')
);
print(
  'Control recuperación W5 — diferencia máxima; esperado ≈ 0',
  finalAcr.aggregate_max('w5_recovery_control_diferencia_ha')
);
print(
  'Pérdida W5 hacia urbano por ámbito — ha-evento',
  finalAcr.aggregate_array('w5_loss_to24_urbano_evento_ha')
);
print(
  'Pérdida W5 hacia agro por ámbito — ha-evento',
  finalAcr.aggregate_array('w5_loss_to_agro_evento_ha')
);
print(
  'Intercambio W5 70→68 por ámbito — ha-evento',
  finalAcr.aggregate_array('w5_loss_to68_intercambio_evento_ha')
);
print(
  'Cambio natural W5 70→13 pendiente por ámbito — ha-evento',
  finalAcr.aggregate_array(
    'w5_loss_to13_natural_pendiente_evento_ha'
  )
);
print(
  'Candidatos censurados 2021–2024 hacia urbano — ha-evento',
  finalAcr.aggregate_array('censura_loss_to24_evento_ha')
);

Export.table.toDrive({
  collection: finalAcr,
  description: 'paso07D1_resultados_finales_acr_1985_2024',
  fileNamePrefix: 'paso07D1_resultados_finales_acr_1985_2024',
  fileFormat: 'CSV'
});

Map.centerObject(acr, 9);
Map.addLayer(
  w5LossTo24.gt(0).selfMask().clip(acr.geometry()),
  {palette: ['D73027']},
  'W5 robusta 70→24 — presión urbana',
  true
);
Map.addLayer(
  w5LossTo68.gt(0).selfMask().clip(acr.geometry()),
  {palette: ['8C6BB1']},
  'W5 70→68 — intercambio natural excluido',
  false
);
Map.addLayer(
  w5LossTo13.gt(0).selfMask().clip(acr.geometry()),
  {palette: ['FDB863']},
  'W5 70→13 — natural pendiente',
  false
);
Map.addLayer(
  censoredLossTo24.gt(0).selfMask().clip(acr.geometry()),
  {palette: ['FF00FF']},
  'Censura 2021–2024 70→24',
  false
);
Map.addLayer(
  acr.style({
    color: '00FFFF',
    fillColor: '00000000',
    width: 2
  }),
  {},
  'Límites ACR',
  true
);

print(
  'PASO 7D1 LISTO — revisar controles y luego ejecutar el Task.'
);
