// PASO 6E2-B — Persistencia y contraste Sentinel-2 del piloto Villa María.
// Refuerza el control de la transición cartográfica 70→24 de 2021–2022.
// No exporta archivos ni concluye pérdida ecológica automáticamente.

var ASSET_ACR =
  'projects/mapbiomas-lomas-jhoreck/assets/inputs/acr_lomas_5_ambitos_gee';
var ASSET_CLASES =
  'projects/mapbiomas-public/assets/peru/collection3/' +
  'mapbiomas_peru_collection3_integration_v1';

var acr = ee.FeatureCollection(ASSET_ACR);
var unidad = acr.filter(ee.Filter.eq('id_ambito', 'villa_maria'));
var geometria = unidad.geometry();
var contexto = geometria.buffer(1000);
var clases = ee.Image(ASSET_CLASES);

var c2020 = clases.select('classification_2020');
var c2021 = clases.select('classification_2021');
var c2022 = clases.select('classification_2022');
var c2023 = clases.select('classification_2023');
var c2024 = clases.select('classification_2024');

// Candidato original: clase loma en 2021 y urbano en 2022.
var candidato = c2021.eq(70).and(c2022.eq(24)).clip(geometria);

// Permanencia posterior de la clase urbana.
var urbanoHasta2023 = candidato.and(c2023.eq(24));
var urbanoHasta2024 = urbanoHasta2023.and(c2024.eq(24));
var noPersistente2023 = candidato.and(c2023.neq(24));
var noPersistente2024 = candidato.and(c2023.eq(24)).and(c2024.neq(24));

// Código de persistencia:
// 1 = urbano solo en 2022;
// 2 = urbano en 2022–2023, pero no en 2024;
// 3 = urbano de forma continua en 2022–2024.
var persistencia = ee.Image(0)
  .where(candidato, 1)
  .where(urbanoHasta2023, 2)
  .where(urbanoHasta2024, 3)
  .updateMask(candidato)
  .clip(geometria);

function areaHa(mask) {
  var resultado = ee.Image.pixelArea()
    .divide(10000)
    .updateMask(mask)
    .reduceRegion({
      reducer: ee.Reducer.sum(),
      geometry: geometria,
      scale: 30,
      maxPixels: 1e9,
      tileScale: 4
    });
  return ee.Number(ee.Algorithms.If(
    resultado.contains('area'),
    resultado.get('area'),
    0
  ));
}

function mascaraSentinel2(imagen) {
  var scl = imagen.select('SCL');
  var mascara = scl.neq(1)
    .and(scl.neq(3))
    .and(scl.neq(8))
    .and(scl.neq(9))
    .and(scl.neq(10))
    .and(scl.neq(11));

  return imagen
    .updateMask(mascara)
    .divide(10000)
    .copyProperties(imagen, ['system:time_start']);
}

function coleccionSentinel2(year) {
  return ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterBounds(contexto)
    .filterDate(year + '-01-01', (year + 1) + '-01-01')
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 60))
    .map(mascaraSentinel2);
}

function compuestoSentinel2(year) {
  return coleccionSentinel2(year)
    .median()
    .clip(contexto);
}

var s2_2021 = compuestoSentinel2(2021);
var s2_2022 = compuestoSentinel2(2022);

var visNaturalS2 = {
  bands: ['B4', 'B3', 'B2'],
  min: 0.02,
  max: 0.30,
  gamma: 1.15
};
var visFalsoColorS2 = {
  bands: ['B11', 'B8', 'B4'],
  min: 0.02,
  max: 0.38,
  gamma: 1.10
};
var visPersistencia = {
  min: 1,
  max: 3,
  palette: ['FFD700', 'FF8C00', 'D7191C']
};

print('PASO 6E2-B — PERSISTENCIA Y SENTINEL-2');
print('Unidad — esperado: 1 objeto', unidad.size());
print('Imágenes Sentinel-2 válidas de 2021',
  coleccionSentinel2(2021).size());
print('Imágenes Sentinel-2 válidas de 2022',
  coleccionSentinel2(2022).size());
print('Área candidata 70→24 en 2021–2022 — ha',
  areaHa(candidato));
print('Persiste como 24 hasta 2023 — ha',
  areaHa(urbanoHasta2023));
print('Persiste como 24 hasta 2024 — ha',
  areaHa(urbanoHasta2024));
print('No persiste como 24 en 2023 — ha',
  areaHa(noPersistente2023));
print('Persiste en 2023 pero no en 2024 — ha',
  areaHa(noPersistente2024));
print('Porcentaje del candidato persistente hasta 2024',
  areaHa(urbanoHasta2024).divide(areaHa(candidato)).multiply(100));

var mapaIzquierdo = ui.Map();
var mapaDerecho = ui.Map();

mapaIzquierdo.setOptions('SATELLITE');
mapaDerecho.setOptions('SATELLITE');

mapaIzquierdo.addLayer(
  s2_2021, visNaturalS2, 'Sentinel-2 2021 — color natural', true
);
mapaDerecho.addLayer(
  s2_2022, visNaturalS2, 'Sentinel-2 2022 — color natural', true
);

mapaIzquierdo.addLayer(
  s2_2021, visFalsoColorS2, 'Sentinel-2 2021 — falso color', false
);
mapaDerecho.addLayer(
  s2_2022, visFalsoColorS2, 'Sentinel-2 2022 — falso color', false
);

mapaIzquierdo.addLayer(
  persistencia, visPersistencia, 'Persistencia MapBiomas', true, 0.55
);
mapaDerecho.addLayer(
  persistencia, visPersistencia, 'Persistencia MapBiomas', true, 0.55
);

var limite = unidad.style({
  color: 'FFFFFF',
  fillColor: '00000000',
  width: 2
});
mapaIzquierdo.addLayer(limite, {}, 'Límite ACR', true);
mapaDerecho.addLayer(limite, {}, 'Límite ACR', true);

mapaIzquierdo.add(ui.Label('2021 — antes', {
  position: 'top-left',
  fontWeight: 'bold',
  fontSize: '16px',
  padding: '6px'
}));
mapaDerecho.add(ui.Label('2022 — después', {
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

print('Leyenda de persistencia:');
print('1 amarillo = urbano solo en 2022');
print('2 naranja = urbano en 2022–2023, no en 2024');
print('3 rojo = urbano continuo en 2022–2024');
print('No se ejecutaron exportaciones.');
