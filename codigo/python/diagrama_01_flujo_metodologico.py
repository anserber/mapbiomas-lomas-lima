#!/usr/bin/env python3
"""
CONTRACT     : D01
QUESTION     : ¿Qué secuencia de pasos, controles y puertas de decisión condujo
               de los productos oficiales de MapBiomas Perú a los resultados
               publicados, y qué se descartó en cada punto?
MESSAGE      : El diagnóstico es un protocolo con controles y renuncias
               documentadas, no un encadenamiento lineal de procesos. La columna
               derecha registra todo lo que se probó y se retiró, con la razón
               medida que lo motivó.
SOURCE       : 00_protocolo_diagnostico/ (guías de los pasos 1 a 12),
               los 60 scripts de GEE y Python del proyecto, y
               08_cierre_metodologico/02_final/metodologia_final_lomas_mapbiomas.md
               con su adenda v1.1.
OUTPUT       : diagrama_01_flujo_metodologico

Nota de alcance: la skill de figuras científicas excluye explícitamente los
diagramas de flujo, por no tener datos que verificar. Este producto se
construye fuera de sus garantías: no lleva manifiesto de fuentes con hash ni
verificación automática de trazado. Su exactitud se sostiene en que cada
subpaso corresponde a un script o a un documento de control existente en el
repositorio.

Requiere: graphviz (paquete de Python y binario `dot`).

Run:  python diagrama_01_flujo_metodologico.py
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import graphviz

ROOT = Path(__file__).resolve().parents[3]
OUTDIR = ROOT / "10_comunicacion_resultados/02_final/figuras"
STEM = "diagrama_01_flujo_metodologico"

FUENTE = "Helvetica"
PT_TITULO = "9"
PT_CUERPO = "7.6"
PT_NOTA = "7"

C_INSUMO = "#E4ECF4"
C_PROCESO = "#FFFFFF"
C_CONTROL = "#FDF2E0"
C_PRODUCTO = "#E7F1E7"
C_DESCARTE = "#FBEBE8"
C_BORDE = "#3A3A3A"
C_BORDE_DESCARTE = "#B5482F"
C_ARISTA = "#4A4A4A"


def caja(titulo: str, lineas: list[str]) -> str:
    """Etiqueta HTML: título en negrita y subpasos alineados a la izquierda."""
    filas = [f'<TR><TD ALIGN="LEFT"><B>{titulo}</B></TD></TR>']
    for l in lineas:
        filas.append(f'<TR><TD ALIGN="LEFT">{l}</TD></TR>')
    return ("<<TABLE BORDER=\"0\" CELLBORDER=\"0\" CELLSPACING=\"0\" "
            "CELLPADDING=\"1\">" + "".join(filas) + "</TABLE>>")


# ---------------------------------------------------------------------------
# Cadena principal: los doce pasos con sus subpasos reales
# ---------------------------------------------------------------------------
PASOS = [
    ("p0", C_INSUMO, "INSUMOS OFICIALES · MapBiomas Perú Colección 3", [
        "Integración anual de cobertura y uso, 1985–2024, 30 m",
        "Mapa oficial de transiciones anuales y multianuales",
        "Mosaicos Landsat de época seca y húmeda (PANAMAZON, RAISG)",
        "MapBiomas Fuego, Colección 1 · Módulos de vegetación",
        "ATBD y factsheets: clase 70 beta, umbral de probabilidad 40 %,",
        "Random Forest de 60 árboles, jerarquía de prevalencia de clases",
    ]),
    ("p1", C_PROCESO, "PASO 1 · Obtención de límites", [
        "1.1 Descarga del ACR desde el geoservicio oficial (DS 011-2019-MINAM)",
        "1.2 Filtrado de los cinco ámbitos y registro de fuentes y fechas",
        "1.3 Solicitud formal de la geometría de la KBA Lomas de Atocongo",
    ]),
    ("p2", C_PROCESO, "PASO 2 · Preparación de geometrías", [
        "2.1 Validación topológica y normalización a multipolígono",
        "2.2 Reproyección a EPSG:32718 para medir y EPSG:4326 para GEE",
        "2.3 Conciliación de áreas frente al valor legal de 13 475,74 ha",
    ]),
    ("p3", C_PROCESO, "PASO 3 · Zonas de influencia", [
        "3.1 Máscara terrestre INEI 2023: disolución y validación",
        "3.2 Anillos disjuntos de 0–500, 500–1 000 y 1 000–2 000 m",
        "3.3 Recorte a tierra; exclusión del ACR y del enclave SEDAPAL",
        "3.4 Control de solapamiento y doble nivel: 15 anillos por ámbito",
        "      para diagnóstico y 3 anillos disueltos para totales",
    ]),
    ("p4", C_PROCESO, "PASO 4 · Verificación de los productos MapBiomas", [
        "4.1 Auditoría del asset de integración: bandas, años, clases, resolución",
        "4.2 Auditoría del asset de transiciones",
        "4.3 Auditoría de los mosaicos Landsat oficiales",
        "4.4 Lectura de ATBD y factsheets; ficha de asset y limitaciones",
    ]),
    ("p5", C_PROCESO, "PASO 5 · Extracción de la serie 1985–2024", [
        "5A Preparación del ACR para GEE y carga del asset",
        "5B Verificación del asset: cinco objetos, identificadores, áreas",
        "5C Prueba piloto de cinco años",
        "5D Serie completa por bloques quinquenales",
        "5E Validación y consolidación de CSV con firma SHA-256",
        "5F Réplica para anillos y corrección del enclave de Carabayllo 2",
        "5G Plan B para la KBA: exportación de 40 bandas y proceso local",
    ]),
    ("p6", C_CONTROL, "PASO 6 · Años representativos, transiciones y controles", [
        "6A Auditoría del asset de transiciones y verificación del código",
        "      de transición como clase inicial × 100 + clase final",
        "6B Inventario temporal en Python sobre las tablas validadas",
        "6C Selección de periodos por reglas explícitas",
        "6D Medición de transiciones: validación de codificación, piloto,",
        "      ACR y anillos",
        "6E Controles visuales y espectrales: mosaicos, versiones,",
        "      piloto visual, persistencia con Sentinel-2, control",
        "      independiente con Dynamic World, Ancón 2000–2001 y",
        "      1985–1986, insumo Landsat de 40 años, ventana 1986–2024",
        "6F Persistencia de transiciones urbanas y control CV-042",
        "6G Tipología de confianza de 45 controles; 12 revisados en detalle",
    ]),
    ("p7", C_PROCESO, "PASO 7 · Persistencia, eventos y ruido temporal", [
        "7A Métricas básicas: frecuencia, racha máxima, cambios de estado,",
        "      ausencias y apariciones aisladas",
        "7B Eventos estables con ventanas W3 y W5, y eventos censurados",
        "7C Sensibilidad W3 frente a W5 y conciliación con el asset oficial",
        "7D Resultados finales por unidad: ACR, anillos y KBA restringida",
    ]),
    ("p8", C_CONTROL, "PASO 8 · Validación visual ciega", [
        "8A Inventario de los seis estratos de señal candidata",
        "8B Generación de candidatos: reserva pública en GEE y KBA en Python",
        "8C Cierre de la muestra: 60 sectores únicos y 6 repeticiones ciegas",
        "8D Evaluación con ficha común sobre mosaicos MapBiomas, color",
        "      natural, falso color, NDVI, Landsat C2 y Sentinel-2",
        "8E Métricas: concordancia, Wilson 95 %, control intraobservador",
    ]),
    ("p9", C_PROCESO, "PASO 9 · Prueba de productos complementarios", [
        "9A Inventario técnico de MapBiomas Fuego",
        "9B Medición de la señal de fuego en las ocho unidades",
        "9C Reconstrucción de Pérdida de Vegetación y Veg. Secundaria",
        "9D Prueba de valor añadido frente al núcleo",
        "9E Matriz de decisión y dictamen por producto",
    ]),
    ("p10", C_PROCESO, "PASO 10 · Cierre metodológico", [
        "10.1 Dictamen de factibilidad: AMARILLO CONTROLADO",
        "10.2 Congelación de la metodología v1.0 y de la matriz de variables",
        "10.3 Adenda v1.1: línea base en 1986 y regímenes de sensor",
    ]),
    ("p11", C_PROCESO, "PASO 11 · Integración de resultados públicos", [
        "11.1 Tabla maestra de las ocho unidades públicas",
        "11.2 Diccionario de campos y reglas de uso",
        "11.3 Versión v2: tres definiciones de superficie declaradas y",
        "        retirada del campo que sumaba señales no sumables",
    ]),
    ("p12", C_PROCESO, "PASO 12 · Comunicación reproducible", [
        "12A Contratos de comunicación por producto",
        "12B Figuras analíticas y tablas automatizadas en Python",
        "12C Exportación de capas espaciales en GEE",
        "12D Composición de M00 en QGIS y de M01–M02 en Python",
        "12E Texto de resultados, pies de figura y manifiesto de fuentes",
    ]),
    ("pf", C_PRODUCTO, "PRODUCTOS PÚBLICOS", [
        "Tabla maestra v2 y diccionario · 7 figuras analíticas · 3 mapas",
        "Tablas 5, 6 y 9 automatizadas · diagrama metodológico A1–A3",
        "Código de GEE y Python, protocolo y documentos de control",
        "Retroalimentación a MapBiomas Perú sobre la clase beta 70",
    ]),
]

# ---------------------------------------------------------------------------
# Puertas de decisión: lo que se probó y se retiró, con su razón medida
# ---------------------------------------------------------------------------
DESCARTES = [
    ("d_kba", "p1", "Paso 1.3 · KBA Atocongo", [
        "Retirada de los productos",
        "públicos: condiciones de uso",
        "y redistribución. Se conserva",
        "como contexto restringido.",
    ]),
    ("d_1985", "p6", "Paso 6E · Año 1985", [
        "Ruptura de inicio: 17 escenas",
        "Landsat y 58 % de nubes;",
        "−29,3 % de clase 70.",
        "Línea base movida a 1986.",
    ]),
    ("d_rupt", "p6", "Pasos 6E–6F · Rupturas", [
        "Ancón 2000–2001: 532,735 ha.",
        "CV-042 Carabayllo 2: 10,734 ha.",
        "Sin contrapartida espectral.",
        "Fuera de los totales de cambio.",
    ]),
    ("d_e5e6", "p8", "Paso 8E · Estratos E5 y E6", [
        "Recuperación 68→70: 27,3 %.",
        "Cambio 70→13: 37,5 %.",
        "Fuera del núcleo analítico.",
    ]),
    ("d_fuego", "p9", "Paso 9B · MapBiomas Fuego", [
        "0 ha quemadas y 0 años con",
        "señal, 2013–2024. Descartado;",
        "se reporta el resultado",
        "negativo como limitación.",
    ]),
    ("d_vegsec", "p9", "Paso 9C · Veg. Secundaria", [
        "0 ha con ventana W5 en las",
        "ocho unidades. Descartado.",
    ]),
    ("d_perdida", "p9", "Paso 9D · Pérdida de Veg.", [
        "34,457 ha W5, con 18,453 ha",
        "comunes al núcleo. Solo como",
        "sensibilidad contextual.",
    ]),
    ("d_modelo", "p10", "Paso 10.1 · Modelo 2050", [
        "Sin variable objetivo validada",
        "ni predictores defendibles.",
        "Análisis descartado.",
    ]),
    ("d_frag", "p10", "Paso 10.1 · Fragmentación", [
        "No calculadas ni validadas",
        "en esta versión. Diferidas.",
    ]),
]


# ---------------------------------------------------------------------------
# Reparto en dos láminas A4 verticales. El corte separa la preparación del
# dato de su auditoría, y deja ocho de las nueve puertas de decisión en la
# lámina B, que así sostiene el argumento por sí sola.
# ---------------------------------------------------------------------------
LAMINAS = {
    "A": {
        "titulo": "Lámina A · Preparación y extracción del dato",
        "pasos": ["p0", "p1", "p2", "p3", "p4", "p5"],
        "descartes": ["d_kba"],
        "enlace": [("continua", "Continúa en la lámina B")],
    },
    "B": {
        "titulo": "Lámina B · Auditoría temporal, persistencia y validación",
        "pasos": ["p6", "p7", "p8"],
        "descartes": ["d_1985", "d_rupt", "d_e5e6"],
        "enlace": [("viene", "Viene de la lámina A"),
                   ("continua", "Continúa en la lámina C")],
    },
    "C": {
        "titulo": "Lámina C · Decisiones, cierre y productos",
        "pasos": ["p9", "p10", "p11", "p12", "pf"],
        "descartes": ["d_fuego", "d_vegsec", "d_perdida", "d_modelo", "d_frag"],
        "enlace": [("viene", "Viene de la lámina B")],
    },
}


def construir(lamina: str, dpi: str | None = None) -> graphviz.Digraph:
    """Una lámina del diagrama, en dos columnas verticales.

    Cada columna se encadena con sus propias aristas de orden, y las puertas
    se enlazan a su paso de origen con aristas sin restricción de rango. Sin
    esas dos cadenas, Graphviz reparte los nodos a lo ancho y el resultado
    sale apaisado, que es lo contrario de lo que pide una página A4 vertical.
    """
    cfg = LAMINAS[lamina]
    pasos = [p for p in PASOS if p[0] in cfg["pasos"]]
    descartes = [d for d in DESCARTES if d[0] in cfg["descartes"]]

    g = graphviz.Digraph(f"{STEM}_{lamina}")
    # nodesep separa las dos columnas. Estaba en 0,15 in y, junto con el margen
    # horizontal de las cajas, dejaba la lámina B en 163,3 mm de ancho: 3,3 mm
    # por encima de la caja de texto de 160 mm del documento. Word habría
    # reescalado la lámina y el cuerpo de 7,6 pt habría caído por debajo del
    # piso de 7 pt. Se estrecha la separación en lugar de escalar el dibujo,
    # que es lo que habría hundido la tipografía.
    g.attr(rankdir="TB", splines="polyline", nodesep="0.10", ranksep="0.06",
           bgcolor="white", newrank="true")
    # Graphviz añade 0,5 in de margen por lado en la salida PDF, y con ello la
    # caja del archivo pasaba de 242 a 270 mm de alto: Word la habría reescalado
    # y la tipografía habría caído por debajo del piso de 7 pt. Se deja solo un
    # respiro de 1,3 mm para que el trazo del borde no se corte.
    g.attr(margin="0", pad="0.025")
    if dpi:
        g.attr(dpi=dpi)
    g.attr("node", shape="box", style="filled", fontname=FUENTE,
           fontsize=PT_CUERPO, color=C_BORDE, penwidth="0.7",
           # El margen horizontal de las cajas se bajó de 0,11 a 0,085 in por la misma
           # razón que nodesep: la lámina B salía a 163,3 mm y la caja de texto del
           # documento mide 160. Con 0,085 queda en 159,1 mm y la tipografía conserva
           # sus 7,6 pt de cuerpo y 7 pt de nota, que es el piso del documento.
           margin="0.040,0.042")
    g.attr("edge", color=C_ARISTA, penwidth="0.8", arrowsize="0.6")

    # Dos columnas, con cada puerta de decision al mismo rango que el paso del
    # que sale.
    #
    # Antes las puertas se encadenaban entre si en la columna derecha con
    # aristas invisibles. Como un paso podia tener tres puertas y otro ninguna,
    # las cajas se desalineaban de su origen y los conectores cruzaban por
    # encima de otros bloques: para saber de donde salia cada puerta habia que
    # rastrear una diagonal por todo el diagrama. Ahora las puertas de un mismo
    # paso se funden en una caja, `rank=same` la fija a la altura de su paso, y
    # el conector es un segmento horizontal corto que no puede cruzarse con
    # ningun otro. Los textos de las puertas se reescribieron a lineas de unos
    # 31 caracteres para que las dos columnas quepan en los 160 mm de la caja.
    for nid, color, titulo, lineas in pasos:
        g.node(nid, label=caja(titulo, lineas), fillcolor=color)
    for (a, *_), (b, *_) in zip(pasos, pasos[1:]):
        g.edge(a, b, weight="20")

    porOrigen = {}
    for nid, origen, titulo, lineas in descartes:
        porOrigen.setdefault(origen, []).append((titulo, lineas))

    for origen, grupo in porOrigen.items():
        clave = f"gate_{origen}"
        filas = []
        for k, (t, ls) in enumerate(grupo):
            if k:
                filas.append('<TR><TD ALIGN="LEFT"> </TD></TR>')
            filas.append(f'<TR><TD ALIGN="LEFT"><B>{t}</B></TD></TR>')
            for l in ls:
                filas.append(f'<TR><TD ALIGN="LEFT">{l}</TD></TR>')
        g.node(clave, fillcolor=C_DESCARTE, color=C_BORDE_DESCARTE,
               style="filled,dashed", fontsize=PT_NOTA,
               label='<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" '
                     'CELLPADDING="1">' + "".join(filas) + "</TABLE>>")
        g.edge(origen, clave, style="dashed", color=C_BORDE_DESCARTE,
               constraint="false", arrowsize="0.5", penwidth="0.6")
        with g.subgraph() as fila:
            fila.attr(rank="same")
            fila.node(origen)
            fila.node(clave)

    # Sin encadenarlas, Graphviz reparte las puertas en columnas distintas y el
    # dibujo se va de 160 a 207 mm de ancho. La cadena invisible las mantiene
    # en una sola columna a la derecha.
    claves = [f"gate_{o}" for o in porOrigen]
    for a, b in zip(claves, claves[1:]):
        g.edge(a, b, style="invis", weight="20")

    for clave, texto in cfg["enlace"]:
        g.node(clave, label=texto, shape="box", style="filled,dashed",
               fillcolor="#F2F2F2", color="#888888", fontsize=PT_NOTA,
               fontname=FUENTE)
        if clave == "continua":
            g.edge(pasos[-1][0], clave, weight="20", style="dashed",
                   color="#888888")
        else:
            g.edge(clave, pasos[0][0], weight="20", style="dashed",
                   color="#888888")

    return g


def main():
    if shutil.which("dot") is None:
        raise SystemExit("no se encuentra el binario `dot`; instalar Graphviz")
    OUTDIR.mkdir(parents=True, exist_ok=True)
    for lamina in LAMINAS:
        stem = f"{STEM}_{lamina.lower()}"
        # Se escriben los bytes directamente: `render` deja un archivo .gv
        # intermedio que no puede borrarse en la carpeta montada del proyecto.
        (OUTDIR / f"{stem}.pdf").write_bytes(
            construir(lamina).pipe(format="pdf"))
        (OUTDIR / f"{stem}.png").write_bytes(
            construir(lamina, dpi="300").pipe(format="png"))
        n_p = len(LAMINAS[lamina]["pasos"])
        n_d = len(LAMINAS[lamina]["descartes"])
        print(f"  {stem}: {n_p} bloques de proceso, {n_d} puertas de decisión")
    print(f"  salida en {OUTDIR}")


if __name__ == "__main__":
    main()
