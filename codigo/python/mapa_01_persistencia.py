#!/usr/bin/env python3
"""
CONTRACT     : M01
QUESTION     : ¿Dónde se localiza el núcleo de la clase 70 — Loma costera que
               persiste todos los años, dónde el margen de clasificación
               inestable, y qué relación guardan con el límite del ACR?
MESSAGE      : El núcleo persistente forma manchas compactas en las cabeceras de
               las lomas, rodeadas por un margen de clasificación inestable. Una
               parte sustancial de ese núcleo queda fuera del ACR y de su
               periferia de 2 km, dentro del mismo recuadro de análisis.
SOURCE       : 10_comunicacion_resultados/01_intermediate/rasteres/
               persistencia_clase70_frecuencia_1985_2024.tif (paso 12C)
               01_limites/02_final/acr_sistema_lomas_5_ambitos_epsg32718.gpkg
               02_zonas_influencia/02_final/
               anillos_3_distancias_sistema_periferia_externa_epsg32718.gpkg
               02_zonas_influencia/02_final/
               mascara_terrestre_peru_inei2023_epsg32718_unificada.gpkg
UNIT         : número de años clasificados como clase 70, de 1 a 40
INCLUDES     : el recuadro completo exportado por el paso 12C, que excede el ACR
               y su periferia. Se muestra a propósito: la loma persistente
               continúa fuera de los límites del área protegida.
EXCLUDES     : la frecuencia cero no se dibuja. KBA restringida.
PROHIBITIONS : no citar hectáreas de la superficie exterior al ACR: el recuadro
               es el rectángulo de exportación y su extensión es arbitraria, de
               modo que cualquier total dependería de dónde se cortó. La
               observación es cualitativa y así debe redactarse.
VISUAL FORM  : mapa planimétrico único en CRS proyectado. Se descarta el relieve
               en perspectiva: el lector debe comparar frecuencias en todo el
               paisaje y el escorzo y la oclusión tras las crestas ocultarían
               dato.
LIMIT        : frecuencia de clasificación de una clase beta; no mide densidad,
               biomasa ni condición ecológica de la vegetación.
OUTPUT       : mapa_01_persistencia_clase70

Requiere: geopandas, rasterio.

Run:  python mapa_01_persistencia.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.patches import Patch, Rectangle
import numpy as np

import geopandas as gpd
import rasterio

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sciviz

# ---------------------------------------------------------------- paths ----
ROOT = Path(__file__).resolve().parents[3]
RASTER = (ROOT / "10_comunicacion_resultados/01_intermediate/rasteres/"
                 "persistencia_clase70_frecuencia_1985_2024.tif")
ACR = ROOT / "01_limites/02_final/acr_sistema_lomas_5_ambitos_epsg32718.gpkg"
ANILLOS = (ROOT / "02_zonas_influencia/02_final/"
                  "anillos_3_distancias_sistema_periferia_externa_epsg32718.gpkg")
TIERRA = (ROOT / "02_zonas_influencia/02_final/"
                 "mascara_terrestre_peru_inei2023_epsg32718_unificada.gpkg")
OUTDIR = ROOT / "10_comunicacion_resultados/02_final/mapas"
STEM = "mapa_01_persistencia_clase70"

LANG = "es"
FORMATS = ("pdf", "png")

CRS_MAPA = "EPSG:32718"
CRS_ETIQUETA = "WGS 84 / UTM 18S (EPSG:32718)"
N_YEARS = 40

# Clases declaradas: la última aísla el núcleo que nunca dejó de ser clase 70.
CORTES = [0.5, 10.5, 20.5, 30.5, 39.5, 40.5]
ETIQUETAS_CLASE = ["1–10", "11–20", "21–30", "31–39", "40 (núcleo)"]
COLORES = ["#E8F3E3", "#BFE0B6", "#8CCA86", "#4EAC5E", "#17683A"]

# Nombre, desplazamiento en puntos y alineación. Sin desplazar, las etiquetas
# de Carabayllo 1 y 2 se solapan y la de Villa María se sale por el borde este.
ETIQUETAS_AMBITO = {
    "ancon":        ("Ancón",        (0, 0),    "center"),
    "carabayllo_1": ("Carabayllo 1", (-16, -9), "right"),
    "carabayllo_2": ("Carabayllo 2", (16, 9),   "left"),
    "amancaes":     ("Amancaes",     (0, -11),  "center"),
    "villa_maria":  ("Villa María",  (-8, 0),   "right"),
}


# ---------------------------------------------------- input assertions -----
def load():
    with rasterio.open(RASTER) as src:
        if src.crs.to_string() != CRS_MAPA:
            raise SystemExit(f"el ráster está en {src.crs}, se esperaba {CRS_MAPA}")
        frec = src.read(1)
        extent = (src.bounds.left, src.bounds.right,
                  src.bounds.bottom, src.bounds.top)
    if frec.max() > N_YEARS:
        raise SystemExit(f"frecuencia máxima {frec.max()} por encima de {N_YEARS}")

    acr = gpd.read_file(ACR).to_crs(CRS_MAPA)
    anillos = gpd.read_file(ANILLOS).to_crs(CRS_MAPA)
    tierra = gpd.read_file(TIERRA).to_crs(CRS_MAPA)
    if len(acr) != 5:
        raise SystemExit(f"se esperaban 5 ámbitos y hay {len(acr)}")

    # Control: el núcleo dentro del ACR debe reproducir la tabla maestra.
    from rasterio.mask import mask as rmask
    with rasterio.open(RASTER) as src:
        dentro, _ = rmask(src, acr.geometry, crop=True, filled=True, nodata=0)
    nucleo_acr = float((dentro[0] == N_YEARS).sum()) * 900 / 10000
    # Tolerancia del 0,5 %: rasterio incluye el píxel cuando su centro cae
    # dentro del polígono, mientras Earth Engine pondera los píxeles parciales
    # del borde. La diferencia es de borde, no de contenido, y crece con el
    # perímetro de la unidad. Por encima del 0,5 % dejaría de ser explicable así.
    referencia = 3542.972
    desvio = abs(nucleo_acr - referencia) / referencia
    if desvio > 0.005:
        raise SystemExit(f"el núcleo dentro del ACR da {nucleo_acr:.3f} ha y la "
                         f"tabla maestra declara {referencia} ha "
                         f"({100 * desvio:.2f} % de desvío)")
    print(f"  núcleo dentro del ACR: {nucleo_acr:.3f} ha "
          f"(tabla: {referencia}; desvío de borde {100 * desvio:.2f} %)")
    print(f"  núcleo en todo el recuadro: "
          f"{float((frec == N_YEARS).sum()) * 900 / 10000:.0f} ha")

    return frec, extent, acr, anillos, tierra


# ------------------------------------------------------------- drawing -----
def build(frec, extent, acr, anillos, tierra):
    fig, ax = sciviz.new_figure(width=132, height_mm=200)

    x0, x1, y0, y1 = extent
    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)
    ax.set_aspect("equal")

    # Tierra de fondo: sin ella el desierto y el mar son el mismo blanco.
    tierra.clip(box(extent)).plot(ax=ax, facecolor="#F5F2ED",
                                 edgecolor="#B9B2A6", linewidth=0.4, zorder=0)

    norma = BoundaryNorm(CORTES, len(COLORES))
    ax.imshow(np.ma.masked_where(frec < 1, frec), extent=extent, origin="upper",
              cmap=ListedColormap(COLORES), norm=norma,
              interpolation="nearest", zorder=2)

    # Velo de contexto. El recuadro es el rectángulo de exportación del paso
    # 12C y excede el ACR y su periferia; eso se muestra a propósito, porque la
    # loma persistente no se detiene en el límite administrativo. Pero sin
    # distinguir dentro de fuera, el lector puede leer todo el recuadro como
    # ámbito medido y sacar hectáreas de donde no las hay. El velo mantiene
    # visible el exterior y lo subordina: no oculta, jerarquiza.
    ambito = gpd.GeoSeries(
        [acr.union_all().union(anillos.union_all())], crs=acr.crs)
    fuera = gpd.GeoSeries([box(extent)], crs=acr.crs).difference(ambito, align=False)
    fuera.plot(ax=ax, facecolor="white", edgecolor="none", alpha=0.55, zorder=2.5)

    anillos.dissolve().boundary.plot(ax=ax, edgecolor="#7A7A7A", linewidth=0.5,
                                     linestyle=(0, (4, 2)), zorder=3)
    acr.boundary.plot(ax=ax, edgecolor="#1A1A1A", linewidth=0.8, zorder=4)

    for _, r in acr.iterrows():
        c = r.geometry.representative_point()
        texto, desplaza, alinea = ETIQUETAS_AMBITO[r["id_ambito"]]
        ax.annotate(texto, (c.x, c.y), xytext=desplaza,
                    textcoords="offset points", ha=alinea, va="center",
                    fontsize=sciviz.pt(0.85), zorder=6,
                    path_effects=[pe.withStroke(linewidth=1.8, foreground="white")])

    # Rejilla UTM en kilómetros: a 35 km de ancho es la convención local y se
    # lee más rápido que una retícula en grados.
    ax.set_xticks(np.arange(260000, x1, 10000))
    ax.set_yticks(np.arange(8660000, y1, 10000))
    ax.set_xticklabels([f"{v/1000:.0f}" for v in ax.get_xticks()])
    ax.set_yticklabels([f"{v/1000:.0f}" for v in ax.get_yticks()])
    ax.set_xlabel("Este UTM (km)")
    ax.set_ylabel("Norte UTM (km)")
    ax.grid(color="#D8D8D8", linewidth=0.3, zorder=1)
    ax.tick_params(labelsize=sciviz.pt(0.8))

    # El mar del suroeste y el cuadrante nororiental son las dos zonas sin dato:
    # ahí van escala, norte, localizador y declaración del SRC.
    sciviz.add_scalebar(ax, 10000, location=(0.05, 0.055), segments=2)
    sciviz.add_north_arrow(ax, location=(0.950, 0.700), size_frac=0.056,
                           fontsize=sciviz.pt(1.55))
    ax.text(0.05, 0.020, CRS_ETIQUETA, transform=ax.transAxes, ha="left",
            va="bottom", fontsize=sciviz.pt(0.75), color="#555555", zorder=60)

    manijas = [Patch(facecolor=c, edgecolor="none", label=e)
               for c, e in zip(COLORES, ETIQUETAS_CLASE)]
    manijas += [
        plt.Line2D([], [], color="#1A1A1A", linewidth=0.8,
                   label="Ámbitos del ACR"),
        plt.Line2D([], [], color="#7A7A7A", linewidth=0.5, linestyle=(0, (4, 2)),
                   label="Periferia externa, 2 km"),
    ]
    ax.legend(handles=manijas, loc="lower left",
              bbox_to_anchor=(0.015, 0.105), frameon=True, framealpha=0.92,
              edgecolor="#CCCCCC", fontsize=sciviz.pt(0.8),
              handlelength=1.1, handleheight=0.9, labelspacing=0.35,
              title="Años como clase 70", title_fontsize=sciviz.pt(0.8))

    # Localizador: sin él, un lector de fuera no sabe dónde está esto.
    # Se ancla con inset_axes y no con el ayudante de sciviz: aquel se apoya en
    # la caja nominal del eje, que con aspecto igual es más ancha que el mapa
    # dibujado, y el recuadro se salía del marco por arriba y dejaba aire a la
    # derecha. En coordenadas de eje queda a ras de la esquina.
    ancho_loc, alto_loc = 0.335, 0.200
    loc = ax.inset_axes([1 - ancho_loc, 1 - alto_loc, ancho_loc, alto_loc])
    loc.set_xticks([]); loc.set_yticks([])
    loc.set_facecolor("white")
    for borde in loc.spines.values():
        borde.set_linewidth(0.5)
        borde.set_edgecolor("#555555")
    peru = tierra.dissolve()
    peru.plot(ax=loc, facecolor="#EDEAE4", edgecolor="#999999", linewidth=0.4)
    loc.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, facecolor="none",
                            edgecolor="#D55E00", linewidth=0.9, zorder=5))
    b = peru.total_bounds
    loc.set_xlim(b[0], b[2]); loc.set_ylim(b[1], b[3])
    # adjustable="datalim" mantiene la caja en el rectángulo pedido y expande
    # los límites de dato. Con el ajuste por caja, que es el predeterminado,
    # matplotlib encoge el recuadro para respetar la forma del Perú y deja aire
    # entre el localizador y el marco del mapa.
    loc.set_aspect("equal", adjustable="datalim")

    return fig


def box(extent):
    from shapely.geometry import box as sbox
    x0, x1, y0, y1 = extent
    return sbox(x0, y0, x1, y1)


# ---------------------------------------------------------------- main -----
def main():
    frec, extent, acr, anillos, tierra = load()
    fig = build(frec, extent, acr, anillos, tierra)

    manifest = sciviz.finalize(
        fig, outdir=OUTDIR, stem=STEM, contract="M01",
        source=[RASTER, ACR, ANILLOS, TIERRA], lang=LANG, formats=FORMATS,
        caption=(
            "Persistencia cartográfica de la clase 70 — Loma costera en el "
            "entorno del ACR Sistema de Lomas de Lima, 1985-2024. El color "
            "indica el número de años en que cada píxel de 30 m fue clasificado "
            "como clase 70; la clase más oscura reúne los píxeles que lo fueron "
            "los cuarenta años. La frecuencia cero no se representa. El recuadro "
            "corresponde a la extensión exportada del análisis y excede el "
            "límite del ACR y de su periferia de 2 km: esa superficie exterior "
            "se atenúa con un velo blanco, de modo que sigue visible como "
            "contexto pero se distingue del ámbito sobre el que se mide."
        ),
        note=(
            "n = 40 años. La superficie de núcleo dentro de los cinco ámbitos "
            "del ACR es de 3 542,972 ha, la misma cifra de la tabla maestra. En "
            "el interior del recuadro se observa núcleo persistente fuera del "
            "ACR y de su periferia; esa superficie no se cuantifica porque la "
            "extensión del recuadro es la del rectángulo de exportación y "
            "cualquier total dependería de dónde se cortó. La diferencia entre "
            "el núcleo y el margen de 1 a 39 años es la expresión espacial de "
            "la superficie con clasificación inestable de la clase beta. La "
            "frecuencia mide años de clasificación, no densidad, biomasa ni "
            "condición ecológica de la vegetación."
        ),
        source_note=(
            "MapBiomas Perú, Colección 3, mapa anual de cobertura y uso del "
            "suelo (1985-2024), 30 m, procesado en Google Earth Engine (paso "
            "12C). Límites del ACR: DS 011-2019-MINAM. Máscara terrestre: INEI "
            "2023. Acceso: agosto de 2026."
        ),
    )
    print(f"{STEM}: {manifest['figure_size_mm']} mm — verificación de trazado "
          f"{'OK' if manifest['layout_check']['passed'] else 'FALLIDA'}")


if __name__ == "__main__":
    main()
