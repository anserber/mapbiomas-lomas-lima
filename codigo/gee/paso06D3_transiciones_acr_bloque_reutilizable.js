// PASO 6D3 — Transiciones seleccionadas del ACR.
// Ejecutar un bloque por vez. Cambiar NUMERO_BLOQUE únicamente después de
// aprobar el bloque anterior.

var NUMERO_BLOQUE = 1; // Valores permitidos: 1, 2 o 3.

var ASSET_TRANSICIONES =
  'projects/mapbiomas-public/assets/peru/collection3/' +
  'mapbiomas_peru_collection3_transitions_v1';

var ASSET_ACR =
  'projects/mapbiomas-lomas-jhoreck/assets/inputs/' +
  'acr_lomas_5_ambitos_gee';

var transiciones = ee.Image(ASSET_TRANSICIONES);
var acr = ee.FeatureCollection(ASSET_ACR);
var areaHa = ee.Image.pixelArea().divide(10000).rename('area_ha');

var bandasSeleccionadas = [
  'transitions_1985_1986',
  'transitions_1986_1987',
  'transitions_2000_2001',
  'transitions_2005_2006',
  'transitions_2009_2010',
  'transitions_2011_2012',
  'transitions_2013_2014',
  'transitions_2014_2015',
  'transitions_2019_2020',
  'transitions_2021_2022',
  'transitions_2022_2023',
  'transitions_2023_2024',
  'transitions_1985_2024',
  'transitions_2000_2024',
  'transitions_2010_2024'
];

var clasesDocumentadas = ee.List([
  0, 3, 4, 5, 6, 7, 9, 11, 12, 13, 15, 18, 19, 21, 23, 24, 25, 29,
  30, 31, 32, 33, 34, 35, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69,
  70, 72
]);

if (NUMERO_BLOQUE < 1 || NUMERO_BLOQUE > 3) {
  throw new Error('NUMERO_BLOQUE debe ser 1, 2 o 3.');
}

var indiceInicial = (NUMERO_BLOQUE - 1) * 5;
var bandasBloqueCliente = bandasSeleccionadas.slice(
  indiceInicial,
  indiceInicial + 5
);
var bandasBloque = ee.List(bandasBloqueCliente);

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

  return ee.FeatureCollection(reduccion.iterate(function(
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
}

var tablaBloque = ee.FeatureCollection(
  bandasBloque.iterate(function(nombreBanda, acumulado) {
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

tablaBloque = tablaBloque.select(camposSalida);

var noDocumentadas = tablaBloque.filter(
  ee.Filter.or(
    ee.Filter.eq('from_documentada', false),
    ee.Filter.eq('to_documentada', false)
  )
);

var nombreBloque =
  'serie_transiciones_acr_bloque_' + NUMERO_BLOQUE + '_de_3';

print('PASO 6D3 — TRANSICIONES ACR — BLOQUE', NUMERO_BLOQUE);
print('Bandas del bloque — esperado: 5', bandasBloque);
print('Cantidad de bandas — esperado: 5',
  tablaBloque.aggregate_array('banda').distinct().size());
print('Ámbitos — esperado: 5',
  tablaBloque.aggregate_array('id_ambito').distinct().sort());
print('Cantidad de ámbitos — esperado: 5',
  tablaBloque.aggregate_array('id_ambito').distinct().size());
print('Filas del bloque', tablaBloque.size());
print('Filas con los 11 campos completos — debe igualar filas del bloque',
  tablaBloque.filter(ee.Filter.notNull(camposSalida)).size());
print('Clases no documentadas — esperado: 0', noDocumentadas.size());
print('Códigos de transición distintos',
  tablaBloque.aggregate_array('transition_code').distinct().sort());
print('Área total por banda — orden de las bandas del bloque',
  bandasBloque.map(function(banda) {
    return tablaBloque
      .filter(ee.Filter.eq('banda', banda))
      .aggregate_sum('area_ha');
  }));
print('Vista previa — primeras 20 filas', tablaBloque.limit(20));

Export.table.toDrive({
  collection: tablaBloque,
  description: nombreBloque,
  fileNamePrefix: nombreBloque,
  fileFormat: 'CSV',
  selectors: camposSalida
});

Map.centerObject(acr, 9);
Map.addLayer(
  transiciones.select(bandasBloqueCliente[0]).clip(acr.geometry()),
  {min: 0, max: 7070},
  bandasBloqueCliente[0]
);
Map.addLayer(
  acr.style({color: '00D5FF', fillColor: '00000000', width: 2}),
  {},
  'ACR — cinco ámbitos'
);

print('Revisa los controles antes de ejecutar la tarea de exportación.');
