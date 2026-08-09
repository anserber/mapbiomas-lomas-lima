// PASO 6F2 — Control específico de CV-042 en Lomas de Carabayllo 2.
// Audita los píxeles 70→13 y 70→68 de 2014–2015.
// Evalúa trayectoria 2012–2024, retorno a clase 70 y señal NDVI 2012–2018.
// No exporta archivos ni concluye automáticamente degradación ecológica.

var ASSET_ACR =
  'projects/mapbiomas-lomas-jhoreck/assets/inputs/acr_lomas_5_ambitos_gee';
var ASSET_CLASES =
  'projects/mapbiomas-public/assets/peru/collection3/' +
  'mapbiomas_peru_collection3_integration_v1';
var ASSET_MOSAICOS =
  'projects/nexgenmap/MapBiomas2/LANDSAT/PANAMAZON/mosaics-2';

var acr = ee.FeatureCollection(ASSET_ACR);
var unidad = acr.filter(ee.Filter.eq('id_ambito', 'carabayllo_2'));
var geometria = unidad.geometry();
var contexto = geometria.buffer(1000);
var clases = ee.Image(ASSET_CLASES);
var mosaicos = ee.ImageCollection(ASSET_MOSAICOS);

var yearsClases = ee.List.sequence(2012, 2024);
var yearsNdvi = ee.List.sequence(2012, 2018);

function clasificacion(year) {
  return clases.select(
    ee.String('classification_').cat(ee.Number(year).format('%d'))
  );
}

var c2014 = clasificacion(2014);
var c2015 = clasificacion(2015);

// Componentes exactos de CV-042.
var candidato70a13 = c2014.eq(70).and(c2015.eq(13)).clip(geometria);
var candidato70a68 = c2014.eq(70).and(c2015.eq(68)).clip(geometria);
var candidato = candidato70a13.or(candidato70a68).clip(geometria);

function bandaAreas(year) {
  year = ee.Number(year);
  var sufijo = year.format('%d');
  var clase = clasificacion(year);
  var pixelHa = ee.Image.pixelArea().divide(10000).updateMask(candidato);

  return pixelHa.updateMask(clase.eq(70))
    .rename(ee.String('clase70_ha_').cat(sufijo))
    .addBands(
      pixelHa.updateMask(clase.eq(13))
        .rename(ee.String('clase13_ha_').cat(sufijo))
    )
    .addBands(
      pixelHa.updateMask(clase.eq(68))
        .rename(ee.String('clase68_ha_').cat(sufijo))
    )
    .addBands(
      pixelHa.updateMask(
        clase.neq(70).and(clase.neq(13)).and(clase.neq(68))
      ).rename(ee.String('otra_clase_ha_').cat(sufijo))
    );
}

var stackAreas = bandaAreas(2012);
stackAreas = ee.Image(ee.List.sequence(2013, 2024).iterate(
  function(year, acumulado) {
    return ee.Image(acumulado).addBands(bandaAreas(year));
  },
  stackAreas
));

function algunRetorno70(yearStart, yearEnd) {
  return ee.Image(ee.List.sequence(yearStart, yearEnd).iterate(
    function(year, acumulado) {
      return ee.Image(acumulado).or(clasificacion(year).eq(70));
    },
    ee.Image(0)
  )).and(candidato);
}

function permaneceSin70(yearStart, yearEnd) {
  return ee.Image(ee.List.sequence(yearStart, yearEnd).iterate(
    function(year, acumulado) {
      return ee.Image(acumulado).and(clasificacion(year).neq(70));
    },
    ee.Image(1)
  )).and(candidato);
}

function permaneceDestino(yearStart, yearEnd) {
  return ee.Image(ee.List.sequence(yearStart, yearEnd).iterate(
    function(year, acumulado) {
      var clase = clasificacion(year);
      var conserva13 = candidato70a13.and(clase.eq(13));
      var conserva68 = candidato70a68.and(clase.eq(68));
      return ee.Image(acumulado).and(conserva13.or(conserva68));
    },
    candidato
  ));
}

var pixelHa30 = ee.Image.pixelArea().divide(10000);
var retorno70_2016_2018 = algunRetorno70(2016, 2018);
var retorno70_2016_2024 = algunRetorno70(2016, 2024);
var sin70_2016_2024 = permaneceSin70(2016, 2024);
var destino_2016_2018 = permaneceDestino(2016, 2018);
var destino_2016_2024 = permaneceDestino(2016, 2024);

stackAreas = stackAreas
  .addBands(
    pixelHa30.updateMask(candidato70a13).rename('candidato_70_13_ha')
  )
  .addBands(
    pixelHa30.updateMask(candidato70a68).rename('candidato_70_68_ha')
  )
  .addBands(
    pixelHa30.updateMask(candidato).rename('candidato_total_ha')
  )
  .addBands(
    pixelHa30.updateMask(retorno70_2016_2018)
      .rename('retorno_70_2016_2018_ha')
  )
  .addBands(
    pixelHa30.updateMask(retorno70_2016_2024)
      .rename('retorno_70_2016_2024_ha')
  )
  .addBands(
    pixelHa30.updateMask(sin70_2016_2024)
      .rename('sin_70_continuo_2016_2024_ha')
  )
  .addBands(
    pixelHa30.updateMask(destino_2016_2018)
      .rename('destino_continuo_2016_2018_ha')
  )
  .addBands(
    pixelHa30.updateMask(destino_2016_2024)
      .rename('destino_continuo_2016_2024_ha')
  )
  .addBands(
    pixelHa30.updateMask(candidato.and(clasificacion(2024).eq(70)))
      .rename('clase_70_en_2024_ha')
  );

var areas = stackAreas.reduceRegion({
  reducer: ee.Reducer.sum(),
  geometry: geometria,
  scale: 30,
  maxPixels: 1e9,
  tileScale: 4
});

function mosaicoAnual(year) {
  return mosaicos
    .filter(ee.Filter.eq('year', year))
    .filterBounds(contexto)
    .mosaic()
    .clip(contexto);
}

function bandaNdvi(year) {
  year = ee.Number(year);
  return mosaicoAnual(year)
    .select('ndvi_median')
    .updateMask(candidato)
    .rename(ee.String('ndvi_').cat(year.format('%d')));
}

var stackNdvi = bandaNdvi(2012);
stackNdvi = ee.Image(ee.List.sequence(2013, 2018).iterate(
  function(year, acumulado) {
    return ee.Image(acumulado).addBands(bandaNdvi(year));
  },
  stackNdvi
));

var ndvi = stackNdvi.reduceRegion({
  reducer: ee.Reducer.mean(),
  geometry: geometria,
  scale: 30,
  maxPixels: 1e9,
  tileScale: 4
});

function obtener(diccionario, clave) {
  clave = ee.String(clave);
  return ee.Number(ee.Algorithms.If(
    diccionario.contains(clave),
    diccionario.get(clave),
    0
  ));
}

function serieAreas(prefijo) {
  return yearsClases.map(function(year) {
    var clave = ee.String(prefijo).cat(ee.Number(year).format('%d'));
    return obtener(areas, clave);
  });
}

var ndviLista = yearsNdvi.map(function(year) {
  var clave = ee.String('ndvi_').cat(ee.Number(year).format('%d'));
  return obtener(ndvi, clave);
});

var nMosaicos = yearsNdvi.map(function(year) {
  return mosaicos
    .filter(ee.Filter.eq('year', year))
    .filterBounds(contexto)
    .size();
});

var areaCandidato = obtener(areas, 'candidato_total_ha');
var areaRetornoCorto = obtener(areas, 'retorno_70_2016_2018_ha');
var areaRetornoLargo = obtener(areas, 'retorno_70_2016_2024_ha');
var areaSin70 = obtener(areas, 'sin_70_continuo_2016_2024_ha');
var areaDestinoCorto = obtener(areas, 'destino_continuo_2016_2018_ha');
var areaDestinoLargo = obtener(areas, 'destino_continuo_2016_2024_ha');
var area70_2024 = obtener(areas, 'clase_70_en_2024_ha');

print('PASO 6F2 — RESULTADO CV-042', ee.Dictionary({
  unidad_objetos: unidad.size(),
  years_clases: yearsClases,
  clase70_por_year_ha: serieAreas('clase70_ha_'),
  clase13_por_year_ha: serieAreas('clase13_ha_'),
  clase68_por_year_ha: serieAreas('clase68_ha_'),
  otra_clase_por_year_ha: serieAreas('otra_clase_ha_'),
  candidato_70_13_2014_2015_ha:
    obtener(areas, 'candidato_70_13_ha'),
  candidato_70_68_2014_2015_ha:
    obtener(areas, 'candidato_70_68_ha'),
  candidato_total_ha: areaCandidato,
  retorno_70_2016_2018_ha: areaRetornoCorto,
  retorno_70_2016_2018_pct:
    areaRetornoCorto.divide(areaCandidato).multiply(100),
  retorno_70_2016_2024_ha: areaRetornoLargo,
  retorno_70_2016_2024_pct:
    areaRetornoLargo.divide(areaCandidato).multiply(100),
  sin_70_continuo_2016_2024_ha: areaSin70,
  sin_70_continuo_2016_2024_pct:
    areaSin70.divide(areaCandidato).multiply(100),
  destino_continuo_2016_2018_ha: areaDestinoCorto,
  destino_continuo_2016_2018_pct:
    areaDestinoCorto.divide(areaCandidato).multiply(100),
  destino_continuo_2016_2024_ha: areaDestinoLargo,
  destino_continuo_2016_2024_pct:
    areaDestinoLargo.divide(areaCandidato).multiply(100),
  clase_70_en_2024_ha: area70_2024,
  clase_70_en_2024_pct:
    area70_2024.divide(areaCandidato).multiply(100),
  years_ndvi: yearsNdvi,
  n_mosaicos: nMosaicos,
  ndvi_median_medio_por_year: ndviLista
}));

// Control visual 2014 frente a 2015.
var mosaico2014 = mosaicoAnual(2014);
var mosaico2015 = mosaicoAnual(2015);
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

var tiposCambio = ee.Image(0)
  .where(candidato70a13, 1)
  .where(candidato70a68, 2)
  .updateMask(candidato)
  .clip(geometria);
var visCambios = {
  min: 1,
  max: 2,
  palette: ['FF8C00', '00FFFF']
};

var mapaIzquierdo = ui.Map();
var mapaDerecho = ui.Map();
mapaIzquierdo.setOptions('SATELLITE');
mapaDerecho.setOptions('SATELLITE');

mapaIzquierdo.addLayer(
  mosaico2014, visNatural, 'Mosaico 2014 — color natural', true
);
mapaDerecho.addLayer(
  mosaico2015, visNatural, 'Mosaico 2015 — color natural', true
);
mapaIzquierdo.addLayer(mosaico2014, visNdvi, 'NDVI 2014', false);
mapaDerecho.addLayer(mosaico2015, visNdvi, 'NDVI 2015', false);
mapaIzquierdo.addLayer(
  tiposCambio, visCambios, 'CV-042: naranja 70→13; cian 70→68', true, 0.65
);
mapaDerecho.addLayer(
  tiposCambio, visCambios, 'CV-042: naranja 70→13; cian 70→68', true, 0.65
);

var limite = unidad.style({
  color: 'FFFFFF',
  fillColor: '00000000',
  width: 2
});
mapaIzquierdo.addLayer(limite, {}, 'Límite Carabayllo 2', true);
mapaDerecho.addLayer(limite, {}, 'Límite Carabayllo 2', true);

mapaIzquierdo.add(ui.Label('Carabayllo 2 — 2014', {
  position: 'top-left',
  fontWeight: 'bold',
  fontSize: '16px',
  padding: '6px'
}));
mapaDerecho.add(ui.Label('Carabayllo 2 — 2015', {
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
mapaIzquierdo.centerObject(unidad, 14);

print('Lectura prudente:');
print('Retorno alto a 70 y NDVI estable = señal temporal o reclasificación.');
print('No retorno, NDVI estable = cambio cartográfico estable entre clases.');
print('No retorno y descenso NDVI visible = candidato a revisión ecológica.');
print('No se ejecutaron exportaciones.');
