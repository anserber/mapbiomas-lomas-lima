#!/usr/bin/env python3
"""
CONTRACT     : F06
QUESTION     : ¿Qué proporción de cada unidad territorial corresponde al núcleo
               que ha sido clase 70 — Loma costera todos los años, cuánto a la
               cobertura actual, y cuánto a la envolvente de superficie que
               alguna vez fue clasificada como clase 70?
MESSAGE      : La cobertura de 2024 coincide prácticamente con el núcleo
               persistente: la brecha entre ambos no supera 0,62 puntos
               porcentuales en ninguna unidad. No existe superficie de loma
               ganada recientemente. En cambio la envolvente histórica es mucho
               mayor que el núcleo —en Ancón lo dobla, 45,6 % frente a 22,1 %—,
               de modo que la diferencia entre ambas mide la superficie inestable
               de la clase, no cobertura adicional disponible.
SOURCE       : 09_integracion_resultados/02_final/
               tabla_maestra_resultados_publicos_v2.csv
UNIT         : porcentaje del área de grilla de cada unidad
INCLUDES     : cinco ámbitos del ACR y tres anillos disueltos de la periferia
               externa; ventana 1986-2024 para la envolvente.
EXCLUDES     : anillos por ámbito, que se solapan entre sí y no pueden sumarse;
               KBA restringida.
PROHIBITIONS : no leer la envolvente como superficie de loma recuperable ni como
               potencial de restauración; no describir la diferencia entre
               envolvente y núcleo como pérdida.
VISUAL FORM  : gráfico de rangos horizontal. Se descarta el diagrama de puntos
               emparejados previsto en el contrato original —cobertura de 2024
               frente a núcleo persistente— porque la brecha entre ambos es de
               0,00 a 0,62 puntos y los dos marcadores se superponen. La
               superposición se conserva como mensaje, y el rango se extiende
               hasta la envolvente, que es donde está la variación real.
LIMIT        : persistencia cartográfica de una clase beta; no mide calidad ni
               condición ecológica del hábitat.
OUTPUT       : figura_06_nucleo_y_envolvente_clase70

Run:  python figura_06_nucleo_y_envolvente.py
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
SOURCE = (ROOT / "09_integracion_resultados/02_final/"
                 "tabla_maestra_resultados_publicos_v2.csv")
OUTDIR = ROOT / "10_comunicacion_resultados/02_final/figuras"
STEM = "figura_06_nucleo_y_envolvente_clase70"

LANG = "es"
FORMATS = ("pdf", "png")

ETIQUETAS = {
    "acr|amancaes":      "Amancaes",
    "acr|villa_maria":   "Villa María",
    "acr|carabayllo_2":  "Carabayllo 2",
    "acr|carabayllo_1":  "Carabayllo 1",
    "acr|ancon":         "Ancón",
    "sistema|0_500":     "Anillo 0–500 m",
    "sistema|500_1000":  "Anillo 500–1 000 m",
    "sistema|1000_2000": "Anillo 1 000–2 000 m",
}

C_NUCLEO = OKABE_ITO["blue"]
C_ENVOLVENTE = OKABE_ITO["vermillion"]
C_RANGO = "#C8C8C8"


# ---------------------------------------------------- input assertions -----
def load() -> pd.DataFrame:
    df = pd.read_csv(SOURCE)
    columnas = {"unidad_id", "dominio", "area_grilla_ha", "area_siempre70_ha",
                "area_70_2024_ha", "area_alguna_vez70_1986_2024_ha"}
    faltan = columnas - set(df.columns)
    if faltan:
        raise SystemExit(f"la fuente no trae las columnas: {sorted(faltan)}")
    if len(df) != 8:
        raise SystemExit(f"se esperaban 8 unidades públicas y hay {len(df)}")

    g = df["area_grilla_ha"]
    df["nucleo"] = df["area_siempre70_ha"] / g * 100
    df["actual"] = df["area_70_2024_ha"] / g * 100
    df["envolvente"] = df["area_alguna_vez70_1986_2024_ha"] / g * 100

    # Relación de contención que el indicador promete: núcleo ⊆ actual ⊆ envolvente.
    # Si se rompiera, la figura estaría dibujando un rango que no existe.
    if (df["nucleo"] > df["actual"] + 1e-9).any():
        raise SystemExit("hay unidades con núcleo mayor que la cobertura de 2024")
    if (df["actual"] > df["envolvente"] + 1e-9).any():
        raise SystemExit("hay unidades con cobertura de 2024 mayor que la envolvente")

    # ACR primero y anillos después; dentro de cada grupo, por núcleo descendente.
    df["orden_grupo"] = (df["dominio"] == "ANILLO_SISTEMA").astype(int)
    df = df.sort_values(["orden_grupo", "nucleo"], ascending=[True, False])
    return df.reset_index(drop=True)


# ------------------------------------------------------------- drawing -----
def build(df: pd.DataFrame):
    fig, ax = sciviz.new_figure(width="a4text", height_mm=80)

    n_acr = int((df["orden_grupo"] == 0).sum())
    # Hueco de una posición entre los dos grupos, sin línea divisoria: la
    # separación basta y una línea más sería tinta que no codifica nada.
    y = [len(df) - i + (0 if i < n_acr else -1) for i in range(len(df))]

    ax.hlines(y, df["nucleo"], df["envolvente"], color=C_RANGO,
              linewidth=2.6, zorder=1, capstyle="round")
    ax.plot(df["envolvente"], y, marker="|", markersize=6.5,
            markeredgewidth=1.2, linestyle="none", color=C_ENVOLVENTE, zorder=3)
    ax.plot(df["actual"], y, marker="o", markersize=6.0, linestyle="none",
            markerfacecolor="none", markeredgecolor=C_NUCLEO,
            markeredgewidth=0.9, zorder=4)
    ax.plot(df["nucleo"], y, marker="o", markersize=2.8, linestyle="none",
            color=C_NUCLEO, zorder=5)

    ax.set_yticks(y, [ETIQUETAS[u] for u in df["unidad_id"]])
    ax.set_ylim(-0.9, len(df) + 0.9)
    ax.set_xlim(0, 100)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel("Clase 70 — Loma costera (% del área de grilla)")

    manijas = [
        plt.Line2D([], [], marker="o", markersize=2.8, linestyle="none",
                   color=C_NUCLEO, label="Núcleo persistente (todos los años)"),
        plt.Line2D([], [], marker="o", markersize=6.0, linestyle="none",
                   markerfacecolor="none", markeredgecolor=C_NUCLEO,
                   markeredgewidth=0.9, label="Cobertura en 2024"),
        plt.Line2D([], [], marker="|", markersize=6.5, linestyle="none",
                   markeredgewidth=1.2, color=C_ENVOLVENTE,
                   label="Envolvente 1986–2024 (alguna vez clase 70)"),
    ]
    ax.legend(handles=manijas, loc="lower right", frameon=False,
              fontsize=sciviz.pt(0.8), handletextpad=0.5, labelspacing=0.4,
              borderaxespad=0.4)

    ax.grid(axis="x", linewidth=0.4, color="#DDDDDD")
    ax.set_axisbelow(True)
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    ax.tick_params(axis="y", length=0)

    sciviz.declare_n(ax, len(df), where="upper right")
    return fig


# ---------------------------------------------------------------- main -----
def main():
    df = load()
    brecha = (df["actual"] - df["nucleo"]).max()
    print(f"  brecha máxima entre cobertura de 2024 y núcleo: {brecha:.2f} pp")
    for _, f in df.iterrows():
        print(f"  {ETIQUETAS[f['unidad_id']]:22s} núcleo {f['nucleo']:5.1f} % | "
              f"2024 {f['actual']:5.1f} % | envolvente {f['envolvente']:5.1f} %")

    fig = build(df)

    manifest = sciviz.finalize(
        fig,
        outdir=OUTDIR,
        stem=STEM,
        contract="F06",
        source=SOURCE,
        lang=LANG,
        formats=FORMATS,
        caption=(
            "Núcleo persistente, cobertura actual y envolvente histórica de la "
            "clase 70 — Loma costera en las ocho unidades públicas del "
            "diagnóstico: los cinco ámbitos del ACR Sistema de Lomas de Lima y "
            "los tres anillos disueltos de su periferia externa. Cada barra gris "
            "abarca desde el núcleo persistente —superficie clasificada como "
            "clase 70 en todos los años— hasta la envolvente, es decir la "
            "superficie clasificada como clase 70 al menos una vez entre 1986 y "
            "2024. El círculo abierto marca la cobertura de 2024. Las unidades se "
            "ordenan por núcleo descendente, con los ámbitos del ACR arriba y los "
            "anillos de periferia abajo."
        ),
        note=(
            "n = 8 unidades. La cobertura de 2024 coincide prácticamente con el "
            "núcleo persistente: la brecha máxima entre ambos es de 0,62 puntos "
            "porcentuales, en Villa María, y es nula en Ancón, Carabayllo 1 y el "
            "anillo de 1 000–2 000 m. Por eso los dos marcadores se superponen. "
            "El núcleo persistente emplea la ventana completa 1985-2024, que se "
            "demostró insensible a la exclusión de 1985; la envolvente emplea la "
            "ventana 1986-2024, de la que 1985 sí queda excluido por ruptura de "
            "inicio de serie. La diferencia entre envolvente y núcleo mide la "
            "superficie con clasificación inestable de la clase beta 70, no "
            "cobertura recuperable ni potencial de restauración. Los porcentajes "
            "se calculan sobre el área de grilla de cada unidad."
        ),
        source_note=(
            "MapBiomas Perú, Colección 3, mapa anual de cobertura y uso del "
            "suelo (1985-2024), 30 m. Archivo: "
            "tabla_maestra_resultados_publicos_v2.csv. Acceso: agosto de 2026."
        ),
    )
    print(f"{STEM}: {manifest['figure_size_mm']} mm — verificación de trazado "
          f"{'OK' if manifest['layout_check']['passed'] else 'FALLIDA'}")


if __name__ == "__main__":
    main()
