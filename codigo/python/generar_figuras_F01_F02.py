#!/usr/bin/env python3
"""Genera F01 y F02 del Paso 12 desde resultados publicos aprobados.

La logica grafica se implementa en SVG para no depender de librerias graficas
externas. Un conversor separado produce PNG y PDF sin modificar el contenido.
"""

from __future__ import annotations

import csv
import json
import math
import argparse
from html import escape
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
SERIE = ROOT / "04_extraccion_series/02_resultados/00_raw/serie_indicadores_acr_1985_2024.csv"
MAESTRA = ROOT / "09_integracion_resultados/02_final/tabla_maestra_resultados_publicos.csv"
INTERMEDIATE = ROOT / "10_comunicacion_resultados/01_intermediate"
OUT = ROOT / "10_comunicacion_resultados/02_final/figuras"
EVIDENCE = ROOT / "10_comunicacion_resultados/evidencia"

BLUE = "#1F5A7A"
BLUE_DARK = "#153E54"
ORANGE = "#D97721"
CHARCOAL = "#263238"
MID = "#66757F"
GRID = "#D9E1E5"
LIGHT = "#F4F7F8"
WHITE = "#FFFFFF"


def text(x, y, value, size=24, fill=CHARCOAL, weight=400, anchor="start", **extra):
    attrs = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in extra.items())
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-family="Arial, Helvetica, sans-serif" '
        f'font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" {attrs}>'
        f'{escape(str(value))}</text>'
    )


def line(x1, y1, x2, y2, stroke=GRID, width=1, dash=None):
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    return (
        f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
        f'stroke="{stroke}" stroke-width="{width}"{dash_attr}/>'
    )


def circle(cx, cy, r, fill, stroke="none", width=0):
    return (
        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{fill}" '
        f'stroke="{stroke}" stroke-width="{width}"/>'
    )


def svg_document(width, height, elements):
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">\n'
        f'<rect width="{width}" height="{height}" fill="{WHITE}"/>\n'
        + "\n".join(elements)
        + "\n</svg>\n"
    )


def assert_inputs(series, master):
    expected_years = list(range(1985, 2025))
    if len(series) != 200:
        raise ValueError(f"F01: se esperaban 200 filas y se encontraron {len(series)}")
    if sorted(series["year"].astype(int).unique().tolist()) != expected_years:
        raise ValueError("F01: los anos no forman la serie completa 1985-2024")
    if series["id_ambito"].nunique() != 5:
        raise ValueError("F01: se esperaban cinco ambitos")
    counts = series.groupby("id_ambito")["year"].nunique()
    if not (counts == 40).all():
        raise ValueError("F01: cada ambito debe tener 40 anos")
    if series.duplicated(["id_ambito", "year"]).any():
        raise ValueError("F01: existen pares id_ambito-year duplicados")
    if not series["loma_pct_ambito"].between(0, 100).all():
        raise ValueError("F01: porcentaje de clase 70 fuera de 0-100")

    acr = master.loc[master["dominio"].eq("ACR")].copy()
    if len(acr) != 5 or acr["unidad_id"].nunique() != 5:
        raise ValueError("F02: la tabla maestra no contiene cinco ACR unicos")
    for col in ["area_70_2024_pct", "area_siempre70_pct"]:
        if not acr[col].between(0, 1).all():
            raise ValueError(f"F02: {col} debe estar expresado como proporcion 0-1")
    if (acr["area_siempre70_pct"] - acr["area_70_2024_pct"] > 1e-9).any():
        raise ValueError("F02: la persistencia completa no puede superar clase 70 en 2024")
    return acr


def figure_01(series):
    # Diseño de publicación: el nombre de cada ámbito ocupa una línea propia.
    # Las etiquetas de la escala quedan en una columna separada y nunca
    # comparten espacio con los nombres de los ámbitos.
    width, height = 1800, 1660
    left, right = 250, 1640
    top = 290
    panel_h, gap = 215, 18
    title_h, plot_h = 34, 148
    order = ["amancaes", "villa_maria", "carabayllo_2", "ancon", "carabayllo_1"]
    labels = dict(series[["id_ambito", "nombre"]].drop_duplicates().values)
    events = {"ancon": (2001, "ruptura 2000–2001"), "carabayllo_2": (2015, "ruptura 2014–2015")}
    xticks = [1985, 1990, 2000, 2010, 2020, 2024]
    yticks = [0, 25, 50, 75, 100]

    el = [
        text(90, 70, "Cobertura anual de loma costera (clase 70), 1985–2024", 36, BLUE_DARK, 700),
        text(90, 112, "Cinco ámbitos del ACR Sistema de Lomas de Lima · porcentaje del área de grilla", 22, MID),
        line(90, 148, 1710, 148, GRID, 2),
        line(98, 194, 140, 194, BLUE, 5),
        text(154, 202, "Serie anual", 19, MID),
        line(322, 194, 364, 194, ORANGE, 3, "8 6"),
        text(378, 202, "Ruptura cartográfica conocida", 19, MID),
        text(58, 905, "Área de grilla clasificada como clase 70 (%)", 19, MID, 600,
             anchor="middle", transform="rotate(-90 58 905)"),
    ]

    def x(year):
        return left + (year - 1985) / 39 * (right - left)

    for i, ident in enumerate(order):
        y0 = top + i * (panel_h + gap)
        plot_top = y0 + title_h
        bottom = plot_top + plot_h
        sub = series.loc[series["id_ambito"].eq(ident)].sort_values("year")
        el.append(text(left, y0 + 21, labels[ident], 21, CHARCOAL, 700))
        for tick in yticks:
            yy = bottom - tick / 100 * plot_h
            el.append(line(left, yy, right, yy, GRID, 1))
            el.append(text(left - 16, yy + 6, tick, 16, MID, anchor="end"))
        points = []
        for row in sub.itertuples():
            xx = x(int(row.year))
            yy = bottom - float(row.loma_pct_ambito) / 100 * plot_h
            points.append(f"{xx:.1f},{yy:.1f}")
        el.append(f'<polyline points="{" ".join(points)}" fill="none" stroke="{BLUE}" stroke-width="4" stroke-linejoin="round" stroke-linecap="round"/>')
        for xx, yy in (tuple(map(float, p.split(","))) for p in points):
            el.append(circle(xx, yy, 2.4, BLUE))
        if ident in events:
            year, label = events[ident]
            xx = x(year)
            el.append(line(xx, plot_top, xx, bottom, ORANGE, 2, "7 5"))
            # La anotación se sitúa dentro de la parte superior del panel,
            # separada del nombre del ámbito.
            el.append(text(xx + 8, plot_top + 18, label, 15, ORANGE, 600))
        if i == len(order) - 1:
            for tick in xticks:
                xx = x(tick)
                el.append(line(xx, bottom, xx, bottom + 8, MID, 1))
                el.append(text(xx, bottom + 34, tick, 18, MID, anchor="middle"))
        last = sub.iloc[-1]
        el.append(text(right + 12, bottom - float(last["loma_pct_ambito"]) / 100 * plot_h + 7,
                       f'{last["loma_pct_ambito"]:.1f} %', 18, BLUE_DARK, 700))

    el.extend([
        line(90, 1534, 1710, 1534, GRID, 1),
        text(90, 1575, "Nota:", 18, CHARCOAL, 700),
        text(151, 1575, "la serie representa clasificación cartográfica anual; no demuestra por sí sola condición o pérdida ecológica.", 18, MID),
        text(90, 1615, "Fuente: MapBiomas Perú, Colección 3. Clase 70 = Loma costera (producto beta). Elaboración propia.", 16, MID),
    ])
    return svg_document(width, height, el)


def figure_02(acr):
    data = acr.copy()
    data["actual_pct"] = data["area_70_2024_pct"] * 100
    data["persist_pct"] = data["area_siempre70_pct"] * 100
    data["gap_pp"] = data["actual_pct"] - data["persist_pct"]
    data = data.sort_values("actual_pct", ascending=False).reset_index(drop=True)

    width, height = 1600, 960
    label_x, main_l, main_r = 70, 390, 1070
    values_x = 1095
    gap_l, gap_r = 1335, 1490
    top, row_gap = 330, 102
    max_gap = max(0.7, math.ceil(data["gap_pp"].max() * 10) / 10)
    el = [
        text(70, 68, "Clase 70 en 2024 y persistencia durante 1985–2024", 34, BLUE_DARK, 700),
        text(70, 112, "Porcentaje del área de grilla en los cinco ámbitos del ACR Sistema de Lomas de Lima", 21, MID),
        line(65, 152, 1530, 152, GRID, 2),
        circle(80, 202, 8, BLUE),
        text(99, 210, "Clase 70 en 2024", 21, MID),
        circle(350, 202, 8, WHITE, ORANGE, 4),
        text(369, 210, "Siempre clase 70 en 1985–2024", 21, MID),
        text((main_l + main_r) / 2, 250, "Porcentaje del área de grilla", 18, MID, 600, anchor="middle"),
        text(values_x, 250, "Persistente | 2024", 16, MID, 600),
        text((gap_l + gap_r) / 2, 250, "Brecha (p.p.)", 17, MID, 600, anchor="middle"),
    ]

    def mx(v):
        return main_l + v / 100 * (main_r - main_l)

    def gx(v):
        return gap_l + v / max_gap * (gap_r - gap_l)

    for tick in [0, 25, 50, 75, 100]:
        xx = mx(tick)
        el.append(line(xx, top - 35, xx, top + row_gap * 4 + 35, GRID, 1))
        el.append(text(xx, top - 50, tick, 18, MID, anchor="middle"))
    for tick in [0, max_gap / 2, max_gap]:
        xx = gx(tick)
        el.append(line(xx, top - 35, xx, top + row_gap * 4 + 35, GRID, 1))
        el.append(text(xx, top - 50, f"{tick:.1f}", 18, MID, anchor="middle"))

    for i, row in data.iterrows():
        yy = top + i * row_gap
        p = float(row["persist_pct"])
        a = float(row["actual_pct"])
        gap = float(row["gap_pp"])
        el.append(text(label_x, yy + 8, row["nombre"], 21, CHARCOAL, 600))
        el.append(line(mx(p), yy, mx(a), yy, GRID, 5))
        el.append(circle(mx(p), yy, 9, WHITE, ORANGE, 4))
        el.append(circle(mx(a), yy, 8, BLUE))
        el.append(text(values_x, yy + 7, f"{p:.2f} % | {a:.2f} %", 16, MID))
        el.append(line(gap_l, yy, gx(gap), yy, ORANGE, 5))
        el.append(circle(gx(gap), yy, 7, ORANGE))
        el.append(text(gap_r + 12, yy + 7, f"{gap:.2f}", 18, ORANGE, 700))

    el.extend([
        text(70, 848, "Definición:", 18, CHARCOAL, 700),
        text(167, 848, "persistente = píxeles clasificados como clase 70 en cada uno de los 40 años.", 18, MID),
        text(70, 880, "Lectura:", 18, CHARCOAL, 700),
        text(145, 880, "la brecha cuantifica estabilidad cartográfica; no mide por sí sola condición ni calidad ecológica.", 18, MID),
        text(70, 918, "Fuente: MapBiomas Perú, Colección 3. Clase 70 = Loma costera (producto beta). Elaboración propia.", 16, MID),
    ])
    return svg_document(width, height, el), data


def main():
    parser = argparse.ArgumentParser(description="Genera las figuras F01 y F02 del Paso 12")
    parser.add_argument(
        "--figure",
        choices=["F01", "F02", "all"],
        default="all",
        help="Permite revisar una figura por vez sin sobrescribir la otra.",
    )
    args = parser.parse_args()
    INTERMEDIATE.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    series = pd.read_csv(SERIE)
    master = pd.read_csv(MAESTRA)
    acr = assert_inputs(series, master)

    f01_svg = OUT / "figura_01_serie_clase70_acr_1985_2024.svg"
    f02_svg = OUT / "figura_02_clase70_2024_vs_siempre70.svg"
    if args.figure in {"F01", "all"}:
        f01_svg.write_text(figure_01(series), encoding="utf-8")
    f02, f02_data = figure_02(acr)
    if args.figure in {"F02", "all"}:
        f02_svg.write_text(f02, encoding="utf-8")

    series[["id_ambito", "nombre", "year", "loma_ha", "loma_pct_ambito"]].to_csv(
        INTERMEDIATE / "datos_figura_01_serie_clase70.csv", index=False
    )
    f02_data[["unidad_id", "nombre", "area_grilla_ha", "persist_pct", "actual_pct", "gap_pp"]].to_csv(
        INTERMEDIATE / "datos_figura_02_clase70_2024_vs_siempre70.csv", index=False
    )

    qa = {
        "F01": {
            "filas": int(len(series)),
            "ambitos": int(series["id_ambito"].nunique()),
            "anos": int(series["year"].nunique()),
            "rango_anos": [int(series["year"].min()), int(series["year"].max())],
            "duplicados_id_year": int(series.duplicated(["id_ambito", "year"]).sum()),
            "pct_min": float(series["loma_pct_ambito"].min()),
            "pct_max": float(series["loma_pct_ambito"].max()),
        },
        "F02": {
            "filas_acr": int(len(acr)),
            "brecha_min_pp": float(f02_data["gap_pp"].min()),
            "brecha_max_pp": float(f02_data["gap_pp"].max()),
            "persistencia_mayor_actual": int((f02_data["persist_pct"] > f02_data["actual_pct"] + 1e-9).sum()),
        },
    }
    (EVIDENCE / "control_datos_F01_F02.json").write_text(
        json.dumps(qa, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(qa, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
