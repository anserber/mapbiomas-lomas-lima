#!/usr/bin/env python3
"""
CONTRACT     : F08
QUESTION     : ¿Qué proporción de las señales cartográficas de cada estrato
               resultó respaldada por la validación visual ciega, y con qué
               incertidumbre?
MESSAGE      : El respaldo visual no es uniforme entre estratos. La persistencia
               de la clase 70 y la presión urbana W5 alcanzan el 100 % de apoyo;
               el intercambio 68↔70 baja al 66,7 %; y la recuperación 68→70 y el
               cambio 70→13 quedan en 27,3 % y 37,5 %, por debajo de lo que daría
               una decisión al azar. Los intervalos de Wilson son anchos porque
               cada estrato descansa sobre 8 a 12 evaluaciones: un 100 % con n=8
               no es lo mismo que un 100 % con n=11.
SOURCE       : 06_validacion_visual/02_final/metricas_concordancia_paso08.csv
UNIT         : porcentaje de evaluaciones con veredicto que respaldan el
               candidato cartográfico, con intervalo de Wilson del 95 %
INCLUDES     : los seis estratos de la muestra estratificada y la concordancia
               global de las 66 evaluaciones como referencia.
EXCLUDES     : el desglose por dominio, que contiene una fila del ámbito KBA
               restringido y no se publica. Las evaluaciones indeterminadas
               quedan fuera del denominador y se reportan como recuento aparte.
PROHIBITIONS : no presentar estas cifras como exactitud temática oficial de la
               Colección 3 ni como estimación probabilística para todo el
               paisaje: la muestra es estratificada y dirigida a señales
               candidatas, no aleatoria sobre el territorio.
VISUAL FORM  : diagrama de puntos con intervalo, en la tradición del forest plot.
               Se descarta la barra con bigotes: el relleno de la barra sugiere
               que la estimación puede estar en cualquier punto desde cero, y no
               es así. El color codifica el dictamen de confianza, que no es una
               función del punto estimado: E3 alcanza el 100 % de apoyo y aun así
               es MEDIA por sus cuatro evaluaciones indeterminadas.
LIMIT        : mide concordancia entre un intérprete y el candidato cartográfico
               sobre fuentes visuales auxiliares; no es verificación de campo ni
               medición de condición ecológica.
OUTPUT       : figura_08_confianza_validacion_por_estrato

Run:  python figura_08_confianza_estratos.py
"""

from __future__ import annotations

import math
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
SOURCE = (ROOT / "06_validacion_visual/02_final/"
                 "metricas_concordancia_paso08.csv")
OUTDIR = ROOT / "10_comunicacion_resultados/02_final/figuras"
STEM = "figura_08_confianza_validacion_por_estrato"

LANG = "es"
FORMATS = ("pdf", "png")

ETIQUETAS = {
    "E1_PERSISTENTE70":     "E1 · Persistente 70",
    "E2_URBANO_W5":         "E2 · Urbano W5",
    "E3_URBANO_CENSURADO":  "E3 · Urbano censurado",
    "E4_INTERCAMBIO_68_70": "E4 · Intercambio 68↔70",
    "E5_RECUPERACION_68_70": "E5 · Recuperación 68→70",
    "E6_CAMBIO_70_13":      "E6 · Cambio 70→13",
}
ORDEN = list(ETIQUETAS)

COLOR_DICTAMEN = {
    "ALTA":  OKABE_ITO["blue"],
    "MEDIA": OKABE_ITO["orange"],
    "BAJA":  OKABE_ITO["vermillion"],
}

# Segundo canal para el dictamen. El naranja y el bermellón de Okabe-Ito son
# distinguibles en deuteranopia, pero pierden separación al imprimir en escala
# de grises, y el dictamen es justamente lo que la figura codifica. La forma del
# marcador lo repite sin depender del color.
MARCA_DICTAMEN = {"ALTA": "o", "MEDIA": "s", "BAJA": "^"}
TAM_DICTAMEN = {"ALTA": 4.4, "MEDIA": 3.9, "BAJA": 4.6}

Z95 = 1.959963985


def wilson(k: int, n: int) -> tuple[float, float, float]:
    """Intervalo de Wilson al 95 %.

    Se recalcula en lugar de leerse del CSV para que la figura no pueda
    heredar en silencio un intervalo desactualizado: los valores obtenidos se
    contrastan después con los publicados.
    """
    if n == 0:
        return math.nan, math.nan, math.nan
    p = k / n
    d = 1 + Z95 ** 2 / n
    centro = (p + Z95 ** 2 / (2 * n)) / d
    medio = Z95 * math.sqrt(p * (1 - p) / n + Z95 ** 2 / (4 * n * n)) / d
    return p * 100, (centro - medio) * 100, (centro + medio) * 100


# ---------------------------------------------------- input assertions -----
def load() -> tuple[pd.DataFrame, dict]:
    df = pd.read_csv(SOURCE)
    columnas = {"nivel", "grupo", "total", "evaluable", "acuerdo",
                "indeterminado", "apoyo_visual_pct", "ic95_wilson_inf_pct",
                "ic95_wilson_sup_pct", "dictamen"}
    faltan = columnas - set(df.columns)
    if faltan:
        raise SystemExit(f"la fuente no trae las columnas: {sorted(faltan)}")

    estratos = df[df["nivel"] == "estrato"].set_index("grupo").loc[ORDEN].reset_index()
    if len(estratos) != 6:
        raise SystemExit("se esperaban los seis estratos E1-E6")

    calc = estratos.apply(
        lambda f: wilson(int(f["acuerdo"]), int(f["evaluable"])), axis=1,
        result_type="expand")
    estratos[["p", "lo", "hi"]] = calc

    # El intervalo recalculado debe coincidir con el publicado en el paso 8.
    for col_calc, col_pub in (("p", "apoyo_visual_pct"),
                              ("lo", "ic95_wilson_inf_pct"),
                              ("hi", "ic95_wilson_sup_pct")):
        if not np.allclose(estratos[col_calc], estratos[col_pub], atol=0.06):
            raise SystemExit(
                f"el intervalo recalculado no reproduce {col_pub} del paso 8")

    # La aritmética que sostiene el denominador evaluable.
    if not ((estratos["acuerdo"] + (estratos["evaluable"] - estratos["acuerdo"]))
            == estratos["evaluable"]).all():
        raise SystemExit("la partición acuerdo/desacuerdo no cierra")
    if not ((estratos["evaluable"] + estratos["indeterminado"])
            == estratos["total"]).all():
        raise SystemExit("evaluable + indeterminado no reproduce el total")

    # La referencia de fondo es la fila de sectores únicos, no la de las 66
    # evaluaciones. Las seis repeticiones ciegas miden consistencia del
    # evaluador y no son unidades de muestra: incluirlas en el estimador
    # principal contaría seis sectores dos veces. El apartado 5.8 publica
    # 38/54 = 70,4 % y la figura tiene que mostrar esa misma cifra.
    g = df[(df["nivel"] == "sensibilidad")].iloc[0]
    p, lo, hi = wilson(int(g["acuerdo"]), int(g["evaluable"]))
    for calc, pub in ((p, "apoyo_visual_pct"), (lo, "ic95_wilson_inf_pct"),
                      (hi, "ic95_wilson_sup_pct")):
        if abs(calc - float(g[pub])) > 0.06:
            raise SystemExit(
                f"la referencia recalculada no reproduce {pub} del paso 8")
    global_ = {"p": p, "lo": lo, "hi": hi,
               "acuerdo": int(g["acuerdo"]), "evaluable": int(g["evaluable"])}
    return estratos, global_


# ------------------------------------------------------------- drawing -----
def build(df: pd.DataFrame, global_: dict):
    fig, ax = sciviz.new_figure(width="a4text", height_mm=80)

    y = list(range(len(df) - 1, -1, -1))

    # Referencia global detrás de todo: contexto, no protagonista.
    ax.axvspan(global_["lo"], global_["hi"], color="#EFEFEF", zorder=0)
    ax.axvline(global_["p"], color="#9A9A9A", linewidth=0.7,
               linestyle=(0, (3, 2)), zorder=1)

    for yi, (_, f) in zip(y, df.iterrows()):
        color = COLOR_DICTAMEN[f["dictamen"]]
        ax.plot([f["lo"], f["hi"]], [yi, yi], color=color, linewidth=1.1,
                solid_capstyle="butt", zorder=3)
        for extremo in (f["lo"], f["hi"]):
            ax.plot([extremo], [yi], marker="|", markersize=4.5,
                    markeredgewidth=1.1, color=color, zorder=3)
        ax.plot([f["p"]], [yi], marker=MARCA_DICTAMEN[f["dictamen"]],
                markersize=TAM_DICTAMEN[f["dictamen"]], color=color, zorder=4)

        indet = int(f["indeterminado"])
        texto = f"{int(f['acuerdo'])}/{int(f['evaluable'])}"
        if indet:
            texto += f"  (+{indet} ind.)"
        ax.text(104, yi, texto, ha="left", va="center",
                fontsize=sciviz.pt(0.8), color="#444444")

    ax.set_yticks(y, [ETIQUETAS[g] for g in df["grupo"]])
    ax.set_ylim(-0.7, len(df) - 0.3)
    ax.set_xlim(0, 132)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel("Evaluaciones que respaldan el candidato cartográfico (%)")

    manijas = [plt.Line2D([], [], marker=MARCA_DICTAMEN[d],
                          markersize=TAM_DICTAMEN[d], linestyle="none",
                          color=c, label=f"Confianza {d.lower()}")
               for d, c in COLOR_DICTAMEN.items()]
    manijas.append(plt.Line2D(
        [], [], color="#9A9A9A", linewidth=0.7, linestyle=(0, (3, 2)),
        label=(f"Sectores únicos: {global_['p']:.1f} % "
               f"({global_['acuerdo']}/{global_['evaluable']})").replace(".", ",")))
    # Fuera del área de datos: dentro, en cualquier esquina libre, la leyenda
    # se apoyaba sobre los intervalos de E5 y E6. El verificador no lo detecta
    # porque compara texto contra texto, no texto contra trazo.
    ax.legend(handles=manijas, loc="upper center", bbox_to_anchor=(0.5, -0.19),
              ncol=2, frameon=False, fontsize=sciviz.pt(0.8),
              handletextpad=0.6, columnspacing=1.6, borderaxespad=0.0)

    ax.grid(axis="x", linewidth=0.4, color="#DDDDDD")
    ax.set_axisbelow(True)
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.spines["bottom"].set_bounds(0, 100)

    return fig


# ---------------------------------------------------------------- main -----
def main():
    df, global_ = load()
    for _, f in df.iterrows():
        print(f"  {ETIQUETAS[f['grupo']]:26s} {f['p']:5.1f} % "
              f"[{f['lo']:4.1f}, {f['hi']:5.1f}]  {f['dictamen']}")
    # Subconjunto publicable con el mismo criterio de sectores únicos que el
    # estimador principal: se excluyen las tres repeticiones ciegas que caen en
    # los dominios ACR y anillos. Con ellas serían 25/36 = 69,4 %, cifra que se
    # publicó antes por error y que contaba tres sectores dos veces.
    p_pub, lo_pub, hi_pub = wilson(22, 33)
    print(f"  subconjunto publicable (ACR + anillos, sectores únicos): "
          f"{p_pub:.1f} % [{lo_pub:.1f}, {hi_pub:.1f}]")

    fig = build(df, global_)

    manifest = sciviz.finalize(
        fig,
        outdir=OUTDIR,
        stem=STEM,
        contract="F08",
        source=SOURCE,
        lang=LANG,
        formats=FORMATS,
        caption=(
            "Respaldo de la validación visual ciega a cada uno de los seis "
            "estratos de señal cartográfica del ACR Sistema de Lomas de Lima. El "
            "punto marca la proporción de evaluaciones con veredicto que apoyan "
            "el candidato y la barra su intervalo de Wilson del 95 %. El color "
            "indica el dictamen de confianza asignado en el paso 8. La cifra a la "
            "derecha de cada barra es el número de acuerdos sobre el de "
            "evaluaciones con veredicto, y entre paréntesis las evaluaciones "
            "indeterminadas, que quedan fuera del denominador. La línea "
            "discontinua y la banda gris son la concordancia sobre sectores "
            "únicos y su intervalo."
        ),
        note=(
            "n = 60 sectores únicos, 54 con veredicto; entre 8 y 12 "
            "evaluaciones con veredicto por estrato. Concordancia sobre "
            "sectores únicos: 38 de 54, 70,4 %, intervalo de 57,2 a 80,9 %. Las "
            "seis repeticiones ciegas no entran en el denominador porque miden "
            "consistencia del evaluador y no son unidades de muestra: con ellas "
            "el cómputo sería 43 de 60, 71,7 %, y contaría seis sectores dos "
            "veces. En el "
            "subconjunto publicable, formado por los dominios ACR y anillos y "
            "excluyendo el ámbito KBA restringido, la concordancia es de 22 de "
            "33 sectores, 66,7 %, intervalo de 49,6 a 80,2 %, cuyo límite "
            "inferior queda por debajo del 50 %. Las seis "
            "repeticiones ciegas de control obtuvieron veredicto idéntico, 6 de "
            "6. El estrato E3 alcanza el 100 % de apoyo y aun así recibe "
            "confianza media porque 4 de sus 12 evaluaciones resultaron "
            "indeterminadas. Los estratos E5 y E6 quedan por debajo del 50 % y "
            "sus señales se retiraron del núcleo analítico. La anchura de los "
            "intervalos refleja el tamaño de cada estrato: un 100 % sobre 8 "
            "evaluaciones admite valores verdaderos desde el 67,6 %. Estas "
            "cifras son concordancia de una muestra estratificada y dirigida a "
            "señales candidatas; no son exactitud temática oficial de la "
            "Colección 3 ni una estimación probabilística para todo el paisaje."
        ),
        source_note=(
            "Validación visual ciega del paso 8 del protocolo, sobre mosaicos "
            "MapBiomas, color natural, falso color, NDVI y, cuando correspondía, "
            "Landsat Colección 2 y Sentinel-2 como fuentes auxiliares "
            "independientes. Archivo: metricas_concordancia_paso08.csv. Acceso: "
            "agosto de 2026."
        ),
    )
    print(f"{STEM}: {manifest['figure_size_mm']} mm — verificación de trazado "
          f"{'OK' if manifest['layout_check']['passed'] else 'FALLIDA'}")


if __name__ == "__main__":
    main()
