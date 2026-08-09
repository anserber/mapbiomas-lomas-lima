#!/usr/bin/env python3
"""
CONTRACT     : F01
QUESTION     : ¿Cómo varió el porcentaje del área de grilla clasificado como
               clase 70 — Loma costera en cada uno de los cinco ámbitos del ACR
               Sistema de Lomas de Lima entre 1986 y 2024, y bajo qué régimen de
               sensor Landsat se produjo cada tramo de esa variación?
MESSAGE      : Las trayectorias presentan oscilaciones de gran amplitud durante
               los regímenes de Landsat 5 y de mezcla de sensores, y se
               estabilizan bajo Landsat 8. La amplitud es muy desigual entre
               ámbitos: Ancón y Carabayllo 2 varían decenas de puntos, mientras
               Carabayllo 1 y Amancaes permanecen casi planos. El año 1985 queda
               fuera de la serie por ruptura de inicio de serie documentada.
SOURCE       : 04_extraccion_series/02_resultados/00_raw/
               serie_indicadores_acr_1985_2024.csv
UNIT         : porcentaje del área de grilla del ámbito, por año
INCLUDES     : cinco ámbitos del ACR; años 1986-2024
EXCLUDES     : 1985, dibujado como punto abierto fuera de la trayectoria porque
               el mosaico de ese año se construyó con 17 escenas Landsat y 58 %
               de nubosidad media, los peores valores de los 38 años
               comparables (control 6E4 y 6E5). Anillos externos y KBA
               restringida quedan fuera del alcance de esta figura.
PROHIBITIONS : no describir las variaciones como pérdida o recuperación
               ecológica; no comparar años de regímenes de sensor distintos sin
               declarar esa condición; no unir 1985 a la línea de la serie.
VISUAL FORM  : small multiples, cinco paneles de líneas con escala vertical
               común 0-100 %, con bandas de fondo por régimen de sensor.
               Escala común porque el mensaje incluye la comparación del nivel
               entre ámbitos, no solo de su forma.
LIMIT        : persistencia cartográfica de una clase beta, no condición
               ecológica ni presencia de vegetación.
OUTPUT       : figura_01_serie_clase70_acr_1986_2024

Run:  python figura_01_serie_clase70.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sciviz
from sciviz import OKABE_ITO

# ---------------------------------------------------------------- paths ----
ROOT = Path(__file__).resolve().parents[3]
SOURCE = (ROOT / "04_extraccion_series/02_resultados/00_raw/"
                 "serie_indicadores_acr_1985_2024.csv")
OUTDIR = ROOT / "10_comunicacion_resultados/02_final/figuras"
STEM = "figura_01_serie_clase70_acr_1986_2024"

LANG = "es"
FORMATS = ("pdf", "png")

YEAR_MIN, YEAR_MAX = 1986, 2024
YEAR_EXCLUIDO = 1985

# Orden de paneles por superficie descendente: el ámbito dominante primero.
# Ordenar alfabéticamente obligaría al lector a reconstruir el peso de cada uno.
AMBITOS = [
    ("ancon",        "Ancón",        12160.4),
    ("villa_maria",  "Villa María",    627.6),
    ("amancaes",     "Amancaes",       253.8),
    ("carabayllo_1", "Carabayllo 1",   228.8),
    ("carabayllo_2", "Carabayllo 2",   198.2),
]

# Regímenes de sensor del mosaico oficial (control 6E5).
REGIMENES = [
    (1986, 1999, "I"),
    (2000, 2013, "II"),
    (2014, 2024, "III"),
]
YEAR_CAMBIO_VERSION = 2022.5  # v4 -> v5 del mosaico

# Base distinta de cero. El mínimo observado en 1986-2024 es 22,1 % (Ancón), de
# modo que la franja 0-15 % está vacía en los cinco paneles. Es admisible porque
# la marca es una línea, que codifica posición y no longitud; se declara en el pie.
YLIM = (15, 100)

C_LINEA = OKABE_ITO["blue"]
C_EXCLUIDO = OKABE_ITO["vermillion"]
C_BANDA = "#F0F0F0"


# ---------------------------------------------------- input assertions -----
def load() -> pd.DataFrame:
    df = pd.read_csv(SOURCE)
    faltan = {"id_ambito", "year", "loma_pct_ambito"} - set(df.columns)
    if faltan:
        raise SystemExit(f"la fuente no trae las columnas: {sorted(faltan)}")

    df["year"] = df["year"].astype(float).astype(int)
    df = df[["id_ambito", "year", "loma_pct_ambito"]].copy()

    for aid, _, _ in AMBITOS:
        años = sorted(df.loc[df["id_ambito"] == aid, "year"])
        if años != list(range(1985, 2025)):
            raise SystemExit(f"{aid}: se esperaban 40 años completos 1985-2024")
    if df["loma_pct_ambito"].isna().any():
        raise SystemExit("hay NaN en loma_pct_ambito; deben mostrarse, no caer en silencio")
    return df


# ------------------------------------------------------------- drawing -----
def build(df: pd.DataFrame):
    fig, axes = sciviz.new_panel_grid(
        len(AMBITOS), 1, width="a4text", panel_h_mm=20.0,
        sharex=True, sharey=True,
    )

    for i, (aid, nombre, area_ha) in enumerate(AMBITOS):
        ax = axes[i]
        d = df[df["id_ambito"] == aid].sort_values("year")
        serie = d[(d["year"] >= YEAR_MIN) & (d["year"] <= YEAR_MAX)]
        excluido = d[d["year"] == YEAR_EXCLUIDO]

        # Régimen II sombreado y fronteras marcadas: sombrear alternando dejaba
        # I y III en blanco, indistinguibles del fondo.
        ax.axvspan(REGIMENES[1][0] - 0.5, REGIMENES[1][1] + 0.5,
                   color=C_BANDA, zorder=0)
        for frontera in (REGIMENES[1][0] - 0.5, REGIMENES[2][0] - 0.5):
            ax.axvline(frontera, color="#BBBBBB", linewidth=0.5, zorder=1)

        ax.axvline(YEAR_CAMBIO_VERSION, color="#999999", linewidth=0.6,
                   linestyle=(0, (3, 2)), zorder=1)

        ax.plot(serie["year"], serie["loma_pct_ambito"],
                color=C_LINEA, linewidth=1.1, zorder=3, solid_capstyle="round")
        # 1985 desconectado de la trayectoria: visible, pero no forma parte de ella.
        ax.plot(excluido["year"], excluido["loma_pct_ambito"],
                marker="o", markersize=3.2, markerfacecolor="white",
                markeredgecolor=C_EXCLUIDO, markeredgewidth=0.9,
                linestyle="none", zorder=4)

        # Base distinta de cero: legítima en líneas, que codifican posición y no
        # longitud. El mínimo de la serie es 22,1 %. Se declara en el pie.
        ax.set_ylim(YLIM)
        ax.set_yticks([25, 50, 75, 100])
        ax.set_xlim(1983.5, 2025.5)

        # La etiqueta va sobre el panel, fuera del área de datos: dentro se
        # sentaba encima de la línea en Villa María, Amancaes y Carabayllo 2.
        etiqueta = f"({chr(97 + i)}) {nombre} · {area_ha:,.0f} ha".replace(",", " ")
        ax.set_title(etiqueta, loc="left", fontsize=sciviz.pt(0.95),
                     fontweight="bold", pad=2.0)

        ax.grid(axis="y", linewidth=0.4, color="#DDDDDD")
        ax.set_axisbelow(False)
        for lado in ("top", "right"):
            ax.spines[lado].set_visible(False)

    # Rótulos de régimen: una sola vez, en la franja alta del panel de Ancón,
    # que es la única zona libre de dato en todos los paneles.
    top = axes[0]
    for y0, y1, rom in REGIMENES:
        top.text((y0 + y1) / 2, 93, rom, ha="center", va="top",
                 fontsize=sciviz.pt(0.9), color="#666666")

    # El punto excluido se identifica una sola vez y sin flecha: la etiqueta se
    # coloca a su derecha, a la misma altura, en una zona sin dato.
    top.text(1986.6, 25.4, "excluido", fontsize=sciviz.pt(0.85),
             color=C_EXCLUIDO, ha="left", va="center")

    axes[-1].set_xticks(range(1985, 2025, 5))
    axes[-1].set_xlabel("Año")
    # Rótulo del eje en el panel central, no con supylabel: el verificador
    # trata los rótulos `sup*` como prosa de manuscrito y rechaza la exportación.
    axes[len(AMBITOS) // 2].set_ylabel("Clase 70 — Loma costera\n(% del área de grilla)")

    return fig


# ---------------------------------------------------------------- main -----
def main():
    df = load()
    fig = build(df)

    manifest = sciviz.finalize(
        fig,
        outdir=OUTDIR,
        stem=STEM,
        contract="F01",
        source=SOURCE,
        lang=LANG,
        formats=FORMATS,
        caption=(
            "Superficie clasificada como clase 70 — Loma costera, expresada como "
            "porcentaje del área de grilla de cada ámbito del ACR Sistema de Lomas "
            "de Lima, 1986-2024. Los paneles comparten la escala vertical y se "
            "ordenan por superficie descendente. Las bandas de fondo separan los "
            "tres regímenes de sensor del mosaico oficial: I, Landsat 5 "
            "(hasta 1999); II, mezcla de Landsat 5, 7 y compuestos mixtos "
            "(2000-2013); III, Landsat 8 y 9 (2014-2024). La línea vertical "
            "discontinua marca el cambio de la versión 4 a la versión 5 del "
            "mosaico, en 2023."
        ),
        note=(
            "n = 39 años por ámbito (1986-2024); 5 ámbitos. El punto abierto en "
            "1985 se muestra fuera de la trayectoria: el mosaico de ese año se "
            "construyó con 17 escenas Landsat y 58 % de nubosidad media, los "
            "peores valores de los 38 años comparables, y subdetecta un 29,3 % de "
            "la clase 70 del conjunto del ACR. Por ese motivo 1985 se excluye de "
            "todo cálculo de cambio y de la línea base. La desviación estándar del "
            "residual interanual del ACR, calculada sin apoyarse en 1985, es de "
            "35,7 ha en el régimen I (1987-1999), 129,2 ha en el II (2000-2013) "
            "y 10,8 ha en el III (2014-2022). La clase 70 "
            "es un producto beta: las variaciones representan persistencia y "
            "transición cartográficas, no pérdida ni recuperación ecológica "
            "demostrada."
        ),
        source_note=(
            "MapBiomas Perú, Colección 3, mapa anual de cobertura y uso del suelo "
            "(1985-2024), 30 m. Serie extraída en Google Earth Engine y validada "
            "en el paso 5 del protocolo. Archivo: "
            "serie_indicadores_acr_1985_2024.csv. Acceso: agosto de 2026."
        ),
    )
    print(f"{STEM}: {manifest['figure_size_mm']} mm — verificación de trazado "
          f"{'OK' if manifest['layout_check']['passed'] else 'FALLIDA'}")


if __name__ == "__main__":
    main()
