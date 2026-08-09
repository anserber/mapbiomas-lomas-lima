// PASO 6F1-B — Diagnóstico del asset de transiciones frente a bandas anuales.
// Compara dos casos: sistema 0–500 m 2021–2022 y Villa María 2022–2023.
// No exporta archivos.

var ASSET_ACR =
  'projects/mapbiomas-lomas-jhoreck/assets/inputs/acr_lomas_5_ambitos_gee';
var ASSET_ANILLOS =
  'projects/mapbiomas-lomas-jhoreck/assets/inputs/' +
  'anillos_sistema_periferia_externa_gee';
var ASSET_CLASES =
  'projects/mapbiomas-public/assets/peru/collection3/' +
  'mapbiomas_peru_collection3_integration_v1';
var ASSET_TRANSICIONES =
  'projects/mapbiomas-public/assets/peru/collection3/' +
  'mapbiomas_peru_collection3_transitions_v1';

var acr = ee.FeatureCollection(ASSET_ACR);
var anillos = ee.FeatureCollection(ASSET_ANILLOS);
var clases = ee.Image(ASSET_CLASES);
var transiciones = ee.Image(ASSET_TRANSICIONES);

var casos = [
  {
    id: 'CV-009',
    unidad: anillos.filter(ee.Filter.eq('zona', '0_500')),
    inicio: 2021,
    fin: 2022,
    esperado_ha: 12.932611665182671
  },
  {
    id: 'CV-017',
    unidad: acr.filter(ee.Filter.eq('id_ambito', 'villa_maria')),
    inicio: 2022,
    fin: 2023,
    esperado_ha: 1.5217137626618031
  }
];

function auditar(caso) {
  var geometria = caso.unidad.geometry();
  var banda = 'transitions_' + caso.inicio + '_' + caso.fin;
  var oficialCodigo = transiciones.select(banda);
  var reconstruidoCodigo = clases
    .select('classification_' + caso.inicio)
    .multiply(100)
    .add(clases.select('classification_' + caso.fin))
    .toInt16();

  var oficial7024 = oficialCodigo.eq(7024).clip(geometria);
  var reconstruido7024 = reconstruidoCodigo.eq(7024).clip(geometria);
  var diferencia = oficial7024.unmask(0)
    .neq(reconstruido7024.unmask(0))
    .clip(geometria);

  var pixelHa = ee.Image.pixelArea().divide(10000);
  var stack = pixelHa.updateMask(oficial7024).rename('oficial_ha')
    .addBands(
      pixelHa.updateMask(reconstruido7024).rename('reconstruido_ha')
    )
    .addBands(
      pixelHa.updateMask(diferencia).rename('xor_ha')
    );

  var resultado = stack.reduceRegion({
    reducer: ee.Reducer.sum(),
    geometry: geometria,
    scale: 30,
    maxPixels: 1e9,
    tileScale: 4
  });

  function seguro(clave) {
    return ee.Number(ee.Algorithms.If(
      resultado.contains(clave),
      resultado.get(clave),
      0
    ));
  }

  return ee.Feature(null, {
    id_control: caso.id,
    banda: banda,
    area_esperada_csv_ha: caso.esperado_ha,
    area_asset_transiciones_ha: seguro('oficial_ha'),
    area_reconstruida_bandas_ha: seguro('reconstruido_ha'),
    diferencia_espacial_xor_ha: seguro('xor_ha'),
    diferencia_asset_vs_csv_ha:
      seguro('oficial_ha').subtract(caso.esperado_ha),
    diferencia_bandas_vs_csv_ha:
      seguro('reconstruido_ha').subtract(caso.esperado_ha)
  });
}

var resultados = ee.FeatureCollection([
  auditar(casos[0]),
  auditar(casos[1])
]);

print('PASO 6F1-B — RESULTADO DIAGNÓSTICO', resultados);
print('No se ejecutaron exportaciones.');
