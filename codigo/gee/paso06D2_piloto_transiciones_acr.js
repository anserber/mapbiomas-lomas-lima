// PASO 6D2 — Piloto de composición de transiciones para el ACR.
// Procesa tres bandas de control y no exporta datos.

var ASSET_TRANSICIONES =
  'projects/mapbiomas-public/assets/peru/collection3/' +
  'mapbiomas_peru_collection3_transitions_v1';

var ASSET_ACR =
  'projects/mapbiomas-lomas-jhoreck/assets/inputs/' +
  'acr_lomas_5_ambitos_gee';

var transiciones = ee.Image(ASSET_TRANSICIONES);
var acr = ee.FeatureCollection(ASSET_ACR);
var areaHa = ee.Image.pixelArea().divide(10000).rename('area_ha');

var bandasPiloto = ee.List([
  'transitions_1985_1986',
  'transitions_2023_2024',
  'transitions_1985_2024'
]);

var clasesDocumentadas = ee.List([
  0, 3, 4, 5, 6, 7, 9, 11, 12, 13, 15, 18, 19, 21, 23, 24, 25, 29,
  30, 31, 32, 33, 34, 35, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69,
  70, 72
]);

function resumirBanda(nombreBanda) {
  nombreBanda = ee.String(nombreBanda);
  var partes = nombreBanda.split('_');
  var inicio = ee.Number.parse(ee.String(partes.get(1)));
  var fin = ee.Number.parse(ee.String(partes.get(2)));
  var codigo = transiciones.select([nombreBanda]).rename('transition_code');

  var reduccion = areaHa.addBands(codigo).reduceRegions({
    collection: acr,
    reducer: ee.Reducer.sum().group({
      groupField: 1,
      groupName: 'transition_code'
    }),
    scale: 30,
    tileScale: 4
  });

  var filasPorAmbito = ee.FeatureCollection(reduccion.iterate(function(
    ambito,
    acumulado
  ) {
    ambito = ee.Feature(ambito);
    var grupos = ee.List(ambito.get('groups'));
    var filas = ee.FeatureCollection(grupos.map(function(elemento) {
      elemento = ee.Dictionary(elemento);
      var transicion = ee.Number(elemento.get('transition_code')).toInt();
      var origen = transicion.divide(100).floor().toInt();
      var destino = transicion.mod(100).toInt();

      return ee.Feature(null, {
        id_ambito: ambito.get('id_ambito'),
        nombre: ambito.get('NOMBRE'),
        banda: nombreBanda,
        year_start: inicio,
        year_end: fin,
        transition_code: transicion,
        from_class: origen,
        to_class: destino,
        from_documentada: clasesDocumentadas.contains(origen),
        to_documentada: clasesDocumentadas.contains(destino),
        area_ha: ee.Number(elemento.get('sum'))
      });
    }));
    return ee.FeatureCollection(acumulado).merge(filas);
  }, ee.FeatureCollection([])));

  return filasPorAmbito;
}

var tablaPiloto = ee.FeatureCollection(
  bandasPiloto.iterate(function(nombreBanda, acumulado) {
    return ee.FeatureCollection(acumulado).merge(
      resumirBanda(ee.String(nombreBanda))
    );
  }, ee.FeatureCollection([]))
);

var camposSalida = [
  'id_ambito',
  'nombre',
  'banda',
  'year_start',
  'year_end',
  'transition_code',
  'from_class',
  'to_class',
  'from_documentada',
  'to_documentada',
  'area_ha'
];

tablaPiloto = tablaPiloto.select(camposSalida);

var noDocumentadas = tablaPiloto.filter(
  ee.Filter.or(
    ee.Filter.eq('from_documentada', false),
    ee.Filter.eq('to_documentada', false)
  )
);

print('PASO 6D2 — PILOTO DE TRANSICIONES ACR');
print('Bandas piloto — esperado: 3', bandasPiloto);
print('Ámbitos — esperado: 5', tablaPiloto.aggregate_array('id_ambito').distinct().sort());
print('Cantidad de ámbitos — esperado: 5', tablaPiloto.aggregate_array('id_ambito').distinct().size());
print('Cantidad de bandas — esperado: 3', tablaPiloto.aggregate_array('banda').distinct().size());
print('Filas del piloto', tablaPiloto.size());
print('Campos esperados — 11', camposSalida);
print(
  'Campos del primer registro',
  ee.Feature(tablaPiloto.first()).propertyNames().sort()
);
print(
  'Filas con los 11 campos completos — debe igualar filas del piloto',
  tablaPiloto.filter(ee.Filter.notNull(camposSalida)).size()
);
print('Primer registro completo', tablaPiloto.first());
print(
  'Códigos de transición presentes',
  tablaPiloto.aggregate_array('transition_code').distinct().sort()
);
print('Clases no documentadas — esperado: 0', noDocumentadas.size());
print('Vista previa — primeras 20 filas', tablaPiloto.limit(20));
print(
  'Área total por banda — orden de bandas piloto',
  bandasPiloto.map(function(banda) {
    return tablaPiloto.filter(ee.Filter.eq('banda', banda)).aggregate_sum('area_ha');
  })
);

Map.centerObject(acr, 9);
Map.addLayer(
  transiciones.select('transitions_2023_2024').clip(acr.geometry()),
  {min: 0, max: 7070},
  'Transiciones 2023–2024 — piloto'
);
Map.addLayer(
  acr.style({color: '00D5FF', fillColor: '00000000', width: 2}),
  {},
  'ACR — cinco ámbitos'
);

print('PASO 6D2 FINALIZADO — no se ejecutaron exportaciones');
