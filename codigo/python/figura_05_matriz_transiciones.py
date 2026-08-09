#!/usr/bin/env python3
"""
CONTRACT     : F05
QUESTION     : ¿Hacia qué clases se desplazó la superficie del ACR Sistema de
               Lomas de Lima, y qué proporción del cambio corresponde a la
               frontera entre clases naturales frente a la conversión urbana?
MESSAGE      : Entre 2000 y 2024 el cambio está dominado por la transición
               70 -> 68 con 2 781,5 ha, frente a 31,7 ha de 70 -> 24: por cada
               hectárea que la clase 70 cede a infraestructura urbana cede 88 a
               su clase complementaria. En el tramo reciente 2010-2024 esa
               desproporción cae a 10 y la clase 24 se alimenta sobre todo de la
               clase 68, no de la 70.
SOURCE       : 05_analisis_temporal/01_intermediate/
               transiciones_acr_15_periodos_consolidado.csv
UNIT         : hectáreas de superficie transicionada entre los dos años extremos
               de cada periodo
INCLUDES     : cinco ámbitos del ACR agregados; bandas oficiales de transición
               2000-2024 y 2010-2024; las cinco clases con flujo no nulo.
EXCLUDES     : la banda 1985-2024, porque su año inicial está excluido por
               ruptura de inicio de serie (controles 6E4 y 6E5). Anillos
               externos y KBA restringida.
PROHIBITIONS : no describir 70 -> 68 como pérdida de vegetación; no sumar la
               diagonal con lo que queda fuera de ella; no leer estas cifras
               como eventos temporales, que se miden con la regla W5 y no con
               una comparación entre dos años extremos.
VISUAL FORM  : dos matrices de calor origen x destino coordinadas, con la misma
               escala de color logarítmica y todos los valores rotulados. La
               diagonal, que es persistencia y no cambio, se representa en gris
               y queda fuera de la escala de color. Se descarta el diagrama de
               Sankey: en una página impresa las cintas se cruzan y los rótulos
               colisionan.
LIMIT        : compara los dos años extremos de cada periodo; no describe la
               trayectoria intermedia ni distingue un cambio estable de una
               oscilación que empieza y termina en clases distintas.
OUTPUT       : figura_05_matriz_transiciones_acr

Run:  python figura_05_matriz_transiciones.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sciviz
from sciviz import MM

# ---------------------------------------------------------------- paths ----
ROOT = Path(__file__).resolve().parents[3]
SOURCE = (ROOT / "05_analisis_temporal/01_intermediate/"
                 "transiciones_acr_15_periodos_consolidado.csv")
OUTDIR = ROOT / "10_comunicacion_resultados/02_final/figuras"
STEM = "figura_05_matriz_transiciones_acr"

LANG = "es"
FORMATS = ("pdf", "png")

BANDAS = [
    ("transitions_2000_2024", "2000–2024"),
    ("transitions_2010_2024", "2010–2024"),
]

# Orden de clases coherente con F04: la focal primero, la antrópica al final.
# Los ejes llevan solo el código: los nombres completos no caben en celdas de
# 14 mm, y F04 precede a esta figura en el documento estableciendo la
# correspondencia entre código, nombre y color. Los nombres se recogen en el pie.
CLASES = [
    (70, "70"),
    (68, "68"),
    (13, "13"),
    (66, "66"),
    (24, "24"),
]

C_DIAGONAL = "#E8E8E8"


def _color_texto(rgba) -> str:
    """Blanco o negro según la luminancia real del fondo de la celda.

    Un umbral fijo en hectáreas no sirve: el color depende de la normalización
    logarítmica, no del valor bruto. Coeficientes de luminancia relativa de
    la recomendación ITU-R BT.709.
    """
    r, g, b = rgba[:3]
    luminancia = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return "white" if luminancia < 0.5 else "#222222"


# ---------------------------------------------------- input assertions -----
def load() -> dict[str, pd.DataFrame]:
    df = pd.read_csv(SOURCE)
    faltan = {"banda", "from_class", "to_class", "area_ha"} - set(df.columns)
    if faltan:
        raise SystemExit(f"la fuente no trae las columnas: {sorted(faltan)}")

    codigos = [c for c, _ in CLASES]
    matrices = {}
    for banda, _ in BANDAS:
        d = df[df["banda"] == banda]
        if d.empty:
            raise SystemExit(f"la banda {banda} no está en la fuente")

        presentes = set(d["from_class"]) | set(d["to_class"])
        if not presentes <= set(codigos):
            raise SystemExit(
                f"{banda}: clases sin fila/columna asignada: "
                f"{sorted(presentes - set(codigos))}")

        m = (d.pivot_table(index="from_class", columns="to_class",
                           values="area_ha", aggfunc="sum")
               .reindex(index=codigos, columns=codigos)
               .fillna(0.0))

        # El total debe reproducir el área de grilla del ACR: la matriz reparte
        # toda la superficie, no una selección de ella.
        total = float(m.to_numpy().sum())
        if abs(total - 13468.753) > 0.5:
            raise SystemExit(f"{banda}: la matriz suma {total:.3f} ha y se "
                             f"esperaban 13 468,753 ha de grilla del ACR")
        matrices[banda] = m
    return matrices


# ------------------------------------------------------------- drawing -----
def build(matrices: dict[str, pd.DataFrame]):
    codigos = [c for c, _ in CLASES]
    etiquetas = [n for _, n in CLASES]
    n = len(codigos)

    fuera = np.concatenate([
        matrices[b].to_numpy()[~np.eye(n, dtype=bool)] for b, _ in BANDAS])
    positivos = fuera[fuera > 0]
    # La escala arranca en el flujo no nulo más pequeño: empezar por debajo
    # desperdicia rango de color en valores que no existen.
    norma = LogNorm(vmin=float(positivos.min()), vmax=float(fuera.max()))
    mapa = sciviz.sequential("YlOrBr")

    w_mm = sciviz.WIDTHS["a4text"]
    fig, axes = plt.subplots(1, 2, figsize=(w_mm * MM, 88 * MM),
                             layout="constrained")
    fig.get_layout_engine().set(w_pad=1.5 * MM, h_pad=1.5 * MM, wspace=0.06)

    for k, ((banda, periodo), ax) in enumerate(zip(BANDAS, axes)):
        m = matrices[banda].to_numpy()
        visible = np.where(np.eye(n, dtype=bool), np.nan, m)
        visible = np.where(visible == 0, np.nan, visible)

        ax.imshow(np.where(np.eye(n, dtype=bool), 1.0, np.nan),
                  cmap=matplotlib.colors.ListedColormap([C_DIAGONAL]),
                  vmin=0, vmax=1, aspect="equal")
        im = ax.imshow(visible, cmap=mapa, norm=norma, aspect="equal")

        for i in range(n):
            for j in range(n):
                v = m[i, j]
                if v == 0:
                    continue
                # Un valor por debajo de 0,05 ha se redondearía a "0,0" y se
                # leería como ausencia de flujo, que es lo contrario del dato.
                txt = ("< 0,1" if v < 0.05
                       else f"{v:,.1f}".replace(",", " ").replace(".", ","))
                color = ("#222222" if i == j
                         else _color_texto(mapa(norma(v))))
                ax.text(j, i, txt, ha="center", va="center",
                        fontsize=sciviz.pt(0.75), color=color)

        ax.set_xticks(range(n), etiquetas, fontsize=sciviz.pt())
        ax.set_yticks(range(n), etiquetas, fontsize=sciviz.pt())
        ax.set_xlabel("Clase de destino (código)")
        if k == 0:
            ax.set_ylabel("Clase de origen (código)")
        # La razón entre la salida hacia la clase complementaria y la salida
        # hacia la clase urbana es el hallazgo de la figura, y hasta ahora solo
        # estaba en el pie. Un lector que mire la matriz tiene que hacer la
        # división mentalmente entre dos celdas no contiguas. Se rotula en el
        # título, en segunda línea: a la derecha del título no cabe, y el
        # verificador de trazado lo detectó.
        i70, i68, i24 = (codigos.index(c) for c in (70, 68, 24))
        v68, v24 = m[i70, i68], m[i70, i24]
        razon = (f"70 → 68 : 70 → 24 = {v68 / v24:,.0f} : 1"
                 .replace(",", " ") if v24 > 0 else "70 → 24 nulo")
        ax.set_title(f"({chr(97 + k)}) {periodo}\n{razon}", loc="left",
                     fontsize=sciviz.pt(0.95), fontweight="bold", pad=3.0)
        ax.set_xticks(np.arange(-0.5, n, 1), minor=True)
        ax.set_yticks(np.arange(-0.5, n, 1), minor=True)
        ax.grid(which="minor", color="white", linewidth=1.2)
        ax.tick_params(which="minor", length=0)
        for lado in ax.spines.values():
            lado.set_visible(False)

    # Marcas explícitas: el localizador logarítmico por defecto genera 10⁻³ y
    # 10⁵, que caen fuera de la barra y quedan cortados por el borde.
    marcas = [t for t in (0.1, 1, 10, 100, 1000) if norma.vmin <= t <= norma.vmax]
    barra = fig.colorbar(im, ax=axes, orientation="horizontal",
                         fraction=0.05, pad=0.02, shrink=0.6, aspect=34,
                         ticks=marcas)
    barra.set_ticklabels([f"{t:g}".replace(".", ",") for t in marcas])
    barra.set_label("Superficie transicionada (ha, escala logarítmica)")
    barra.ax.tick_params(labelsize=sciviz.pt(0.8))
    barra.ax.minorticks_off()

    return fig


# ---------------------------------------------------------------- main -----
def main():
    matrices = load()
    m0 = matrices["transitions_2000_2024"]
    m1 = matrices["transitions_2010_2024"]
    for etq, m in (("2000-2024", m0), ("2010-2024", m1)):
        r = m.loc[70, 68] / m.loc[70, 24]
        print(f"  {etq}: 70->68 = {m.loc[70, 68]:8.2f} ha | "
              f"70->24 = {m.loc[70, 24]:6.2f} ha | razón = {r:5.1f}")

    fig = build(matrices)

    manifest = sciviz.finalize(
        fig,
        outdir=OUTDIR,
        stem=STEM,
        contract="F05",
        source=SOURCE,
        lang=LANG,
        formats=FORMATS,
        caption=(
            "Matrices de transición de cobertura entre los años extremos de dos "
            "periodos, para el conjunto de los cinco ámbitos del ACR Sistema de "
            "Lomas de Lima. Las filas son la clase de origen y las columnas la "
            "clase de destino. Los dos paneles comparten una única escala de "
            "color logarítmica, de modo que un mismo tono representa la misma "
            "superficie en ambos. La diagonal, sombreada en gris, corresponde a "
            "la superficie que permaneció en su clase y queda fuera de la escala "
            "de color por ser persistencia y no cambio. Todos los valores no "
            "nulos están rotulados en hectáreas. Códigos de clase: 70, Loma costera; "
            "68, Otra área natural sin vegetación; 13, Otra formación no "
            "boscosa; 66, Matorral; 24, Infraestructura urbana."
        ),
        note=(
            "n = 2 periodos; 5 clases con flujo no nulo; cada matriz reparte las "
            "13 468,753 ha del área de grilla del ACR. La transición 70 → 68 "
            "suma 2 781,5 ha en 2000-2024 frente a 31,7 ha de 70 → 24: una razón "
            "de 88 a 1. En 2010-2024 esa razón baja a 10 a 1, y la clase 24 se "
            "alimenta principalmente de la clase 68, con 63,6 ha, y no de la "
            "clase 70, con 23,9 ha. La transición entre las clases 70 y 68 "
            "corresponde a la activación o desactivación del clasificador "
            "binario de loma costera y no a una conversión de cobertura: no debe "
            "describirse como pérdida de vegetación. La banda 1985-2024 se "
            "excluye porque su año inicial es una ruptura de inicio de serie "
            "documentada. Estas cifras comparan dos años extremos y no "
            "distinguen un cambio estable de una oscilación que empieza y "
            "termina en clases distintas; los eventos estables se miden con la "
            "regla de ventana W5."
        ),
        source_note=(
            "MapBiomas Perú, Colección 3, mapa oficial de transiciones "
            "(mapbiomas_peru_collection3_transitions_v1), 30 m. Códigos de "
            "transición verificados por reconstrucción independiente desde las "
            "bandas anuales en el paso 6. Archivo: "
            "transiciones_acr_15_periodos_consolidado.csv. Acceso: agosto de 2026."
        ),
    )
    print(f"{STEM}: {manifest['figure_size_mm']} mm — verificación de trazado "
          f"{'OK' if manifest['layout_check']['passed'] else 'FALLIDA'}")


if __name__ == "__main__":
    main()
