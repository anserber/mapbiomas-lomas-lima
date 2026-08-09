// PASO 6D4-R — Transiciones de la periferia externa corregida.
// Mantiene separados los 15 anillos por ámbito, los 3 anillos del sistema
// y excluye el enclave interno de SEDAPAL de Carabayllo 2.
// Ejecutar un bloque por vez.

var NUMERO_BLOQUE = 1; // Valores permitidos: 1, 2 o 3.

var ASSET_TRANSICIONES =
  'projects/mapbiomas-public/assets/peru/collection3/' +
  'mapbiomas_peru_collection3_transitions_v1';
var ASSET_AMBITOS =
  'projects/mapbiomas-lomas-jhoreck/assets/inputs/' +
  'anillos_por_ambito_periferia_externa_gee';
var ASSET_SISTEMA =
  'projects/mapbiomas-lomas-jhoreck/assets/inputs/' +
  'anillos_sistema_periferia_externa_gee';
var ASSET_ENCLAVE =
  'projects/mapbiomas-lomas-jhoreck/assets/inputs/' +
  'enclave_sedapal_carabayllo2_gee';

var transiciones = ee.Image(ASSET_TRANSICIONES);
var anillosAmbitosRaw = ee.FeatureCollection(ASSET_AMBITOS);
var anillosSistemaRaw = ee.FeatureCollection(ASSET_SISTEMA);
var enclave = ee.FeatureCollection(ASSET_ENCLAVE);
var areaHa = ee.Image.pixelArea().divide(10000).rename('area_ha');

var anillosAmbitos = anillosAmbitosRaw.map(function(feature) {
  var id = ee.String(feature.get('id_ambito'));
  var zona = ee.String(feature.get('zona'));
  return feature.set({
    nivel: 'ambito',
    unidad_id: id.cat('|').cat(zona),
    dist_min_m: feature.get('dmin_m'),
    dist_max_m: feature.get('dmax_m')
  });
});

var anillosSistema = anillosSistemaRaw.map(function(feature) {
  var zona = ee.String(feature.get('zona'));
  return feature.set({
    nivel: 'sistema',
    unidad_id: ee.String('sistema|').cat(zona),
    id_ambito: 'sistema',
    nombre: 'Sistema disuelto',
    dist_min_m: feature.get('dmin_m'),
    dist_max_m: feature.get('dmax_m')
  });
});

var unidades = anillosAmbitos.merge(anillosSistema);

// El enclave debe mantenerse completamente fuera de ambas familias de anillos.
var interseccionEnclaveAmbitos = anillosAmbitos
  .geometry()
  .intersection(enclave.geometry(), 1)
  .area(1)
  .divide(10000);
var interseccionEnclaveSistema = anillosSistema
  .geometry()
  .intersection(enclave.geometry(), 1)
  .area(1)
  .divide(10000);

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
    collection: unidades,
    reducer: ee.Reducer.sum().group({
      groupField: 1,
      groupName: 'transition_code'
    }),
    scale: 30,
    tileScale: 4
  });

  return ee.FeatureCollection(reduccion.iterate(function(
    unidad,
    acumulado
  ) {
    unidad = ee.Feature(unidad);
    var grupos = ee.List(unidad.get('groups'));
    var filas = ee.FeatureCollection(grupos.map(function(elemento) {
      elemento = ee.Dictionary(elemento);
      var transicion = ee.Number(elemento.get('transition_code')).toInt();
      var origen = transicion.divide(100).floor().toInt();
      var destino = transicion.mod(100).toInt();

      return ee.Feature(null, {
        nivel: unidad.get('nivel'),
        unidad_id: unidad.get('unidad_id'),
        id_ambito: unidad.get('id_ambito'),
        nombre: unidad.get('nombre'),
        zona: unidad.get('zona'),
        dist_min_m: unidad.get('dist_min_m'),
        dist_max_m: unidad.get('dist_max_m'),
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
  'nivel',
  'unidad_id',
  'id_ambito',
  'nombre',
  'zona',
  'dist_min_m',
  'dist_max_m',
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

var tablaAmbitos = tablaBloque.filter(ee.Filter.eq('nivel', 'ambito'));
var tablaSistema = tablaBloque.filter(ee.Filter.eq('nivel', 'sistema'));
var noDocumentadas = tablaBloque.filter(
  ee.Filter.or(
    ee.Filter.eq('from_documentada', false),
    ee.Filter.eq('to_documentada', false)
  )
);

// Control independiente del área de la grilla a 30 m. La diferencia frente
// al área de transiciones cuantifica píxeles enmascarados por el asset.
var coberturaGrilla = areaHa.rename('area_grilla_ha').reduceRegions({
  collection: unidades,
  reducer: ee.Reducer.sum(),
  scale: 30,
  tileScale: 4
});
var areaGrillaAmbitos = ee.Number(
  coberturaGrilla
    .filter(ee.Filter.eq('nivel', 'ambito'))
    .aggregate_sum('sum')
);
var areaGrillaSistema = ee.Number(
  coberturaGrilla
    .filter(ee.Filter.eq('nivel', 'sistema'))
    .aggregate_sum('sum')
);

var controlCoberturaAmbitos = ee.FeatureCollection(
  bandasBloque.map(function(banda) {
    var cubierta = ee.Number(
      tablaAmbitos
        .filter(ee.Filter.eq('banda', banda))
        .aggregate_sum('area_ha')
    );
    var faltante = areaGrillaAmbitos.subtract(cubierta);
    return ee.Feature(null, {
      banda: banda,
      nivel: 'ambito',
      area_grilla_ha: areaGrillaAmbitos,
      area_transiciones_ha: cubierta,
      area_enmascarada_ha: faltante,
      area_enmascarada_pct:
        faltante.divide(areaGrillaAmbitos).multiply(100)
    });
  })
);

var controlCoberturaSistema = ee.FeatureCollection(
  bandasBloque.map(function(banda) {
    var cubierta = ee.Number(
      tablaSistema
        .filter(ee.Filter.eq('banda', banda))
        .aggregate_sum('area_ha')
    );
    var faltante = areaGrillaSistema.subtract(cubierta);
    return ee.Feature(null, {
      banda: banda,
      nivel: 'sistema',
      area_grilla_ha: areaGrillaSistema,
      area_transiciones_ha: cubierta,
      area_enmascarada_ha: faltante,
      area_enmascarada_pct:
        faltante.divide(areaGrillaSistema).multiply(100)
    });
  })
);

var nombreBloque =
  'serie_transiciones_anillos_periferia_externa_bloque_' +
  NUMERO_BLOQUE + '_de_3';

print('PASO 6D4-R — TRANSICIONES DE ANILLOS CORREGIDOS — BLOQUE',
  NUMERO_BLOQUE);
print('Asset — anillos por ámbito', ASSET_AMBITOS);
print('Asset — anillos del sistema', ASSET_SISTEMA);
print('Asset — enclave excluido', ASSET_ENCLAVE);
print('Intersección anillos por ámbito × enclave — esperado: 0 ha',
  interseccionEnclaveAmbitos);
print('Intersección anillos del sistema × enclave — esperado: 0 ha',
  interseccionEnclaveSistema);
print('Bandas del bloque — esperado: 5', bandasBloque);
print('Cantidad de bandas — esperado: 5',
  tablaBloque.aggregate_array('banda').distinct().size());
print('Unidades espaciales — esperado: 18',
  tablaBloque.aggregate_array('unidad_id').distinct().size());
print('Unidades por ámbito — esperado: 15',
  tablaAmbitos.aggregate_array('unidad_id').distinct().size());
print('Unidades del sistema — esperado: 3',
  tablaSistema.aggregate_array('unidad_id').distinct().size());
print('Zonas — esperado: 3',
  tablaBloque.aggregate_array('zona').distinct().sort());
print('Filas del bloque', tablaBloque.size());
print('Filas por ámbito', tablaAmbitos.size());
print('Filas del sistema', tablaSistema.size());
print('Filas con los 16 campos completos — debe igualar filas del bloque',
  tablaBloque.filter(ee.Filter.notNull(camposSalida)).size());
print('Clases no documentadas — esperado: 0', noDocumentadas.size());
print('Unidades por banda — esperado: [18, 18, 18, 18, 18]',
  bandasBloque.map(function(banda) {
    return tablaBloque
      .filter(ee.Filter.eq('banda', banda))
      .aggregate_count_distinct('unidad_id');
  }));
print('Área total por banda — 15 anillos por ámbito',
  bandasBloque.map(function(banda) {
    return tablaAmbitos
      .filter(ee.Filter.eq('banda', banda))
      .aggregate_sum('area_ha');
  }));
print('Área total por banda — 3 anillos del sistema',
  bandasBloque.map(function(banda) {
    return tablaSistema
      .filter(ee.Filter.eq('banda', banda))
      .aggregate_sum('area_ha');
  }));
print('Área total de la grilla — 15 anillos por ámbito',
  areaGrillaAmbitos);
print('Área total de la grilla — 3 anillos del sistema',
  areaGrillaSistema);
print('Control de cobertura — ámbito', controlCoberturaAmbitos);
print('Área enmascarada por banda — ámbito, ha',
  controlCoberturaAmbitos.aggregate_array('area_enmascarada_ha'));
print('Área enmascarada por banda — ámbito, %',
  controlCoberturaAmbitos.aggregate_array('area_enmascarada_pct'));
print('Control de cobertura — sistema', controlCoberturaSistema);
print('Área enmascarada por banda — sistema, ha',
  controlCoberturaSistema.aggregate_array('area_enmascarada_ha'));
print('Área enmascarada por banda — sistema, %',
  controlCoberturaSistema.aggregate_array('area_enmascarada_pct'));
print('Vista previa — anillos por ámbito', tablaAmbitos.limit(10));
print('Vista previa — sistema disuelto', tablaSistema.limit(10));

Export.table.toDrive({
  collection: tablaBloque,
  description: nombreBloque,
  folder: 'MAPBIOMAS_LOMAS',
  fileNamePrefix: nombreBloque,
  fileFormat: 'CSV',
  selectors: camposSalida
});

Map.centerObject(unidades, 9);
Map.addLayer(
  transiciones.select(bandasBloqueCliente[0]).clip(unidades.geometry()),
  {min: 0, max: 7070},
  bandasBloqueCliente[0]
);
Map.addLayer(
  anillosAmbitos.style({color: '00BFFF', fillColor: '00000000', width: 2}),
  {},
  '15 anillos por ámbito'
);
Map.addLayer(
  anillosSistema.style({color: 'FF8C00', fillColor: '00000000', width: 3}),
  {},
  '3 anillos del sistema'
);
Map.addLayer(
  enclave.style({color: 'FF00FF', fillColor: 'FF00FF55', width: 2}),
  {},
  'Enclave SEDAPAL excluido'
);

print('Revisa los controles antes de ejecutar la tarea de exportación.');
