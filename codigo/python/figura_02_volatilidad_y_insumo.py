#!/usr/bin/env python3
"""
CONTRACT     : F02 (absorbe el contrato F03 como paneles b y c)
QUESTION     : ¿Cómo varía la estabilidad interanual de la clase 70 — Loma
               costera según el régimen de sensor del mosaico oficial, y explica
               esa inestabilidad la cantidad de observaciones Landsat
               disponibles?
MESSAGE      : La inestabilidad no depende de la antigüedad de la serie sino de
               la heterogeneidad del sensor: el régimen de mezcla Landsat 5/7
               (2000-2013) es 3,6 veces más volátil que Landsat 5 solo y 12
               veces más que Landsat 8 solo. El número de escenas no acompaña esa
               variación, salvo en 1985, el peor año de insumo de la serie, que
               por eso se excluye.
SOURCE       : 04_extraccion_series/02_resultados/00_raw/
               serie_indicadores_acr_1985_2024.csv  (residual)
               control 6E5, paso06E5_auditoria_insumo_landsat_1985_2024.js
               (escenas y nubosidad, transcritas en INSUMO)
UNIT         : (a) hectáreas de residual local; (b) número de escenas Landsat;
               (c) porcentaje de nubosidad media declarada por el mosaico
INCLUDES     : ACR completo, suma de los cinco ámbitos.
               (a) 1987-2023, que es donde el residual local puede calcularse
               sin usar 1985 como vecino.
               (b) y (c) 1985-2022, años de mosaico versión 4.
EXCLUDES     : 1985 como valor de la serie de cobertura, por ruptura de inicio
               documentada. 2023-2024 en los paneles b y c, porque el mosaico
               pasa a versión 5 con etiqueta de satélite `ly` y el recuento de
               escenas responde a otra convención: 515 y 236 escenas frente a
               una media de 89. No son comparables y no se dibujan.
PROHIBITIONS : no presentar la correlación entre insumo y residual como
               explicación general — fue contrastada y descartada (Pearson
               -0,226; Spearman -0,104; +0,053 sin 1986); no describir el
               residual como pérdida o ganancia ecológica; no usar doble eje.
VISUAL FORM  : tres paneles apilados con eje temporal compartido. El residual
               como tallos desde cero con bandas horizontales de ±1 DE por
               régimen — la banda que se estrecha es el mensaje. Paneles
               separados en vez de doble eje: tres unidades distintas.
LIMIT        : el residual local mide desviación respecto de los años vecinos,
               no error frente a una verdad de campo.
OUTPUT       : figura_02_volatilidad_regimen_e_insumo

Run:  python figura_02_volatilidad_y_insumo.py
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
from sciviz import OKABE_ITO, MM

# ---------------------------------------------------------------- paths ----
ROOT = Path(__file__).resolve().parents[3]
SOURCE = (ROOT / "04_extraccion_series/02_resultados/00_raw/"
                 "serie_indicadores_acr_1985_2024.csv")
OUTDIR = ROOT / "10_comunicacion_resultados/02_final/figuras"
STEM = "figura_02_volatilidad_regimen_e_insumo"

LANG = "es"
FORMATS = ("pdf", "png")

AMBITOS = ["amancaes", "ancon", "carabayllo_1", "carabayllo_2", "villa_maria"]

# Regímenes de sensor. El régimen I arranca en 1987 y no en 1986: el residual
# de 1986 necesitaría a 1985 como vecino, y 1985 está excluido de la serie.
REGIMENES = [
    ("I",   1987, 1999, "Landsat 5"),
    ("II",  2000, 2013, "mezcla L5/L7"),
    ("III", 2014, 2022, "Landsat 8/9"),
]
YEAR_CAMBIO_VERSION = 2022.5
XLIM = (1983.5, 2025.5)

# Auditoría de insumo del control 6E5, mosaicos versión 4 (1985-2022).
# year: (escenas totales, nubosidad media %)
INSUMO = {
    1985: (17, 58), 1986: (48, 48), 1987: (74, 47), 1988: (96, 53),
    1989: (61, 46), 1990: (78, 45), 1991: (85, 45), 1992: (95, 49),
    1993: (89, 52), 1994: (58, 51), 1995: (83, 49), 1996: (104, 48),
    1997: (64, 49), 1998: (49, 44), 1999: (93, 44), 2000: (96, 46),
    2001: (81, 42), 2002: (77, 44), 2003: (95, 52), 2004: (95, 36),
    2005: (102, 40), 2006: (86, 42), 2007: (73, 44), 2008: (99, 40),
    2009: (113, 48), 2010: (108, 46), 2011: (102, 50), 2012: (108, 50),
    2013: (87, 52), 2014: (101, 36), 2015: (138, 48), 2016: (89, 40),
    2017: (94, 38), 2018: (112, 36), 2019: (70, 30), 2020: (80, 28),
    2021: (98, 36), 2022: (94, 34),
}
YEAR_INSUMO_MAX = 2022

C_RESID = OKABE_ITO["blue"]
C_DESTACADO = OKABE_ITO["vermillion"]
C_BANDA_DE = "#CFE3F2"
C_BARRA = "#8FB8D6"


# ---------------------------------------------------- input assertions -----
def load() -> pd.DataFrame:
    df = pd.read_csv(SOURCE)
    faltan = {"id_ambito", "year", "loma_ha"} - set(df.columns)
    if faltan:
        raise SystemExit(f"la fuente no trae las columnas: {sorted(faltan)}")
    df["year"] = df["year"].astype(float).astype(int)
    if df["loma_ha"].isna().any():
        raise SystemExit("hay NaN en loma_ha")

    tot = (df[df["id_ambito"].isin(AMBITOS)]
           .groupby("year")["loma_ha"].sum().sort_index())
    if list(tot.index) != list(range(1985, 2025)):
        raise SystemExit("se esperaban 40 años completos 1985-2024")

    # Residual local: desviación respecto de la media de los años vecinos.
    # Solo 1987-2023 es calculable sin apoyarse en 1985.
    años = list(range(1987, 2024))
    resid = pd.Series(
        {y: tot[y] - (tot[y - 1] + tot[y + 1]) / 2 for y in años},
        name="residual_ha",
    )
    return resid


def desviaciones(resid: pd.Series) -> dict[str, float]:
    de = {}
    for rom, y0, y1, _ in REGIMENES:
        v = resid.loc[(resid.index >= y0) & (resid.index <= y1)]
        de[rom] = float(np.std(v.values))
    return de


# ------------------------------------------------------------- drawing -----
def build(resid: pd.Series, de: dict[str, float]):
    w_mm = sciviz.WIDTHS["a4text"]
    fig, axes = plt.subplots(
        3, 1, figsize=(w_mm * MM, 118 * MM), layout="constrained",
        sharex=True, gridspec_kw={"height_ratios": [1.75, 1.0, 1.0]},
    )
    fig.get_layout_engine().set(w_pad=1.5 * MM, h_pad=1.5 * MM, hspace=0.03)
    ax_r, ax_n, ax_c = axes

    # ---- (a) residual local con bandas de ±1 DE por régimen ---------------
    for rom, y0, y1, _ in REGIMENES:
        s = de[rom]
        ax_r.add_patch(plt.Rectangle(
            (y0 - 0.5, -s), (y1 - y0 + 1), 2 * s,
            facecolor=C_BANDA_DE, edgecolor="none", zorder=0))
        # Régimen y desviación en una sola cadena: en dos líneas se solapaban.
        ax_r.text((y0 + y1) / 2, 275, f"{rom} · DE {s:.1f} ha".replace(".", ","),
                  ha="center", va="top", fontsize=sciviz.pt(0.85),
                  color="#555555")

    # Fronteras entre regímenes: inicio de II e inicio de III.
    for _, y0, _, _ in REGIMENES[1:]:
        ax_r.axvline(y0 - 0.5, color="#BBBBBB", linewidth=0.5, zorder=1)

    ax_r.axhline(0, color="black", linewidth=0.6, zorder=2)
    ax_r.vlines(resid.index, 0, resid.values, color=C_RESID, linewidth=0.9,
                zorder=3)
    ax_r.plot(resid.index, resid.values, "o", markersize=2.2, color=C_RESID,
              zorder=4)
    ax_r.set_ylim(-300, 335)
    ax_r.set_yticks([-200, 0, 200])
    ax_r.set_ylabel("Residual local\nde la clase 70 (ha)")
    ax_r.set_title("(a)", loc="left", fontsize=sciviz.pt(0.95),
                   fontweight="bold", pad=2.0)

    # ---- (b) escenas Landsat ---------------------------------------------
    años = sorted(INSUMO)
    n_esc = [INSUMO[y][0] for y in años]
    nubes = [INSUMO[y][1] for y in años]
    colores = [C_DESTACADO if y == 1985 else C_BARRA for y in años]

    ax_n.bar(años, n_esc, width=0.72, color=colores, zorder=3)
    ax_n.set_ylim(0, 150)
    ax_n.set_yticks([0, 50, 100, 150])
    ax_n.set_ylabel("Escenas Landsat\ndel mosaico (n)")
    ax_n.set_title("(b)", loc="left", fontsize=sciviz.pt(0.95),
                   fontweight="bold", pad=2.0)
    # Valor rotulado sobre la propia barra: el conector cruzaba tres barras.
    ax_n.text(1985, 22, "17", ha="center", va="bottom",
              fontsize=sciviz.pt(0.85), color=C_DESTACADO)

    # ---- (c) nubosidad ----------------------------------------------------
    ax_c.bar(años, nubes, width=0.72, color=colores, zorder=3)
    ax_c.set_ylim(0, 70)
    ax_c.set_yticks([0, 25, 50])
    ax_c.set_ylabel("Nubosidad media\ndel mosaico (%)")
    ax_c.set_title("(c)", loc="left", fontsize=sciviz.pt(0.95),
                   fontweight="bold", pad=2.0)
    ax_c.text(1985, 60, "58", ha="center", va="bottom",
              fontsize=sciviz.pt(0.85), color=C_DESTACADO)
    ax_c.set_xlabel("Año")

    # Los años de mosaico versión 5 no son comparables: se marca el vacío en
    # vez de dibujar valores de otra convención sobre la misma escala.
    for ax in (ax_n, ax_c):
        ax.axvspan(YEAR_INSUMO_MAX + 0.5, XLIM[1], color="#EEEEEE", zorder=0)
    ax_n.text(2023.6, 132, "v5", ha="center", va="top",
              fontsize=sciviz.pt(0.8), color="#777777")

    for ax in axes:
        ax.axvline(YEAR_CAMBIO_VERSION, color="#999999", linewidth=0.6,
                   linestyle=(0, (3, 2)), zorder=1)
        ax.set_xlim(*XLIM)
        ax.grid(axis="y", linewidth=0.4, color="#DDDDDD")
        ax.set_axisbelow(True)
        for lado in ("top", "right"):
            ax.spines[lado].set_visible(False)

    ax_c.set_xticks(range(1985, 2025, 5))
    return fig


# ---------------------------------------------------------------- main -----
def main():
    resid = load()
    de = desviaciones(resid)
    for rom, y0, y1, _ in REGIMENES:
        n = int(((resid.index >= y0) & (resid.index <= y1)).sum())
        print(f"  régimen {rom:3s} {y0}-{y1}  n={n:2d}  DE={de[rom]:7.1f} ha")

    fig = build(resid, de)

    manifest = sciviz.finalize(
        fig,
        outdir=OUTDIR,
        stem=STEM,
        contract="F02",
        source=SOURCE,
        lang=LANG,
        formats=FORMATS,
        caption=(
            "Estabilidad interanual de la clase 70 — Loma costera en el conjunto "
            "de los cinco ámbitos del ACR Sistema de Lomas de Lima, frente a la "
            "calidad del insumo Landsat del mosaico oficial. (a) Residual local "
            "por año, definido como la superficie del año menos la media de los "
            "dos años vecinos; las bandas horizontales abarcan ±1 desviación "
            "estándar dentro de cada régimen de sensor. (b) Número de escenas "
            "Landsat que componen el mosaico del ACR. (c) Nubosidad media "
            "declarada por el mosaico. En (b) y (c) la barra de 1985 se destaca "
            "en color."
        ),
        note=(
            "n = 37 años de residual (1987-2023) y 38 años de insumo "
            "(1985-2022). Regímenes de sensor: I, Landsat 5; II, mezcla de "
            "Landsat 5, 7 y compuestos mixtos; III, Landsat 8 y 9. El residual "
            "de 1986 no es calculable porque exigiría 1985 como vecino, y 1985 "
            "está excluido de la serie por ruptura de inicio documentada. Los "
            "años 2023 y 2024 no se representan en (b) ni en (c): el mosaico "
            "pasa a la versión 5 y el recuento de escenas responde a otra "
            "convención, con 515 y 236 escenas frente a una media de 89 en la "
            "versión 4. La hipótesis de que el número de escenas explicara la "
            "inestabilidad interanual fue contrastada y descartada (Pearson "
            "-0,226; Spearman -0,104; +0,053 excluyendo 1986). El residual mide "
            "desviación respecto de los años vecinos, no error frente a una "
            "verificación de campo, y no representa pérdida ni ganancia "
            "ecológica."
        ),
        source_note=(
            "MapBiomas Perú, Colección 3, mapa anual de cobertura y uso del "
            "suelo (1985-2024), 30 m; mosaicos Landsat oficiales "
            "nexgenmap/MapBiomas2/LANDSAT/PANAMAZON/mosaics-2 y "
            "mapbiomas-raisg/MOSAICOS/mosaics-2. Auditoría de insumo del control "
            "6E5. Archivo: serie_indicadores_acr_1985_2024.csv. Acceso: agosto "
            "de 2026."
        ),
    )
    print(f"{STEM}: {manifest['figure_size_mm']} mm — verificación de trazado "
          f"{'OK' if manifest['layout_check']['passed'] else 'FALLIDA'}")


if __name__ == "__main__":
    main()
