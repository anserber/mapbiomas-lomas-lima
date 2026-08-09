// PASO 6E3 — Auditoría del intercambio 70→68 en Ancón.
// Sigue los píxeles candidatos entre 1998 y 2004 y compara NDVI de mosaicos.
// No exporta archivos ni interpreta automáticamente pérdida o recuperación.

var ASSET_ACR =
  'projects/mapbiomas-lomas-jhoreck/assets/inputs/acr_lomas_5_ambitos_gee';
var ASSET_CLASES =
  'projects/mapbiomas-public/assets/peru/collection3/' +
  'mapbiomas_peru_collection3_integration_v1';
var ASSET_MOSAICOS =
  'projects/nexgenmap/MapBiomas2/LANDSAT/PANAMAZON/mosaics-2';

var acr = ee.FeatureCollection(ASSET_ACR);
var unidad = acr.filter(ee.Filter.eq('id_ambito', 'ancon'));
var geometria = unidad.geometry();
var contexto = geometria.buffer(1000);
var clases = ee.Image(ASSET_CLASES);
var mosaicos = ee.ImageCollection(ASSET_MOSAICOS);
var years = ee.List.sequence(1998, 2004);

var c2000 = clases.select('classification_2000');
var c2001 = clases.select('classification_2001');

// Candidato fijo: clase 70 en 2000 y clase 68 en 2001.
var candidato = c2000.eq(70)
  .and(c2001.eq(68))
  .clip(geometria);

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

function bandasArea(year) {
  year = ee.Number(year);
  var sufijo = year.format('%d');
  var clase = clasificacion(year);
  var pixelHa = ee.Image.pixelArea().divide(10000);

  var area70 = pixelHa
    .updateMask(candidato)
    .updateMask(clase.eq(70))
    .rename(ee.String('clase70_ha_').cat(sufijo));

  var area68 = pixelHa
    .updateMask(candidato)
    .updateMask(clase.eq(68))
    .rename(ee.String('clase68_ha_').cat(sufijo));

  var otra = pixelHa
    .updateMask(candidato)
    .updateMask(clase.neq(70).and(clase.neq(68)))
    .rename(ee.String('otra_clase_ha_').cat(sufijo));

  return area70.addBands(area68).addBands(otra);
}

var stackAreas = bandasArea(1998);
stackAreas = ee.Image(ee.List.sequence(1999, 2004).iterate(
  function(year, acumulado) {
    return ee.Image(acumulado).addBands(bandasArea(year));
  },
  stackAreas
));

var pixelHa30 = ee.Image.pixelArea().divide(10000);
var persiste68_2004 = candidato
  .and(clasificacion(2002).eq(68))
  .and(clasificacion(2003).eq(68))
  .and(clasificacion(2004).eq(68));
var retorna70 = candidato.and(
  clasificacion(2002).eq(70)
    .or(clasificacion(2003).eq(70))
    .or(clasificacion(2004).eq(70))
);

stackAreas = stackAreas
  .addBands(
    pixelHa30.updateMask(candidato).rename('candidato_70_68_ha')
  )
  .addBands(
    pixelHa30.updateMask(persiste68_2004)
      .rename('persiste_68_2001_2004_ha')
  )
  .addBands(
    pixelHa30.updateMask(retorna70)
      .rename('retorna_70_entre_2002_2004_ha')
  );

// Primera reducción: composición anual del candidato.
var areas = stackAreas.reduceRegion({
  reducer: ee.Reducer.sum(),
  geometry: geometria,
  scale: 30,
  maxPixels: 1e9,
  tileScale: 4
});

function bandaNdvi(year) {
  year = ee.Number(year);
  return mosaicoAnual(year)
    .select('ndvi_median')
    .updateMask(candidato)
    .rename(ee.String('ndvi_').cat(year.format('%d')));
}

var stackNdvi = bandaNdvi(1998);
stackNdvi = ee.Image(ee.List.sequence(1999, 2004).iterate(
  function(year, acumulado) {
    return ee.Image(acumulado).addBands(bandaNdvi(year));
  },
  stackNdvi
));

// Segunda y última reducción: señal espectral media del candidato.
var ndvi = stackNdvi.reduceRegion({
  reducer: ee.Reducer.mean(),
  geometry: geometria,
  scale: 30,
  maxPixels: 1e9,
  tileScale: 4
});

function obtener(diccionario, prefijo, year) {
  var clave = ee.String(prefijo).cat(ee.Number(year).format('%d'));
  return ee.Number(ee.Algorithms.If(
    diccionario.contains(clave),
    diccionario.get(clave),
    0
  ));
}

var area70Lista = years.map(function(year) {
  return obtener(areas, 'clase70_ha_', year);
});
var area68Lista = years.map(function(year) {
  return obtener(areas, 'clase68_ha_', year);
});
var otraClaseLista = years.map(function(year) {
  return obtener(areas, 'otra_clase_ha_', year);
});
var ndviLista = years.map(function(year) {
  return obtener(ndvi, 'ndvi_', year);
});
var nMosaicos = years.map(function(year) {
  return mosaicos
    .filter(ee.Filter.eq('year', year))
    .filterBounds(contexto)
    .size();
});

var areaCandidato = ee.Number(ee.Algorithms.If(
  areas.contains('candidato_70_68_ha'),
  areas.get('candidato_70_68_ha'),
  0
));
var areaPersiste68 = ee.Number(ee.Algorithms.If(
  areas.contains('persiste_68_2001_2004_ha'),
  areas.get('persiste_68_2001_2004_ha'),
  0
));
var areaRetorna70 = ee.Number(ee.Algorithms.If(
  areas.contains('retorna_70_entre_2002_2004_ha'),
  areas.get('retorna_70_entre_2002_2004_ha'),
  0
));

print('PASO 6E3 — RESULTADO ANCÓN 70→68', ee.Dictionary({
  unidad_objetos: unidad.size(),
  years: years,
  n_mosaicos: nMosaicos,
  candidato_70_68_2000_2001_ha: areaCandidato,
  clase70_por_year_ha: area70Lista,
  clase68_por_year_ha: area68Lista,
  otra_clase_por_year_ha: otraClaseLista,
  ndvi_median_medio_por_year: ndviLista,
  persiste_68_2001_2004_ha: areaPersiste68,
  persiste_68_2001_2004_pct:
    areaPersiste68.divide(areaCandidato).multiply(100),
  retorna_70_entre_2002_2004_ha: areaRetorna70,
  retorna_70_entre_2002_2004_pct:
    areaRetorna70.divide(areaCandidato).multiply(100)
}));

var mosaico2000 = mosaicoAnual(2000);
var mosaico2001 = mosaicoAnual(2001);
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
  mosaico2000, visNatural, 'Mosaico 2000 — color natural', true
);
mapaDerecho.addLayer(
  mosaico2001, visNatural, 'Mosaico 2001 — color natural', true
);
mapaIzquierdo.addLayer(
  mosaico2000, visNdvi, 'NDVI 2000', false
);
mapaDerecho.addLayer(
  mosaico2001, visNdvi, 'NDVI 2001', false
);
mapaIzquierdo.addLayer(
  bordeCandidato, {palette: ['FF00FF']}, 'Contorno 70→68', true
);
mapaDerecho.addLayer(
  bordeCandidato, {palette: ['FF00FF']}, 'Contorno 70→68', true
);

var limite = unidad.style({
  color: 'FFFFFF',
  fillColor: '00000000',
  width: 2
});
mapaIzquierdo.addLayer(limite, {}, 'Límite de Ancón', true);
mapaDerecho.addLayer(limite, {}, 'Límite de Ancón', true);

mapaIzquierdo.add(ui.Label('Ancón 2000 — clase 70', {
  position: 'top-left',
  fontWeight: 'bold',
  fontSize: '16px',
  padding: '6px'
}));
mapaDerecho.add(ui.Label('Ancón 2001 — clase 68', {
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
