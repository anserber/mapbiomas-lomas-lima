#!/usr/bin/env python3
"""
CONTRACT     : T02
QUESTION     : ¿Qué discontinuidades cartográficas de la serie están
               documentadas, en qué unidad y periodo, con qué magnitud y por
               qué causa?
SOURCE       : 05_analisis_temporal/evidencia/
               dictamen_ruptura_1985_y_regimenes_sensor.md, que consolida los
               controles 6E4, 6E3 y 6F2. Las cifras se transcriben aquí y se
               contrastan con los CSV de origen en la comprobación.
UNITS        : hectáreas
OUTPUT       : tabla_02_rupturas_conocidas

Es la tabla que convierte una limitación en un producto: enumera lo que el
diagnóstico sabe que su propio insumo hace mal, con evidencia y magnitud.

Run:  python tabla_02_rupturas_conocidas.py
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tablas_comunes as tc

ROOT = Path(__file__).resolve().parents[3]
FUENTE_TRANSICIONES = (ROOT / "05_analisis_temporal/01_intermediate/"
                              "resumen_transiciones_acr_paso06.csv")
OUTDIR = ROOT / "10_comunicacion_resultados/02_final/tablas"
STEM = "tabla_02_rupturas_conocidas"

RUPTURAS = [
    {
        "Identificador": "Inicio de serie 68→70",
        "Unidad": "Ancón",
        "Periodo": "1985–1986",
        "Superficie": 1242.401,
        "Causa documentada": ("Mosaico del primer año construido con 17 escenas "
                              "Landsat y 58 % de nubosidad, los peores valores "
                              "de la serie"),
    },
    {
        "Identificador": "Cambio temático 70→68",
        "Unidad": "Ancón",
        "Periodo": "2000–2001",
        "Superficie": 532.735,
        "Causa documentada": ("Reasignación temática sincrónica sin "
                              "contrapartida espectral; el NDVI aumenta un "
                              "1,7 % mientras la clase desaparece"),
    },
    {
        "Identificador": "CV-042, 70→13/68",
        "Unidad": "Carabayllo 2",
        "Periodo": "2014–2015",
        "Superficie": 10.734,
        "Causa documentada": ("Ruptura estable hacia clases naturales, sin "
                              "transformación física visible en los mosaicos"),
    },
]

UNIDADES = {"Superficie": "ha"}
DECIMALES = {"Superficie": 3}

CAPTION = ("Tabla 2. Discontinuidades cartográficas documentadas en la serie "
           "1985-2024 de la clase 70 — Loma costera dentro del ACR Sistema de "
           "Lomas de Lima.")
LABEL = "tab:rupturas"
NOTAS = [
    "Una ruptura cartográfica es un cambio de clase estable y sincrónico que no "
    "presenta contrapartida en los índices espectrales ni transformación visible "
    "en los mosaicos. Se identifica con cuatro criterios: sincronía, ausencia de "
    "retorno, ausencia de señal espectral y calidad del insumo.",
    "La ruptura de 1985–1986 es la de mayor magnitud de las tres y afecta a la "
    "línea base del conjunto del área de estudio: la clase 70 del ACR completo "
    "varía un +31,9 % entre el primer y el segundo año de la serie. Por ese "
    "motivo 1985 queda excluido de todo cálculo de cambio.",
    "Ninguna de las tres debe interpretarse como pérdida de vegetación, "
    "degradación ni error de la geometría oficial del ACR. La transición entre "
    "las clases 70 y 68 corresponde a la activación o desactivación del "
    "clasificador binario de loma costera.",
    "Las superficies se excluyen de los totales de cambio interpretado.",
    "Fuente: controles 6E4, 6E3 y 6F2 del protocolo, sobre MapBiomas Perú "
    "Colección 3 (1985-2024), 30 m, y los mosaicos Landsat oficiales. Acceso: "
    "agosto de 2026.",
]


def load() -> pd.DataFrame:
    """Contrasta las magnitudes transcritas con el CSV de transiciones del paso 6.

    La tabla se redacta a mano porque su columna de causa es interpretación
    documentada, pero las cifras no pueden divergir de la fuente calculada.
    """
    filas = list(csv.DictReader(open(FUENTE_TRANSICIONES, encoding="utf-8")))

    def area(id_ambito, banda, campo):
        for f in filas:
            if f["id_ambito"] == id_ambito and f["banda"] == banda:
                return float(f[campo])
        raise SystemExit(f"no se encontró {id_ambito} / {banda} en la fuente")

    # La ruptura de 2000-2001 es el componente 70→68 en concreto, no la salida
    # total de la clase 70: ese año salieron 532,822 ha, de las cuales 0,087 ha
    # fueron a otra clase natural distinta de la 68.
    controles = [
        ("Ancón", "1985–1986",
         area("ancon", "transitions_1985_1986", "entrada_clase_loma_ha")),
        ("Ancón", "2000–2001",
         area("ancon", "transitions_2000_2001", "intercambio_68_70_ha")),
    ]
    for (_, periodo, calculado) in controles:
        declarado = next(r["Superficie"] for r in RUPTURAS if r["Periodo"] == periodo)
        if abs(calculado - declarado) > 0.01:
            raise SystemExit(
                f"{periodo}: la tabla declara {declarado} ha y la fuente "
                f"calcula {calculado:.3f} ha")

    return pd.DataFrame(RUPTURAS)


def main():
    df = load()
    tc.escribir(df, outdir=OUTDIR, stem=STEM, caption=CAPTION, label=LABEL,
                unidades=UNIDADES, decimales=DECIMALES, notas=NOTAS)


if __name__ == "__main__":
    main()
