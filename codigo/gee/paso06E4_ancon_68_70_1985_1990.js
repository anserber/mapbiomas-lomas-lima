// =====================================================================
// PASO 6E4 — Auditoria del ingreso 68->70 en Lomas de Ancon, 1985-1990.
// ---------------------------------------------------------------------
// Pregunta: el salto de +1223.460 ha netas en la clase 70 entre 1985 y
// 1986, registrado como rank 1 del ranking de saltos de Ancon, ¿es una
// ruptura cartografica de inicio de serie o un cambio territorial real?
//
// Replica metodologica de:
//   paso06E3_ancon_68_70_1998_2004.js               (ruptura 2000-2001)
//   paso06F2_control_cv042_carabayllo2_2014_2015.js (CV-042, 2014-2015)
//
// Criterios de decision, los mismos de los controles anteriores:
//   1. Sincronia  — ¿ingresa todo el candidato en el mismo year?
//   2. Retorno    — ¿persiste como clase 70 durante 1987-1990?
//   3. Espectral  — ¿hay contrapartida en NDVI y EVI2?
//   4. Insumo     — ¿el mosaico de 1985 es mas pobre que el de 1986?
//
// El criterio 4 no existia en 6E3 y es el decisivo para un quiebre de
// inicio de serie: mide nimages y cloud_cover de los mosaicos oficiales.
//
// No exporta archivos. No interpreta automaticamente perdida ni
// recuperacion. Solo imprime evidencia para decision humana.
// =====================================================================

// ---------------------------------------------------------------------
// 1. Assets y constantes
// ---------------------------------------------------------------------

var ASSET_ACR =
  'projects/mapbiomas-lomas-jhoreck/assets/inputs/acr_lomas_5_ambitos_gee';
var ASSET_CLASES =
  'projects/mapbiomas-public/assets/peru/collection3/' +
  'mapbiomas_peru_collection3_integration_v1';
var ASSET_MOSAICOS =
  'projects/nexgenmap/MapBiomas2/LANDSAT/PANAMAZON/mosaics-2';

var YEAR_A = 1985;   // year previo al salto
var YEAR_B = 1986;   // year del salto
var YEAR_FIN = 1990; // fin del seguimiento de persistencia

// Valores de control del Paso 6, resumen_transiciones_acr_paso06.csv,
// banda transitions_1985_1986, unidad ancon:
var CONTROL_ENTRADA_PASO06_HA = 1242.400;  // entrada_clase_loma_ha
var CONTROL_SALIDA_PASO06_HA = 18.941;     // salida_clase_loma_ha
var CONTROL_NETO_PASO06_HA = 1223.460;     // balance_neto_clase_loma_ha

// Valores de control de serie_indicadores_acr_1985_2024.csv, ancon:
var CONTROL_LOMA_1985_HA = 3087.925;
var CONTROL_LOMA_1986_HA = 4311.385;

var acr = ee.FeatureCollection(ASSET_ACR);
var unidad = acr.filter(ee.Filter.eq('id_ambito', 'ancon'));
var geometria = unidad.geometry();
var contexto = geometria.buffer(1000);
var clases = ee.Image(ASSET_CLASES);
var mosaicos = ee.ImageCollection(ASSET_MOSAICOS);
var years = ee.List.sequence(YEAR_A, YEAR_FIN);
var pixelHa = ee.Image.pixelArea().divide(10000);

function clasificacion(year) {
  return clases.select(
    ee.String('classification_').cat(ee.Number(year).format('%d'))
  );
}

function mosaicoAnual(year) {
  return mosaicos
    .filter(ee.Filter.eq('year', year))
    .filterBounds(contexto)
    .mosaic()
    .clip(contexto);
}

// ---------------------------------------------------------------------
// 2. Candidato: pixeles que NO eran clase 70 en 1985 y SI lo son en 1986
// ---------------------------------------------------------------------

var c1985 = clasificacion(YEAR_A);
var c1986 = clasificacion(YEAR_B);

var candidato = c1985.neq(70)
  .and(c1986.eq(70))
  .clip(geometria);

// Direccion inversa, para conciliar el balance neto del Paso 6.
var candidatoSalida = c1985.eq(70)
  .and(c1986.neq(70))
  .clip(geometria);

// ---------------------------------------------------------------------
// 3. Composicion de origen: ¿de que clase venia el candidato en 1985?
// ---------------------------------------------------------------------

var CLASES_ORIGEN = [
  {codigo: 68, nombre: 'otra_area_natural_sin_vegetacion'},
  {codigo: 13, nombre: 'otra_formacion_no_boscosa'},
  {codigo: 66, nombre: 'matorral'},
  {codigo: 12, nombre: 'pastizal_herbazal'},
  {codigo: 29, nombre: 'afloramiento_rocoso'},
  {codigo: 25, nombre: 'otra_area_sin_vegetacion'},
  {codigo: 24, nombre: 'infraestructura_urbana'}
];

var stackOrigen = pixelHa
  .updateMask(candidato)
  .rename('candidato_68_70_total_ha');

var codigosConocidos = ee.List(CLASES_ORIGEN.map(function(item) {
  return item.codigo;
}));

CLASES_ORIGEN.forEach(function(item) {
  stackOrigen = stackOrigen.addBands(
    pixelHa
      .updateMask(candidato)
      .updateMask(c1985.eq(item.codigo))
      .rename('origen_' + item.codigo + '_' + item.nombre + '_ha')
  );
});

stackOrigen = stackOrigen
  .addBands(
    pixelHa
      .updateMask(candidato)
      .updateMask(c1985.remap(codigosConocidos,
        ee.List.repeat(1, codigosConocidos.size()), 0).eq(0))
      .rename('origen_otras_clases_ha')
  )
  .addBands(
    pixelHa.updateMask(candidatoSalida).rename('salida_70_1985_1986_ha')
  )
  .addBands(
    pixelHa.updateMask(c1985.eq(70)).rename('clase70_total_1985_ha')
  )
  .addBands(
    pixelHa.updateMask(c1986.eq(70)).rename('clase70_total_1986_ha')
  );

// ---------------------------------------------------------------------
// 4. Seguimiento anual del candidato, 1985-1990
// ---------------------------------------------------------------------

function bandasArea(year) {
  year = ee.Number(year);
  var sufijo = year.format('%d');
  var clase = clasificacion(year);

  var area70 = pixelHa
    .updateMask(candidato)
    .updateMask(clase.eq(70))
    .rename(ee.String('clase70_ha_').cat(sufijo));

  var area68 = pixelHa
    .updateMask(candidato)
    .updateMask(clase.eq(68))
    .rename(ee.String('clase68_ha_').cat(sufijo));

  var area13 = pixelHa
    .updateMask(candidato)
    .updateMask(clase.eq(13))
    .rename(ee.String('clase13_ha_').cat(sufijo));

  var otra = pixelHa
    .updateMask(candidato)
    .updateMask(clase.neq(70).and(clase.neq(68)).and(clase.neq(13)))
    .rename(ee.String('otra_clase_ha_').cat(sufijo));

  return area70.addBands(area68).addBands(area13).addBands(otra);
}

var stackAreas = bandasArea(YEAR_A);
stackAreas = ee.Image(ee.List.sequence(YEAR_A + 1, YEAR_FIN).iterate(
  function(year, acumulado) {
    return ee.Image(acumulado).addBands(bandasArea(year));
  },
  stackAreas
));

// ---------------------------------------------------------------------
// 5. Persistencia y retorno, criterios 1 y 2
// ---------------------------------------------------------------------

var persiste70_1990 = candidato
  .and(clasificacion(1987).eq(70))
  .and(clasificacion(1988).eq(70))
  .and(clasificacion(1989).eq(70))
  .and(clasificacion(1990).eq(70));

var revierte = candidato.and(
  clasificacion(1987).neq(70)
    .or(clasificacion(1988).neq(70))
    .or(clasificacion(1989).neq(70))
    .or(clasificacion(1990).neq(70))
);

// Persistencia larga: sigue siendo clase 70 en 2024.
var persiste70_2024 = candidato.and(clasificacion(2024).eq(70));

stackAreas = stackAreas
  .addBands(pixelHa.updateMask(persiste70_1990)
    .rename('persiste_70_1987_1990_ha'))
  .addBands(pixelHa.updateMask(revierte)
    .rename('revierte_antes_de_1990_ha'))
  .addBands(pixelHa.updateMask(persiste70_2024)
    .rename('persiste_70_hasta_2024_ha'));

// Primera reduccion: areas.
var areas = stackAreas.addBands(stackOrigen).reduceRegion({
  reducer: ee.Reducer.sum(),
  geometry: geometria,
  scale: 30,
  maxPixels: 1e9,
  tileScale: 4
});

// ---------------------------------------------------------------------
// 6. Señal espectral del candidato, criterio 3
// ---------------------------------------------------------------------

function bandasEspectrales(year) {
  year = ee.Number(year);
  var sufijo = year.format('%d');
  var mosaico = mosaicoAnual(year).updateMask(candidato);
  return mosaico.select('ndvi_median')
    .rename(ee.String('ndvi_').cat(sufijo))
    .addBands(
      mosaico.select('evi2_median')
        .rename(ee.String('evi2_').cat(sufijo))
    );
}

var stackEspectral = bandasEspectrales(YEAR_A);
stackEspectral = ee.Image(ee.List.sequence(YEAR_A + 1, YEAR_FIN).iterate(
  function(year, acumulado) {
    return ee.Image(acumulado).addBands(bandasEspectrales(year));
  },
  stackEspectral
));

// Segunda reduccion: señal espectral media.
var espectral = stackEspectral.reduceRegion({
  reducer: ee.Reducer.mean(),
  geometry: geometria,
  scale: 30,
  maxPixels: 1e9,
  tileScale: 4
});

// ---------------------------------------------------------------------
// 7. Auditoria del insumo Landsat, criterio 4 — bloque decisivo
// ---------------------------------------------------------------------

function auditarInsumo(year) {
  var subset = mosaicos
    .filter(ee.Filter.eq('year', year))
    .filterBounds(contexto);
  return ee.Dictionary({
    year: year,
    n_teselas: subset.size(),
    versiones: subset.aggregate_array('version').distinct().sort(),
    satelites: subset.aggregate_array('satellite').distinct().sort(),
    regiones: subset.aggregate_array('region_code').distinct().sort(),
    nimages_por_tesela: subset.aggregate_array('nimages').sort(),
    nimages_total: subset.aggregate_array('nimages')
      .reduce(ee.Reducer.sum()),
    cloud_cover_por_tesela: subset.aggregate_array('cloud_cover').sort(),
    cloud_cover_medio: subset.aggregate_array('cloud_cover')
      .reduce(ee.Reducer.mean())
  });
}

var insumoPorYear = years.map(auditarInsumo);

// ---------------------------------------------------------------------
// 8. Lectura de resultados
// ---------------------------------------------------------------------

function obtener(diccionario, clave) {
  return ee.Number(ee.Algorithms.If(
    diccionario.contains(clave),
    diccionario.get(clave),
    0
  ));
}

function obtenerSerie(diccionario, prefijo) {
  return years.map(function(year) {
    var clave = ee.String(prefijo).cat(ee.Number(year).format('%d'));
    return obtener(diccionario, clave);
  });
}

var areaCandidato = obtener(areas, 'candidato_68_70_total_ha');
var areaSalida = obtener(areas, 'salida_70_1985_1986_ha');
var areaPersiste1990 = obtener(areas, 'persiste_70_1987_1990_ha');
var areaRevierte = obtener(areas, 'revierte_antes_de_1990_ha');
var areaPersiste2024 = obtener(areas, 'persiste_70_hasta_2024_ha');
var loma1985 = obtener(areas, 'clase70_total_1985_ha');
var loma1986 = obtener(areas, 'clase70_total_1986_ha');

var origenLista = CLASES_ORIGEN.map(function(item) {
  var clave = 'origen_' + item.codigo + '_' + item.nombre + '_ha';
  return ee.Dictionary({
    clase: item.codigo,
    nombre: item.nombre,
    ha: obtener(areas, clave),
    pct_del_candidato: obtener(areas, clave)
      .divide(areaCandidato).multiply(100)
  });
});

print('===== PASO 6E4 — ANCON 68->70, 1985-1990 =====');

print('A. CONTROL CONTRA EL PASO 6', ee.Dictionary({
  unidad_objetos: unidad.size(),
  entrada_68_70_calculada_ha: areaCandidato,
  entrada_68_70_esperada_paso06_ha: CONTROL_ENTRADA_PASO06_HA,
  entrada_diferencia_ha: areaCandidato
    .subtract(CONTROL_ENTRADA_PASO06_HA),
  salida_70_calculada_ha: areaSalida,
  salida_70_esperada_paso06_ha: CONTROL_SALIDA_PASO06_HA,
  neto_calculado_ha: areaCandidato.subtract(areaSalida),
  neto_esperado_paso06_ha: CONTROL_NETO_PASO06_HA,
  clase70_total_1985_calculada_ha: loma1985,
  clase70_total_1985_esperada_ha: CONTROL_LOMA_1985_HA,
  clase70_total_1986_calculada_ha: loma1986,
  clase70_total_1986_esperada_ha: CONTROL_LOMA_1986_HA
}));

print('B. ORIGEN DEL CANDIDATO EN 1985', ee.Dictionary({
  desglose: origenLista,
  otras_clases_ha: obtener(areas, 'origen_otras_clases_ha')
}));

print('C. CRITERIO 1 y 2 — SINCRONIA Y RETORNO', ee.Dictionary({
  years: years,
  clase70_por_year_ha: obtenerSerie(areas, 'clase70_ha_'),
  clase68_por_year_ha: obtenerSerie(areas, 'clase68_ha_'),
  clase13_por_year_ha: obtenerSerie(areas, 'clase13_ha_'),
  otra_clase_por_year_ha: obtenerSerie(areas, 'otra_clase_ha_'),
  persiste_70_1987_1990_ha: areaPersiste1990,
  persiste_70_1987_1990_pct: areaPersiste1990
    .divide(areaCandidato).multiply(100),
  revierte_antes_de_1990_ha: areaRevierte,
  revierte_antes_de_1990_pct: areaRevierte
    .divide(areaCandidato).multiply(100),
  persiste_70_hasta_2024_ha: areaPersiste2024,
  persiste_70_hasta_2024_pct: areaPersiste2024
    .divide(areaCandidato).multiply(100)
}));

print('D. CRITERIO 3 — SEÑAL ESPECTRAL DEL CANDIDATO', ee.Dictionary({
  years: years,
  ndvi_median_medio: obtenerSerie(espectral, 'ndvi_'),
  evi2_median_medio: obtenerSerie(espectral, 'evi2_'),
  nota: 'Escala nativa del mosaico. Comparacion relativa entre years.'
}));

print('E. CRITERIO 4 — AUDITORIA DEL INSUMO LANDSAT', insumoPorYear);

print('F. LECTURA', ee.Dictionary({
  regla_1: 'Si el candidato ingresa completo en 1986 y persiste >95% ' +
    'hasta 1990 sin contrapartida espectral, es ruptura cartografica.',
  regla_2: 'Si nimages_total de 1985 es sustancialmente menor que el ' +
    'de 1986, la causa probable es pobreza del mosaico de inicio de serie.',
  regla_3: 'Si NDVI y EVI2 suben de forma proporcional al area, ' +
    'la hipotesis de cambio real no puede descartarse.',
  regla_4: 'Ninguna de estas salidas autoriza por si sola a declarar ' +
    'recuperacion ecologica de loma.'
}));

// ---------------------------------------------------------------------
// 9. Control visual comparado, 1985 vs 1986
// ---------------------------------------------------------------------

var mosaico1985 = mosaicoAnual(YEAR_A);
var mosaico1986 = mosaicoAnual(YEAR_B);

var visNatural = {
  bands: ['red_median', 'green_median', 'blue_median'],
  min: 200,
  max: 2200,
  gamma: 1.15
};
var visNdvi = {
  bands: ['ndvi_median'],
  min: 0,
  max: 200,
  palette: ['6E3B19', 'E5C07B', 'A6D96A', '1A9641']
};

var candidato30 = candidato.unmask(0).reproject({
  crs: 'EPSG:32718',
  scale: 30
});
var bordeCandidato = candidato30
  .focalMax({radius: 1, units: 'pixels'})
  .neq(candidato30.focalMin({radius: 1, units: 'pixels'}))
  .selfMask();

var mapaIzquierdo = ui.Map();
var mapaDerecho = ui.Map();
mapaIzquierdo.setOptions('SATELLITE');
mapaDerecho.setOptions('SATELLITE');

mapaIzquierdo.addLayer(
  mosaico1985, visNatural, 'Mosaico 1985 — color natural', true
);
mapaDerecho.addLayer(
  mosaico1986, visNatural, 'Mosaico 1986 — color natural', true
);
mapaIzquierdo.addLayer(mosaico1985, visNdvi, 'NDVI 1985', false);
mapaDerecho.addLayer(mosaico1986, visNdvi, 'NDVI 1986', false);
mapaIzquierdo.addLayer(
  clasificacion(YEAR_A).eq(70).selfMask().clip(geometria),
  {palette: ['00FF00']}, 'Clase 70 en 1985', false
);
mapaDerecho.addLayer(
  clasificacion(YEAR_B).eq(70).selfMask().clip(geometria),
  {palette: ['00FF00']}, 'Clase 70 en 1986', false
);
mapaIzquierdo.addLayer(
  bordeCandidato, {palette: ['FF00FF']}, 'Contorno 68->70', true
);
mapaDerecho.addLayer(
  bordeCandidato, {palette: ['FF00FF']}, 'Contorno 68->70', true
);

var limite = unidad.style({
  color: 'FFFFFF',
  fillColor: '00000000',
  width: 2
});
mapaIzquierdo.addLayer(limite, {}, 'Limite de Ancon', true);
mapaDerecho.addLayer(limite, {}, 'Limite de Ancon', true);

mapaIzquierdo.add(ui.Label('Ancon 1985 — antes del salto', {
  position: 'top-left',
  fontWeight: 'bold',
  fontSize: '16px',
  padding: '6px'
}));
mapaDerecho.add(ui.Label('Ancon 1986 — despues del salto', {
  position: 'top-right',
  fontWeight: 'bold',
  fontSize: '16px',
  padding: '6px'
}));

var linker = ui.Map.Linker([mapaIzquierdo, mapaDerecho]);
var divisor = ui.SplitPanel({
  firstPanel: mapaIzquierdo,
  secondPanel: mapaDerecho,
  orientation: 'horizontal',
  wipe: true,
  style: {stretch: 'both'}
});

ui.root.widgets().reset([divisor]);
mapaIzquierdo.centerObject(unidad, 11);

print('No se ejecutaron exportaciones.');
