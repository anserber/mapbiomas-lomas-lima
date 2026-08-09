#!/usr/bin/env python3
"""
Maqueta plana de M00 para replicar en el diseñador de impresión de QGIS.

No es el mapa. Es el plano de la página: dibuja la geometría real a escala
dentro del marco previsto y sitúa cada elemento de la composición con sus
coordenadas en milímetros, medidas desde la esquina superior izquierda de la
hoja A4, que es exactamente como QGIS posiciona los objetos del layout.

El área de estudio tiene una relación alto/ancho de 1,78. Un marco de 160 mm de
ancho pediría 285 mm de alto y no cabe en A4 con márgenes. De ahí la columna
lateral: el mapa se estrecha a 117 mm y los elementos de la composición ocupan
los 39 mm que quedan a la derecha, en vez de apilarse debajo.

Run:  python mapa_00_wireframe.py
"""

from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

ROOT = Path(__file__).resolve().parents[3]
OUTDIR = ROOT / "10_comunicacion_resultados/02_final/mapas"
STEM = "mapa_00_wireframe_layout"

ACR = ROOT / "01_limites/02_final/acr_sistema_lomas_5_ambitos_epsg32718.gpkg"
ANILLOS = (ROOT / "02_zonas_influencia/02_final/"
                  "anillos_3_distancias_sistema_periferia_externa_epsg32718.gpkg")

# --- Hoja y caja de texto -------------------------------------------------
PAGINA = (210.0, 297.0)          # A4 vertical
MARGEN = 25.0                    # margen del documento Word
CAJA = (PAGINA[0] - 2 * MARGEN, PAGINA[1] - 2 * MARGEN)   # 160 x 247 mm

# --- Elementos del layout, en mm desde la esquina superior izquierda de A4 -
# (x, y, ancho, alto, rótulo, tipo)
MAPA_W = 117.0
COL_X = MARGEN + MAPA_W + 4.0    # columna lateral
COL_W = CAJA[0] - MAPA_W - 4.0   # 39 mm

ELEMENTOS = [
    ("marco",     MARGEN,  MARGEN,       MAPA_W, 208.3,
     "MARCO DE MAPA\nEPSG:32718\nextensión fija y bloqueada"),
    ("localizador", COL_X, MARGEN,       COL_W,  39.0,
     "LOCALIZADOR\nPerú por deptos.\nLima resaltada\nsin norte ni escala"),
    ("leyenda",   COL_X,   MARGEN + 43,  COL_W,  62.0,
     "LEYENDA\nACR (5 ámbitos)\nanillo 0–500\nanillo 500–1000\nanillo 1000–2000\n+ áreas en ha"),
    ("norte",     COL_X,   MARGEN + 109, COL_W,  22.0,
     "NORTE\n14–16 mm\nflecha simple"),
    ("escala",    COL_X,   MARGEN + 135, COL_W,  20.0,
     "ESCALA\ngráfica en km\n+ numérica"),
    ("nota",      COL_X,   MARGEN + 159, COL_W,  49.3,
     "NOTA\nárea vectorial\nvs. área de grilla\n(< 0,06 %)"),
    ("membrete",  MARGEN,  MARGEN + 212, CAJA[0], 26.0,
     "MEMBRETE Y FUENTES · código MB-LIM-P12-M00 · autor · CRS · software · "
     "SERNANP 2021 · INEI 2023 · [DEM] · uso académico"),
]

IMAGEN_H = 212.0 + 26.0          # alto total de la imagen exportada


def cargar():
    acr = gpd.read_file(ACR)
    anillos = gpd.read_file(ANILLOS)
    x0, y0, x1, y1 = anillos.total_bounds
    mx, my = (x1 - x0) * 0.03, (y1 - y0) * 0.03
    return acr, anillos, (x0 - mx, y0 - my, x1 + mx, y1 + my)


def main():
    acr, anillos, (bx0, by0, bx1, by1) = cargar()
    bw, bh = bx1 - bx0, by1 - by0

    fig = plt.figure(figsize=(PAGINA[0] / 25.4, PAGINA[1] / 25.4))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, PAGINA[0])
    ax.set_ylim(PAGINA[1], 0)          # origen arriba-izquierda, como QGIS
    ax.set_axis_off()

    # Hoja y caja de texto
    ax.add_patch(Rectangle((0, 0), *PAGINA, fc="white", ec="#999999", lw=0.8))
    ax.add_patch(Rectangle((MARGEN, MARGEN), *CAJA, fc="none", ec="#CC0000",
                           lw=0.6, ls=(0, (4, 3))))
    ax.text(MARGEN, MARGEN - 2.5, "caja de texto del Word — 160 × 247 mm",
            fontsize=6.5, color="#CC0000")
    ax.text(PAGINA[0] / 2, 12, "A4 vertical · 210 × 297 mm · márgenes de 25 mm",
            fontsize=8, ha="center", color="#555555")

    # Elementos
    for nombre, x, y, w, h, rotulo in ELEMENTOS:
        es_mapa = nombre == "marco"
        ax.add_patch(Rectangle((x, y), w, h, fc="#F4F4F4" if not es_mapa else "none",
                               ec="#333333", lw=0.9 if es_mapa else 0.6,
                               zorder=3 if es_mapa else 1))
        ax.text(x + w / 2, y + (5.5 if nombre == "membrete" else h / 2), rotulo,
                fontsize=6.2, ha="center",
                va="center" if nombre != "membrete" else "top",
                color="#333333", linespacing=1.5, zorder=4,
                wrap=nombre == "membrete")
        ax.text(x + 0.6, y + 2.6, f"{x:.0f}, {y:.0f} · {w:.0f}×{h:.0f}",
                fontsize=4.8, color="#B03030", zorder=5, family="monospace")

    # Geometría real dentro del marco, a escala
    mx0, my0, mw, mh = MARGEN, MARGEN, MAPA_W, 208.3
    esc = min(mw / bw, mh / bh)
    dx = mx0 + (mw - bw * esc) / 2
    dy = my0 + (mh - bh * esc) / 2

    def proyecta(gdf):
        g = gdf.copy()
        g["geometry"] = g.geometry.translate(-bx0, -by0).scale(
            esc, -esc, origin=(0, 0, 0)).translate(dx, dy + bh * esc)
        return g

    colores = {"1000_2000": "#BCBDDC", "500_1000": "#807DBA", "0_500": "#54278F"}
    for zona in ("1000_2000", "500_1000", "0_500"):
        proyecta(anillos[anillos["zona"] == zona]).plot(
            ax=ax, fc=colores[zona], ec=colores[zona], lw=0.2, alpha=0.45, zorder=3)
    proyecta(acr).plot(ax=ax, fc="#1B7837", ec="#1B7837", lw=0.5,
                       alpha=0.35, zorder=4)

    escala_num = 1 / esc * 1000        # 1 mm de papel = tantos metros
    ax.text(mx0 + 2, my0 + mh - 3,
            f"geometría real a escala ≈ 1:{escala_num:,.0f}".replace(",", " "),
            fontsize=5.6, color="#1B7837", zorder=6)

    OUTDIR.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(OUTDIR / f"{STEM}.{ext}", dpi=300)
    plt.close(fig)

    print(f"relación alto/ancho del área de estudio: {bh / bw:.3f}")
    print(f"escala del marco de {MAPA_W:.0f} mm: 1:{escala_num:,.0f}".replace(",", " "))
    print(f"imagen exportada: {CAJA[0]:.0f} × {IMAGEN_H:.0f} mm\n")
    print("posiciones para el diseñador de QGIS (mm desde la esquina sup. izq.):")
    print(f"  {'elemento':<12} {'x':>6} {'y':>6} {'ancho':>7} {'alto':>7}")
    for nombre, x, y, w, h, _ in ELEMENTOS:
        print(f"  {nombre:<12} {x:>6.1f} {y:>6.1f} {w:>7.1f} {h:>7.1f}")
    print(f"\n  salida en {OUTDIR}")


if __name__ == "__main__":
    main()
