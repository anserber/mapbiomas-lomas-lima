#!/usr/bin/env python3
"""
CONTRACT     : M02
QUESTION     : ¿En qué sectores concretos del ACR Sistema de Lomas de Lima y su
               periferia se localizan las salidas de la clase 70 hacia clase 24 —
               Infraestructura urbana, distinguiendo las confirmadas por la
               ventana W5 de las recientes todavía censuradas?
MESSAGE      : La señal se concentra en tres sectores del sur y del centro. Villa
               María reúne señal confirmada y reciente; Amancaes, sobre todo
               reciente; y Carabayllo 1 registra 197 candidatos recientes y
               ninguna confirmación. Ancón, que aporta el 90 % de la superficie
               del ACR, no registra un solo píxel de ninguna de las dos señales.
SOURCE       : 10_comunicacion_resultados/01_intermediate/rasteres/
               huella_urbana_70_24.tif (paso 12C)
               persistencia_clase70_frecuencia_1985_2024.tif (contexto)
               01_limites/02_final/acr_sistema_lomas_5_ambitos_epsg32718.gpkg
               02_zonas_influencia/02_final/
               anillos_3_distancias_sistema_periferia_externa_epsg32718.gpkg
UNIT         : superficie de píxel de 30 m con la señal correspondiente
INCLUDES     : tres sectores de 7,5 x 7,5 km centrados en el foco de señal de
               Villa María, Amancaes y Carabayllo 1, que reúnen el 90 % de la
               señal del ámbito de estudio.
EXCLUDES     : los sectores de Ancón y Carabayllo 2, con 0 y 4 píxeles. Su
               ausencia se declara en el pie, no se oculta. KBA restringida.
PROHIBITIONS : no sumar ni fundir las dos señales en una sola categoría de
               cambio; no atribuir causa, legalidad ni responsabilidad a una
               transición cartográfica hacia la clase 24.
VISUAL FORM  : multipanel coordinado con extensión, escala, clases y leyenda
               idénticas. Se descarta el mapa de extensión completa: la señal
               ocupa el 0,048 % del lienzo del paso 12C y a 160 mm de ancho un
               píxel de 30 m mide 0,14 mm, de modo que no habría tinta para
               verla. A 7,5 km por panel el píxel mide unos 0,3 mm.
LIMIT        : la huella dibuja superficie única, mientras la tabla maestra suma
               hectáreas-evento; un píxel con dos eventos en años distintos
               cuenta dos veces en la tabla y una sola en el mapa.
OUTPUT       : mapa_02_huella_urbana_sectores

Requiere: geopandas, rasterio.

Run:  python mapa_02_huella_urbana.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch, Rectangle
import numpy as np

import geopandas as gpd
from shapely.geometry import box
import rasterio

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sciviz
from sciviz import OKABE_ITO, MM

# ---------------------------------------------------------------- paths ----
ROOT = Path(__file__).resolve().parents[3]
RAS = ROOT / "10_comunicacion_resultados/01_intermediate/rasteres"
HUELLA = RAS / "huella_urbana_70_24.tif"
PERSIST = RAS / "persistencia_clase70_frecuencia_1985_2024.tif"
ACR = ROOT / "01_limites/02_final/acr_sistema_lomas_5_ambitos_epsg32718.gpkg"
ANILLOS = (ROOT / "02_zonas_influencia/02_final/"
                  "anillos_3_distancias_sistema_periferia_externa_epsg32718.gpkg")
OUTDIR = ROOT / "10_comunicacion_resultados/02_final/mapas"
STEM = "mapa_02_huella_urbana_sectores"

LANG = "es"
FORMATS = ("pdf", "png")

CRS_MAPA = "EPSG:32718"
CRS_ETIQUETA = "WGS 84 / UTM 18S (EPSG:32718)"

# Lado común del recuadro. La mayor envolvente de señal es la de Villa María,
# 6,96 x 6,15 km: 7,5 km la cubre con margen y mantiene los tres paneles con
# extensión y escala idénticas, que es lo que permite comparar tamaños.
LADO_M = 7500.0

# Centro del foco de señal de cada sector, medido sobre el propio ráster.
SECTORES = [
    ("villa_maria",  "Villa María",  (289860, 8656845)),
    ("amancaes",     "Amancaes",     (278400, 8672775)),
    ("carabayllo_1", "Carabayllo 1", (272025, 8693640)),
]
SIN_SENAL = ["Ancón", "Carabayllo 2"]

# Mismos colores que F07 para las mismas dos variables.
C_W5 = OKABE_ITO["blue"]
C_CENSURA = OKABE_ITO["orange"]
C_NUCLEO = "#C9DFC6"
C_TIERRA = "#F5F2ED"


# ---------------------------------------------------- input assertions -----
def load():
    with rasterio.open(HUELLA) as s:
        huella = s.read(1)
        ext = (s.bounds.left, s.bounds.right, s.bounds.bottom, s.bounds.top)
        crs = s.crs.to_string()
    with rasterio.open(PERSIST) as s:
        persist = s.read(1)
        if (s.bounds.left, s.bounds.right, s.bounds.bottom,
                s.bounds.top) != ext:
            raise SystemExit("los dos ráster no comparten extensión")
    if crs != CRS_MAPA:
        raise SystemExit(f"el ráster está en {crs}, se esperaba {CRS_MAPA}")
    if set(np.unique(huella)) - {0, 1, 2}:
        raise SystemExit("la huella debe ser categórica 0, 1 y 2")

    acr = gpd.read_file(ACR).to_crs(CRS_MAPA)
    anillos = gpd.read_file(ANILLOS).to_crs(CRS_MAPA)

    # Control: los tres sectores deben reunir el 90 % de la señal del ráster.
    total = int((huella > 0).sum())
    dentro = 0
    for aid, _, (cx, cy) in SECTORES:
        dentro += int(recorte(huella, ext, cx, cy).astype(bool).sum())
    if dentro / total < 0.85:
        raise SystemExit(f"los tres sectores solo cubren {100*dentro/total:.0f} % "
                         f"de la señal; revisar los centros")
    print(f"  señal total: {total} px | en los tres sectores: {dentro} px "
          f"({100*dentro/total:.0f} %)")
    return huella, persist, ext, acr, anillos


def recorte(arr, ext, cx, cy):
    """Subconjunto del arreglo dentro del recuadro centrado en (cx, cy)."""
    x0, x1, y0, y1 = ext
    res = 30.0
    j0 = int((cx - LADO_M / 2 - x0) / res)
    j1 = int((cx + LADO_M / 2 - x0) / res)
    i0 = int((y1 - (cy + LADO_M / 2)) / res)
    i1 = int((y1 - (cy - LADO_M / 2)) / res)
    return arr[max(i0, 0):i1, max(j0, 0):j1]


# ------------------------------------------------------------- drawing -----
def build(huella, persist, ext, acr, anillos):
    w_mm = sciviz.WIDTHS["a4text"]
    fig, axes = plt.subplots(2, 2, figsize=(w_mm * MM, 172 * MM),
                             layout="constrained")
    fig.get_layout_engine().set(w_pad=1.5 * MM, h_pad=1.5 * MM,
                                hspace=0.04, wspace=0.04)
    planos = axes.ravel()

    nucleo = np.ma.masked_where(persist != 40, persist)
    w5 = np.ma.masked_where(huella != 1, huella)
    cen = np.ma.masked_where(huella != 2, huella)

    # Velo de contexto, igual que en M01. El recuadro de exportación excede el
    # ACR y su periferia de 2 km, y dentro de un panel de 7,5 km el lector no
    # tiene forma de saber dónde termina el ámbito medido. Se subordina todo lo
    # exterior sin ocultarlo. Va por encima de las dos señales: una señal fuera
    # del ámbito tampoco está medida, y no puede destacar como si lo estuviera.
    ambito = gpd.GeoSeries(
        [acr.union_all().union(anillos.union_all())], crs=acr.crs)
    # `ext` viene en el orden de imshow (x0, x1, y0, y1); shapely.box pide
    # (minx, miny, maxx, maxy).
    fuera = gpd.GeoSeries([box(ext[0], ext[2], ext[1], ext[3])],
                          crs=acr.crs).difference(ambito, align=False)

    for k, (aid, nombre, (cx, cy)) in enumerate(SECTORES):
        ax = planos[k]
        ax.set_facecolor(C_TIERRA)
        ax.imshow(nucleo, extent=ext, origin="upper",
                  cmap=ListedColormap([C_NUCLEO]), interpolation="nearest",
                  zorder=1)
        ax.imshow(cen, extent=ext, origin="upper",
                  cmap=ListedColormap([C_CENSURA]), interpolation="nearest",
                  zorder=4)
        ax.imshow(w5, extent=ext, origin="upper",
                  cmap=ListedColormap([C_W5]), interpolation="nearest",
                  zorder=5)
        fuera.plot(ax=ax, facecolor="white", edgecolor="none", alpha=0.55,
                   zorder=6)
        anillos.dissolve().boundary.plot(ax=ax, edgecolor="#8C8C8C",
                                         linewidth=0.5, linestyle=(0, (4, 2)),
                                         zorder=7)
        acr.boundary.plot(ax=ax, edgecolor="#1A1A1A", linewidth=0.9, zorder=8)

        h = recorte(huella, ext, cx, cy)
        n_w5, n_cen = int((h == 1).sum()), int((h == 2).sum())
        ax.set_title(f"({chr(97 + k)}) {nombre}", loc="left",
                     fontsize=sciviz.pt(0.95), fontweight="bold", pad=2.0)
        ax.text(0.03, 0.03, f"W5 {n_w5 * 0.09:.1f} ha · reciente "
                            f"{n_cen * 0.09:.1f} ha".replace(".", ","),
                transform=ax.transAxes, ha="left", va="bottom",
                fontsize=sciviz.pt(0.8), zorder=20,
                path_effects=[pe.withStroke(linewidth=2.0, foreground="white")])

        ax.set_xlim(cx - LADO_M / 2, cx + LADO_M / 2)
        ax.set_ylim(cy - LADO_M / 2, cy + LADO_M / 2)
        ax.set_aspect("equal")
        ax.set_xticks([]); ax.set_yticks([])
        for lado in ax.spines.values():
            lado.set_linewidth(0.6)

    sciviz.add_scalebar(planos[0], 2000, location=(0.055, 0.135), segments=2)
    sciviz.add_north_arrow(planos[0], location=(0.93, 0.90), size_frac=0.10,
                           fontsize=sciviz.pt(1.2))

    # Cuarta celda: localizador con los tres recuadros sobre el ámbito completo.
    ax_loc = planos[3]
    ax_loc.set_facecolor("white")
    ax_loc.imshow(nucleo, extent=ext, origin="upper",
                  cmap=ListedColormap([C_NUCLEO]), interpolation="nearest",
                  zorder=1)
    acr.boundary.plot(ax=ax_loc, edgecolor="#1A1A1A", linewidth=0.5, zorder=3)
    for k, (aid, nombre, (cx, cy)) in enumerate(SECTORES):
        ax_loc.add_patch(Rectangle((cx - LADO_M / 2, cy - LADO_M / 2),
                                   LADO_M, LADO_M, facecolor="none",
                                   edgecolor="#D55E00", linewidth=0.8, zorder=6))
        ax_loc.text(cx - LADO_M * 0.62, cy, f"({chr(97 + k)})", ha="right",
                    va="center", fontsize=sciviz.pt(0.85), color="#D55E00",
                    zorder=7)
    ax_loc.set_xlim(ext[0], ext[1]); ax_loc.set_ylim(ext[2], ext[3])
    ax_loc.set_aspect("equal")
    ax_loc.set_xticks([]); ax_loc.set_yticks([])
    ax_loc.set_title("(d) Situación de los sectores", loc="left",
                     fontsize=sciviz.pt(0.95), fontweight="bold", pad=2.0)


    # El SRC va en el ángulo libre del panel (c): el localizador es demasiado
    # estrecho para contener la cadena sin desbordarse.
    planos[2].text(0.97, 0.97, CRS_ETIQUETA, transform=planos[2].transAxes,
                   ha="right", va="top", fontsize=sciviz.pt(0.75),
                   color="#555555", zorder=20,
                   path_effects=[pe.withStroke(linewidth=2.0,
                                               foreground="white")])

    manijas = [
        Patch(facecolor=C_W5, edgecolor="none",
              label="Salida 70 → 24 confirmada, W5 1990–2020"),
        Patch(facecolor=C_CENSURA, edgecolor="none",
              label="Salida 70 → 24 reciente censurada, 2021–2024"),
        Patch(facecolor=C_NUCLEO, edgecolor="none",
              label="Núcleo persistente de clase 70"),
        plt.Line2D([], [], color="#1A1A1A", linewidth=0.9,
                   label="Ámbitos del ACR"),
        plt.Line2D([], [], color="#8C8C8C", linewidth=0.5, linestyle=(0, (4, 2)),
                   label="Periferia externa, 2 km"),
    ]
    fig.legend(handles=manijas, loc="outside lower center", ncol=2,
               frameon=False, fontsize=sciviz.pt(0.8), handlelength=1.2,
               handleheight=0.9, labelspacing=0.4, columnspacing=1.4)

    return fig


# ---------------------------------------------------------------- main -----
def main():
    huella, persist, ext, acr, anillos = load()
    fig = build(huella, persist, ext, acr, anillos)

    manifest = sciviz.finalize(
        fig, outdir=OUTDIR, stem=STEM, contract="M02",
        source=[HUELLA, PERSIST, ACR, ANILLOS], lang=LANG, formats=FORMATS,
        caption=(
            "Salidas de la clase 70 — Loma costera hacia la clase 24 — "
            "Infraestructura urbana en los tres sectores del ACR Sistema de "
            "Lomas de Lima que concentran la señal, 1990-2024. Los paneles (a) a "
            "(c) comparten extensión de 7,5 por 7,5 kilómetros, escala, clases y "
            "leyenda, de modo que las superficies son comparables entre ellos. "
            "El panel (d) sitúa los tres recuadros sobre el conjunto del área de "
            "estudio. Las dos señales se representan por separado y nunca "
            "fundidas en una sola categoría. La superficie exterior al ACR y a "
            "su periferia de 2 km se atenúa con un velo blanco: sigue visible "
            "como contexto, pero no forma parte del ámbito medido."
        ),
        note=(
            "n = 3 sectores de 5 626 ha cada uno, que reúnen el 90 % de la señal "
            "urbana detectada en el área exportada. La señal confirmada W5 corresponde a "
            "transiciones que permanecen en clase 24 durante el año del evento y "
            "los cuatro siguientes, con ventana completa entre 1990 y 2020. La "
            "señal reciente corresponde a salidas registradas entre 2021 y 2024, "
            "que no pueden completar esa ventana antes del final de la serie y "
            "cuya confianza es media según la validación visual ciega. Los "
            "recuadros de Ancón y Carabayllo 2 no se representan. El primero "
            "contiene 0 píxeles y el segundo 4 píxeles de señal reciente censurada, "
            "todos situados fuera del polígono de Carabayllo 2; por ello, ambas "
            "unidades registran cero en la Tabla 5. Ancón aporta el 90 % de la "
            "superficie del ACR y no presenta ninguna de las dos señales dentro "
            "de su polígono. Carabayllo 1 "
            "registra candidatos recientes y ninguna confirmación. Las "
            "superficies del mapa son superficie única y por ello resultan algo "
            "menores que las hectáreas-evento de la tabla maestra, que cuentan "
            "dos veces un píxel con dos eventos en años distintos. Una "
            "transición hacia la clase 24 no demuestra por sí sola ocupación "
            "ilegal, invasión ni incumplimiento normativo."
        ),
        source_note=(
            "MapBiomas Perú, Colección 3, mapa anual de cobertura y uso del "
            "suelo y mapa oficial de transiciones (1985-2024), 30 m, procesado "
            "en Google Earth Engine (paso 12C). Límites del ACR: DS "
            "011-2019-MINAM. Acceso: agosto de 2026."
        ),
    )
    print(f"{STEM}: {manifest['figure_size_mm']} mm — verificación de trazado "
          f"{'OK' if manifest['layout_check']['passed'] else 'FALLIDA'}")


if __name__ == "__main__":
    main()
