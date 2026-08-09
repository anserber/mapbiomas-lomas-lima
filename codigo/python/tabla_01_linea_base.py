#!/usr/bin/env python3
"""
CONTRACT     : T01
QUESTION     : ¿Cuáles son los valores exactos de superficie y de señal urbana
               de cada unidad pública del diagnóstico?
SOURCE       : 09_integracion_resultados/02_final/
               tabla_maestra_resultados_publicos_v2.csv
UNITS        : hectáreas; hectáreas-evento
OUTPUT       : tabla_01_linea_base_por_unidad

Es la tabla de consulta del trabajo: las figuras F06 y F07 sirven para comparar
magnitudes, pero el texto necesita citar cifras exactas y ninguna figura las da.

Run:  python tabla_01_linea_base.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tablas_comunes as tc

ROOT = Path(__file__).resolve().parents[3]
SOURCE = (ROOT / "09_integracion_resultados/02_final/"
                 "tabla_maestra_resultados_publicos_v2.csv")
OUTDIR = ROOT / "10_comunicacion_resultados/02_final/tablas"
STEM = "tabla_01_linea_base_por_unidad"

NOMBRES = {
    "acr|ancon":         "Ancón",
    "acr|villa_maria":   "Villa María",
    "acr|amancaes":      "Amancaes",
    "acr|carabayllo_1":  "Carabayllo 1",
    "acr|carabayllo_2":  "Carabayllo 2",
    "sistema|0_500":     "Anillo 0–500 m",
    "sistema|500_1000":  "Anillo 500–1 000 m",
    "sistema|1000_2000": "Anillo 1 000–2 000 m",
}
ORDEN = list(NOMBRES)

COLUMNAS = {
    "nombre_publico":                    "Unidad",
    "area_grilla_ha":                    "Área de grilla",
    "area_70_1986_ha":                   "Clase 70 en 1986",
    "area_70_2024_ha":                   "Clase 70 en 2024",
    "area_siempre70_ha":                 "Núcleo persistente",
    "w5_urbano_ha_evento":               "Urbano W5 confirmado",
    "censura_urbano_2021_2024_ha_evento": "Urbano reciente censurado",
}

UNIDADES = {
    "Área de grilla": "ha",
    "Clase 70 en 1986": "ha",
    "Clase 70 en 2024": "ha",
    "Núcleo persistente": "ha",
    "Urbano W5 confirmado": "ha-evento",
    "Urbano reciente censurado": "ha-evento",
}

# Tres decimales en las señales urbanas porque el texto cita valores como
# 0,905 ha-evento; una cifra en superficies, donde la precisión del píxel de
# 30 m no sostiene más.
DECIMALES = {
    "Área de grilla": 1,
    "Clase 70 en 1986": 1,
    "Clase 70 en 2024": 1,
    "Núcleo persistente": 1,
    "Urbano W5 confirmado": 3,
    "Urbano reciente censurado": 3,
}

CAPTION = ("Tabla 1. Superficie y señal urbana cartográfica de las ocho unidades "
           "públicas del ACR Sistema de Lomas de Lima y su periferia externa, "
           "según MapBiomas Perú Colección 3.")
LABEL = "tab:linea-base"
NOTAS = [
    "El área de grilla es la superficie de los píxeles MapBiomas dentro de cada "
    "unidad y es el denominador de todas las tasas publicadas. Difiere de la "
    "superficie vectorial del polígono en menos del 0,06 %.",
    "La clase 70 de 1986 es la línea base del estudio: 1985 queda excluido por "
    "ruptura de inicio de serie documentada en los controles 6E4 y 6E5.",
    "El núcleo persistente es la superficie clasificada como clase 70 en todos "
    "los años de la serie.",
    "Las dos últimas columnas no deben sumarse: la señal W5 está confirmada con "
    "ventana completa 1990-2020 y confianza alta, y la censurada corresponde a "
    "salidas de la clase 70 registradas entre 2021 y 2024, que no pueden "
    "completar esa ventana antes del final de la serie. "
    "La unidad ha-evento suma superficie por evento temporal y no equivale a "
    "superficie física única.",
    "Los tres anillos son disjuntos y disueltos para todo el sistema; los anillos "
    "por ámbito se solapan entre sí y no admiten totales.",
    "Fuente: MapBiomas Perú, Colección 3 (1985-2024), 30 m. Archivo "
    "tabla_maestra_resultados_publicos_v2.csv. Acceso: agosto de 2026.",
]


def load() -> pd.DataFrame:
    df = pd.read_csv(SOURCE)
    faltan = set(COLUMNAS) - set(df.columns) - {"nombre_publico"}
    if faltan:
        raise SystemExit(f"la fuente no trae las columnas: {sorted(faltan)}")
    if set(df["unidad_id"]) != set(ORDEN):
        raise SystemExit("las unidades de la fuente no son las ocho esperadas")

    df["nombre_publico"] = df["unidad_id"].map(NOMBRES)
    df = df.set_index("unidad_id").loc[ORDEN].reset_index()

    # Control de totales del ACR contra el dictamen del paso 10.
    acr = df[df["dominio"] == "ACR"]
    for col, esperado in (("area_grilla_ha", 13468.753),
                          ("area_siempre70_ha", 3542.972),
                          ("area_70_2024_ha", 3547.650)):
        if abs(acr[col].sum() - esperado) > 0.01:
            raise SystemExit(f"el total ACR de {col} no reproduce {esperado}")

    return df.rename(columns=COLUMNAS)[list(COLUMNAS.values())]


def main():
    df = load()
    tc.escribir(df, outdir=OUTDIR, stem=STEM, caption=CAPTION, label=LABEL,
                unidades=UNIDADES, decimales=DECIMALES, notas=NOTAS)


if __name__ == "__main__":
    main()
