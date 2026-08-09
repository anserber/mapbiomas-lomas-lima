#!/usr/bin/env python3
"""
CONTRACT     : F07 (fusiona los contratos originales F03 y F04)
QUESTION     : ¿Dónde se concentra la transición estable hacia clase 24 —
               Infraestructura urbana confirmada por la ventana W5, dónde la
               señal reciente todavía censurada, y cómo varía la presión con la
               distancia al sistema de lomas?
MESSAGE      : La señal urbana confirmada es máxima en el anillo inmediato,
               2,88 ha-evento por 1 000 ha, y decae de forma monótona con la
               distancia hasta 0,13 a 1-2 km. La señal reciente censurada tiene
               otra geografía: se concentra dentro de dos ámbitos del ACR, Villa
               María y Amancaes, con 27,3 y 23,4, muy por encima de cualquier
               anillo. Tres ámbitos no registran ninguna de las dos señales.
SOURCE       : 09_integracion_resultados/02_final/
               tabla_maestra_resultados_publicos_v2.csv
UNIT         : hectáreas-evento por 1 000 ha de área de grilla de la unidad
INCLUDES     : cinco ámbitos del ACR y tres anillos disueltos de la periferia
               externa. W5 confirmada con ventana completa 1990-2020; señal
               censurada en 2021-2024.
EXCLUDES     : anillos por ámbito, que se solapan y no admiten totales; KBA
               restringida.
PROHIBITIONS : PROHIBIDO SUMAR las dos señales o apilarlas. Tienen ventana,
               estatus y confianza distintos: W5 se apoya en el estrato E2 con
               confianza ALTA y la censura en el estrato E3 con confianza MEDIA.
               El campo que las sumaba se retiró de la tabla pública v2. No
               describir ninguna de las dos como pérdida ecológica ni atribuir
               causa, legalidad ni responsabilidad.
VISUAL FORM  : dos paneles. (a) diagrama de puntos por unidad, con las dos
               señales como series separadas sobre un eje común, nunca apiladas.
               (b) gradiente de las dos señales frente a la distancia real al
               sistema, situando cada anillo en su punto medio. Escalas distintas
               entre paneles porque responden a preguntas distintas: una compara
               unidades, la otra describe una variación con la distancia.
LIMIT        : `ha-evento` suma superficie por evento temporal y no equivale a
               superficie física única: un mismo píxel puede aportar más de un
               evento en años distintos.
OUTPUT       : figura_07_presion_urbana_w5_y_censura

Run:  python figura_07_presion_urbana.py
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
SOURCE = (ROOT / "09_integracion_resultados/02_final/"
                 "tabla_maestra_resultados_publicos_v2.csv")
OUTDIR = ROOT / "10_comunicacion_resultados/02_final/figuras"
STEM = "figura_07_presion_urbana_w5_y_censura"

LANG = "es"
FORMATS = ("pdf", "png")

ETIQUETAS = {
    "acr|villa_maria":   "Villa María",
    "acr|amancaes":      "Amancaes",
    "acr|carabayllo_2":  "Carabayllo 2",
    "acr|carabayllo_1":  "Carabayllo 1",
    "acr|ancon":         "Ancón",
    "sistema|0_500":     "Anillo 0–500 m",
    "sistema|500_1000":  "Anillo 500–1 000 m",
    "sistema|1000_2000": "Anillo 1 000–2 000 m",
}

# Punto medio de cada anillo: sitúa el gradiente sobre una distancia real, de
# modo que la línea sea una interpolación legítima y no un artificio ordinal.
PUNTO_MEDIO_M = {"sistema|0_500": 250, "sistema|500_1000": 750,
                 "sistema|1000_2000": 1500}
# Extensión real de cada anillo. El panel (b) dibuja la tasa como un segmento
# sobre este intervalo, no como un punto unido al siguiente: la medición no
# existe en el punto medio, existe en toda la banda.
EXTENSION_M = {"sistema|0_500": (0, 500), "sistema|500_1000": (500, 1000),
               "sistema|1000_2000": (1000, 2000)}

C_W5 = OKABE_ITO["blue"]
C_CENSURA = OKABE_ITO["orange"]


# ---------------------------------------------------- input assertions -----
def load() -> pd.DataFrame:
    df = pd.read_csv(SOURCE)
    columnas = {"unidad_id", "dominio", "tasa_w5_urbano_por_1000ha",
                "tasa_censura_urbano_por_1000ha", "w5_urbano_ha_evento",
                "censura_urbano_2021_2024_ha_evento", "area_grilla_ha"}
    faltan = columnas - set(df.columns)
    if faltan:
        raise SystemExit(f"la fuente no trae las columnas: {sorted(faltan)}")
    if "tasa_presion_urbana_indicativa_por_1000ha" in df.columns:
        raise SystemExit(
            "la fuente aún contiene el campo que suma W5 y censura; esta figura "
            "exige la tabla maestra v2, de la que ese campo fue retirado")
    if len(df) != 8:
        raise SystemExit(f"se esperaban 8 unidades públicas y hay {len(df)}")

    # Las tasas deben reproducirse desde sus numeradores y denominadores.
    for col_tasa, col_ha in (("tasa_w5_urbano_por_1000ha", "w5_urbano_ha_evento"),
                             ("tasa_censura_urbano_por_1000ha",
                              "censura_urbano_2021_2024_ha_evento")):
        esperada = df[col_ha] / df["area_grilla_ha"] * 1000
        if not np.allclose(df[col_tasa], esperada, atol=1e-6):
            raise SystemExit(f"{col_tasa} no se reproduce desde {col_ha}")

    df["orden_grupo"] = (df["dominio"] == "ANILLO_SISTEMA").astype(int)
    df = df.sort_values(["orden_grupo", "tasa_censura_urbano_por_1000ha"],
                        ascending=[True, False])
    return df.reset_index(drop=True)


# ------------------------------------------------------------- drawing -----
def build(df: pd.DataFrame):
    w_mm = sciviz.WIDTHS["a4text"]
    fig, (ax_u, ax_g) = plt.subplots(
        1, 2, figsize=(w_mm * MM, 76 * MM), layout="constrained",
        gridspec_kw={"width_ratios": [1.45, 1.0]},
    )
    fig.get_layout_engine().set(w_pad=1.5 * MM, h_pad=1.5 * MM, wspace=0.05)

    # ---- (a) por unidad --------------------------------------------------
    n_acr = int((df["orden_grupo"] == 0).sum())
    y = [len(df) - i + (0 if i < n_acr else -1) for i in range(len(df))]

    ax_u.hlines(y, 0, df["tasa_censura_urbano_por_1000ha"].clip(lower=0),
                color="#E4E4E4", linewidth=0.8, zorder=0)
    ax_u.plot(df["tasa_censura_urbano_por_1000ha"], y, marker="^",
              markersize=4.2, linestyle="none", color=C_CENSURA, zorder=3)
    ax_u.plot(df["tasa_w5_urbano_por_1000ha"], y, marker="o", markersize=3.6,
              linestyle="none", color=C_W5, zorder=4)

    ax_u.set_yticks(y, [ETIQUETAS[u] for u in df["unidad_id"]])
    ax_u.set_ylim(-0.9, len(df) + 0.9)
    ax_u.set_xlim(-0.6, 30)
    ax_u.set_xticks([0, 10, 20, 30])
    ax_u.set_xlabel(f"ha-evento · (1 000 ha)⁻¹")
    ax_u.set_title("(a)", loc="left", fontsize=sciviz.pt(0.95),
                   fontweight="bold", pad=3.0)
    ax_u.tick_params(axis="y", length=0)

    # ---- (b) gradiente con la distancia ----------------------------------
    anillos = df[df["dominio"] == "ANILLO_SISTEMA"].copy()
    anillos["x"] = anillos["unidad_id"].map(PUNTO_MEDIO_M)
    anillos = anillos.sort_values("x")

    # Sin línea de continuidad entre anillos. Una línea que une los tres puntos
    # medios afirma dos cosas que el dato no sostiene: que la tasa está medida
    # en trayectoria continua entre 250 y 1 500 m, y que las dos señales son
    # dos curvas comparables. No lo son: W5 se apoya en el estrato E2 con
    # confianza ALTA y la censura en el E3 con MEDIA, y tienen ventanas y
    # estatus distintos. Cada tasa se dibuja como un segmento sobre la banda en
    # que efectivamente se midió.
    for col, color, marca, etq in (
            ("tasa_w5_urbano_por_1000ha", C_W5, "o", "W5 confirmada"),
            ("tasa_censura_urbano_por_1000ha", C_CENSURA, "^",
             "Reciente censurada")):
        for _, f in anillos.iterrows():
            x0, x1 = EXTENSION_M[f["unidad_id"]]
            ax_g.plot([x0, x1], [f[col], f[col]], color=color, linewidth=1.2,
                      solid_capstyle="butt", zorder=3)
        ax_g.plot(anillos["x"], anillos[col], marker=marca, markersize=4.2,
                  linestyle="none", color=color, label=etq, zorder=4)

    x_primero = min(PUNTO_MEDIO_M.values())
    for _, f in anillos.iterrows():
        # El primer anillo va pegado al borde izquierdo: su rótulo a la
        # izquierda se salía del eje y pisaba las marcas. Se coloca encima,
        # donde no hay trazo. Los otros dos caben a la izquierda de su punto.
        if f["x"] == x_primero:
            desplazamiento, alineacion = (0, 7), "center"
        else:
            desplazamiento, alineacion = (-5, -7), "right"
        ax_g.annotate(f"{f['tasa_w5_urbano_por_1000ha']:.2f}".replace(".", ","),
                      (f["x"], f["tasa_w5_urbano_por_1000ha"]),
                      textcoords="offset points", xytext=desplazamiento,
                      ha=alineacion, fontsize=sciviz.pt(0.8), color=C_W5)

    # Marcas métricas en vez de los nombres de los intervalos: el eje es una
    # distancia real y los nombres largos colisionaban en un panel de 60 mm.
    ax_g.set_xticks([0, 500, 1000, 1500, 2000])
    ax_g.set_xlim(0, 2050)
    # Al pasar de puntos a segmentos, la banda censurada de 0-500 m se extiende
    # hasta x = 500 a la altura de 5,97 y la leyenda, anclada arriba a la
    # derecha, quedaba a esa misma altura. Se levanta el techo del eje para que
    # la leyenda no comparta franja con ningún trazo.
    ax_g.set_ylim(-0.9, 8.6)
    ax_g.set_xlabel("Distancia al sistema (m)")
    ax_g.set_ylabel("ha-evento · (1 000 ha)⁻¹")
    ax_g.set_title("(b)", loc="left", fontsize=sciviz.pt(0.95),
                   fontweight="bold", pad=3.0)
    ax_g.legend(loc="upper right", frameon=False, fontsize=sciviz.pt(0.8),
                handletextpad=0.5, labelspacing=0.35, borderaxespad=0.3)

    for ax in (ax_u, ax_g):
        ax.grid(axis="x" if ax is ax_u else "y", linewidth=0.4, color="#DDDDDD")
        ax.set_axisbelow(True)
        for lado in ("top", "right"):
            ax.spines[lado].set_visible(False)
    ax_u.spines["left"].set_visible(False)

    return fig


# ---------------------------------------------------------------- main -----
def main():
    df = load()
    an = df[df["dominio"] == "ANILLO_SISTEMA"].set_index("unidad_id")
    print("  gradiente W5: " + " → ".join(
        f"{an.loc[u, 'tasa_w5_urbano_por_1000ha']:.2f}"
        for u in ["sistema|0_500", "sistema|500_1000", "sistema|1000_2000"]))

    fig = build(df)

    manifest = sciviz.finalize(
        fig,
        outdir=OUTDIR,
        stem=STEM,
        contract="F07",
        source=SOURCE,
        lang=LANG,
        formats=FORMATS,
        caption=(
            "Transición hacia la clase 24 — Infraestructura urbana en las ocho "
            "unidades públicas del diagnóstico, normalizada por 1 000 hectáreas "
            "de área de grilla. (a) Comparación por unidad: los ámbitos del ACR "
            "arriba y los anillos de periferia abajo, ordenados por señal "
            "censurada descendente dentro de cada grupo. (b) Variación de ambas "
            "señales con la distancia al sistema de lomas; cada anillo se sitúa "
            "en su punto medio y se rotula el valor de la señal confirmada. Las "
            "dos señales se mantienen como series separadas en los dos paneles."
        ),
        note=(
            "n = 8 unidades. La señal W5 confirmada corresponde a transiciones "
            "que permanecen en clase 24 durante el año del evento y los cuatro "
            "siguientes, con ventana completa entre 1990 y 2020. La señal "
            "censurada corresponde a salidas de la clase 70 registradas entre 2021 "
            "y 2024, que no pueden completar esa ventana antes del final de la "
            "serie. Las dos no deben sumarse ni presentarse como una única medida "
            "de presión: tienen ventana temporal, estatus y confianza distintos, "
            "ALTA para la confirmada y MEDIA para la censurada según la "
            "validación visual ciega. Carabayllo 1, Carabayllo 2 y Ancón "
            "registran cero en ambas señales. La unidad ha-evento suma "
            "superficie por evento temporal y no equivale a superficie física "
            "única: un mismo píxel puede aportar más de un evento en años "
            "distintos. Una transición hacia la clase 24 no demuestra por sí "
            "sola ocupación ilegal, invasión ni incumplimiento normativo."
        ),
        source_note=(
            "MapBiomas Perú, Colección 3, mapa anual de cobertura y uso del "
            "suelo y mapa oficial de transiciones (1985-2024), 30 m. Archivo: "
            "tabla_maestra_resultados_publicos_v2.csv. Acceso: agosto de 2026."
        ),
    )
    print(f"{STEM}: {manifest['figure_size_mm']} mm — verificación de trazado "
          f"{'OK' if manifest['layout_check']['passed'] else 'FALLIDA'}")


if __name__ == "__main__":
    main()
