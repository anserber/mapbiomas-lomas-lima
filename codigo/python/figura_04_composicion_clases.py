#!/usr/bin/env python3
"""
CONTRACT     : F04
QUESTION     : ¿Cómo se reparte la superficie de cada ámbito del ACR entre las
               clases de cobertura de MapBiomas entre 1986 y 2024, y hacia qué
               clase se desplaza la superficie que deja de clasificarse como
               clase 70 — Loma costera?
MESSAGE      : La superficie que abandona la clase 70 se traslada casi
               íntegramente a la clase 68 — Otra área natural sin vegetación, que
               es su complemento dentro del clasificador binario, y no a la clase
               24 — Infraestructura urbana. La excepción es Carabayllo 1, donde
               la clase 24 sí crece de forma visible hasta ocupar el 19,7 % del
               ámbito en 2023.
SOURCE       : 04_extraccion_series/02_resultados/serie_clases_acr_1985_2024.csv
UNIT         : porcentaje del área de grilla del ámbito, por año
INCLUDES     : cinco ámbitos del ACR; años 1986-2024; las siete clases presentes
               en el ACR según la leyenda de la Colección 3.
EXCLUDES     : 1985, por ruptura de inicio de serie documentada (controles 6E4
               y 6E5). Anillos externos y KBA restringida.
PROHIBITIONS : no describir el traspaso 70 -> 68 como pérdida de vegetación ni
               como degradación; no sumar clases naturales y antrópicas en una
               sola categoría; no emplear una paleta distinta de la oficial.
VISUAL FORM  : small multiples de área apilada al 100 %. Se apila porque las
               siete clases forman un todo exhaustivo y sin solape: suman
               exactamente el área de grilla de cada ámbito. La clase 70 ocupa la
               base y la clase 24 el techo, de modo que ambas se leen contra un
               borde recto. Paleta oficial de MapBiomas Perú, Colección 3.
LIMIT        : composición cartográfica de clases modeladas, no medición directa
               de vegetación ni de condición ecológica.
OUTPUT       : figura_04_composicion_clases_acr_1986_2024

Nota sobre el denominador: la columna `area_pct_ambito` del archivo fuente está
calculada contra la superficie vectorial y suma 99,94 %. Aquí el porcentaje se
recalcula contra la superficie de grilla, que es el denominador declarado en la
adenda metodológica v1.1, y la pila alcanza exactamente el 100 %.

Run:  python figura_04_composicion_clases.py
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
from sciviz import MM

# ---------------------------------------------------------------- paths ----
ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "04_extraccion_series/02_resultados/serie_clases_acr_1985_2024.csv"
OUTDIR = ROOT / "10_comunicacion_resultados/02_final/figuras"
STEM = "figura_04_composicion_clases_acr_1986_2024"

LANG = "es"
FORMATS = ("pdf", "png")

YEAR_MIN, YEAR_MAX = 1986, 2024

AMBITOS = [
    ("ancon",        "Ancón"),
    ("villa_maria",  "Villa María"),
    ("amancaes",     "Amancaes"),
    ("carabayllo_1", "Carabayllo 1"),
    ("carabayllo_2", "Carabayllo 2"),
]

# Paleta oficial de MapBiomas Perú, Colección 3.
# Fuente: https://peru.mapbiomas.org/codigos-de-la-leyenda/
#         Leyenda_MapBiomasPeru_3-Leyenda-CortaENES.pdf
# Orden de apilado de abajo arriba: la clase focal 70 en la base y la clase 24
# en el techo, para que ambas se lean contra un borde recto.
# La cuarta columna recoge la distinción natural/antrópico de la propia leyenda
# oficial. Se dibuja como trama porque la paleta oficial no es segura para
# daltonismo: bajo deuteranopía la clase 70 y la clase 24 convergen en un mismo
# oliva. La trama añade un canal que no depende del color y, a la vez, codifica
# un atributo real de la leyenda en lugar de decorar.
CLASES = [
    (70, "Loma costera",                     "#be9e00", False),
    (68, "Otra área natural sin vegetación", "#E97A7A", False),
    (13, "Otra formación no boscosa",        "#d89f5c", False),
    (66, "Matorral",                         "#a89358", False),
    (4,  "Bosque seco",                      "#7dc975", False),
    (21, "Mosaico agropecuario",             "#ffefc3", True),
    (24, "Infraestructura urbana",           "#d4271e", True),
]
TRAMA = "////"


# ---------------------------------------------------- input assertions -----
def load() -> pd.DataFrame:
    df = pd.read_csv(SOURCE)
    faltan = {"id_ambito", "year", "class_id", "area_ha"} - set(df.columns)
    if faltan:
        raise SystemExit(f"la fuente no trae las columnas: {sorted(faltan)}")

    df["year"] = df["year"].astype(float).astype(int)
    df["class_id"] = df["class_id"].astype(int)
    df = df[(df["year"] >= YEAR_MIN) & (df["year"] <= YEAR_MAX)]

    codigos_datos = set(df["class_id"].unique())
    codigos_paleta = {c for c, _, _, _ in CLASES}
    if not codigos_datos <= codigos_paleta:
        raise SystemExit(
            f"clases sin color oficial asignado: {sorted(codigos_datos - codigos_paleta)}")

    # Pivote con relleno explícito: una clase ausente en un año vale 0 ha, no
    # es un dato faltante. La distinción importa: aquí el cero es información.
    piv = (df.pivot_table(index=["id_ambito", "year"], columns="class_id",
                          values="area_ha", aggfunc="sum")
             .reindex(columns=[c for c, _, _, _ in CLASES])
             .fillna(0.0))

    # Porcentaje contra el área de grilla, no contra la vectorial: la columna
    # area_pct_ambito del origen usa el denominador vectorial y suma 99,94 %.
    pct = piv.div(piv.sum(axis=1), axis=0) * 100.0

    for (aid, year), fila in pct.iterrows():
        if abs(fila.sum() - 100.0) > 1e-6:
            raise SystemExit(f"{aid} {year}: la pila no suma 100 %")
    n_años = pct.groupby(level=0).size()
    if not (n_años == (YEAR_MAX - YEAR_MIN + 1)).all():
        raise SystemExit("algún ámbito no tiene los 39 años completos")

    return pct


# ------------------------------------------------------------- drawing -----
def build(pct: pd.DataFrame):
    w_mm = sciviz.WIDTHS["a4text"]
    fig, axes = plt.subplots(
        3, 2, figsize=(w_mm * MM, 118 * MM), layout="constrained",
        sharex=True, sharey=True,
    )
    fig.get_layout_engine().set(w_pad=1.5 * MM, h_pad=1.5 * MM,
                                hspace=0.05, wspace=0.05)
    planos = axes.ravel()

    for i, (aid, nombre) in enumerate(AMBITOS):
        ax = planos[i]
        d = pct.loc[aid].sort_index()
        años = d.index.to_numpy()
        capas = [d[c].to_numpy() for c, _, _, _ in CLASES]
        colores = [h for _, _, h, _ in CLASES]

        bandas = ax.stackplot(años, *capas, colors=colores,
                              edgecolor="white", linewidth=0.3)
        for banda, (_, _, _, antropico) in zip(bandas, CLASES):
            if antropico:
                banda.set_hatch(TRAMA)
                banda.set_edgecolor("#3A0B06")
                banda.set_linewidth(0.3)
        ax.set_ylim(0, 100)
        ax.set_yticks([0, 25, 50, 75, 100])
        ax.set_xlim(YEAR_MIN - 0.5, YEAR_MAX + 0.5)
        ax.set_xticks([1990, 2000, 2010, 2020])
        ax.set_title(f"({chr(97 + i)}) {nombre}", loc="left",
                     fontsize=sciviz.pt(0.95), fontweight="bold", pad=2.0)
        for lado in ("top", "right"):
            ax.spines[lado].set_visible(False)

    # La sexta celda aloja la leyenda: siete clases no admiten etiquetado
    # directo dentro de bandas apiladas.
    ax_leyenda = planos[-1]
    ax_leyenda.axis("off")
    manijas = [
        plt.Rectangle((0, 0), 1, 1, facecolor=h,
                      edgecolor="#3A0B06" if antropico else "#666666",
                      hatch=TRAMA if antropico else None, linewidth=0.3)
        for _, _, h, antropico in CLASES
    ]
    etiquetas = [f"{c} · {n}" for c, n, _, _ in CLASES]
    ax_leyenda.legend(manijas, etiquetas, loc="center left", frameon=False,
                      fontsize=sciviz.pt(0.85), handlelength=1.1,
                      handleheight=0.9, labelspacing=0.55,
                      borderpad=0.0, borderaxespad=0.0)

    planos[2].set_ylabel("Composición de clases (% del área de grilla)")
    for ax in (planos[3], planos[4]):
        # Bajo el panel (d) está la leyenda, no otro panel: con sharex activado
        # matplotlib le quita las marcas y quedaría un rótulo de eje sin años.
        ax.tick_params(labelbottom=True)
        ax.set_xlabel("Año")

    return fig


# ---------------------------------------------------------------- main -----
def main():
    pct = load()
    fig = build(pct)

    manifest = sciviz.finalize(
        fig,
        outdir=OUTDIR,
        stem=STEM,
        contract="F04",
        source=SOURCE,
        lang=LANG,
        formats=FORMATS,
        caption=(
            "Composición anual de clases de cobertura y uso del suelo en los "
            "cinco ámbitos del ACR Sistema de Lomas de Lima, 1986-2024, "
            "expresada como porcentaje del área de grilla de cada ámbito. Las "
            "siete clases presentes forman un conjunto exhaustivo y sin solape: "
            "suman exactamente el área de grilla. La clase 70 se apila en la "
            "base y la clase 24 en el techo, de modo que ambas se leen contra un "
            "borde recto. Los colores son los de la leyenda oficial de MapBiomas "
            "Perú, Colección 3; las dos clases antrópicas de esa leyenda, 21 y "
            "24, se distinguen además por trama."
        ),
        note=(
            "n = 39 años por ámbito (1986-2024); 5 ámbitos; 7 clases. El año "
            "1985 se excluye por ruptura de inicio de serie documentada en los "
            "controles 6E4 y 6E5. El porcentaje se calcula contra la superficie "
            "de grilla y no contra la superficie vectorial del polígono, "
            "conforme a la adenda metodológica v1.1. Las clases 4, 21, 24 y 66 "
            "no están presentes en todos los ámbitos ni en todos los años; su "
            "ausencia se representa como cero, que es información y no dato "
            "faltante. Las clases antrópicas llevan trama porque la paleta oficial "
            "no es segura para daltonismo: bajo deuteranopía las clases 70 y 24 "
            "convergen en un mismo tono, de modo que la trama aporta una "
            "distinción que no depende del color. La transición entre las "
            "clases 70 y 68 corresponde a la "
            "activación o desactivación del clasificador binario de loma "
            "costera, no a una conversión de cobertura: la clase 68 es el "
            "complemento de la clase 70 en el mapa regional de base y no tiene "
            "prioridad sobre ella en la jerarquía de integración. La "
            "composición representa clases cartográficas modeladas, no medición "
            "directa de vegetación ni de condición ecológica."
        ),
        source_note=(
            "MapBiomas Perú, Colección 3, mapa anual de cobertura y uso del "
            "suelo (1985-2024), 30 m. Paleta y códigos de la leyenda corta de la "
            "Colección 3, publicados en peru.mapbiomas.org/codigos-de-la-leyenda. "
            "Archivo: serie_clases_acr_1985_2024.csv. Acceso: agosto de 2026."
        ),
    )
    print(f"{STEM}: {manifest['figure_size_mm']} mm — verificación de trazado "
          f"{'OK' if manifest['layout_check']['passed'] else 'FALLIDA'}")


if __name__ == "__main__":
    main()
