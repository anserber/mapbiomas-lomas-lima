#!/usr/bin/env python3
"""
CONTRACT     : T03
QUESTION     : ¿Qué productos complementarios de MapBiomas se probaron, qué
               señal produjeron y por qué se incorporaron o se descartaron?
SOURCE       : 07_productos_complementarios/02_final/
               matriz_decision_productos_complementarios.csv
UNITS        : texto; hectáreas dentro de la columna de señal
OUTPUT       : tabla_03_productos_complementarios

Documenta tres resultados negativos. Su valor está en demostrar que los
productos se probaron y se descartaron con criterio, en lugar de añadirse para
aumentar el recuento de fuentes utilizadas.

Run:  python tabla_03_productos_complementarios.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tablas_comunes as tc

ROOT = Path(__file__).resolve().parents[3]
SOURCE = (ROOT / "07_productos_complementarios/02_final/"
                 "matriz_decision_productos_complementarios.csv")
OUTDIR = ROOT / "10_comunicacion_resultados/02_final/tablas"
STEM = "tabla_03_productos_complementarios"

# La fuente guarda el texto sin tildes; aquí se restituye la ortografía y se
# acortan las celdas a lo que el lector necesita leer en una tabla.
PRODUCTOS = {
    "MapBiomas Fuego - Coleccion 1": {
        "Producto": "MapBiomas Fuego, Colección 1",
        "Periodo": "2013–2024",
        "Señal medida": "0 ha quemadas y 0 años con fuego en las ocho unidades",
        "Dictamen": "Descartar",
        "Función en el trabajo": ("Resultado negativo documentado; delimita "
                                  "hasta dónde puede afirmarse ausencia de fuego"),
    },
    "Perdida de Vegetacion - reconstruccion documentada": {
        "Producto": "Pérdida de Vegetación, reconstrucción documentada",
        "Periodo": "2001–2020",
        "Señal medida": ("34,457 ha W5, de las cuales 18,453 ha coinciden con "
                         "el núcleo"),
        "Dictamen": "Contextual",
        "Función en el trabajo": ("Análisis de sensibilidad; no se suma al "
                                  "indicador principal ni lo sustituye"),
    },
    "Vegetacion Secundaria - reconstruccion documentada": {
        "Producto": "Vegetación Secundaria, reconstrucción documentada",
        "Periodo": "1985–2024",
        "Señal medida": ("0 ha con ventana W5 en las ocho unidades; señal W3 "
                         "pequeña y no robusta"),
        "Dictamen": "Descartar",
        "Función en el trabajo": ("Resultado negativo documentado; se conserva "
                                  "la prueba realizada"),
    },
}
ORDEN = list(PRODUCTOS)

UNIDADES: dict[str, str] = {}
DECIMALES: dict[str, int] = {}

CAPTION = ("Tabla 3. Productos complementarios de MapBiomas Perú evaluados para "
           "el diagnóstico, señal obtenida y decisión de incorporación.")
LABEL = "tab:complementarios"
NOTAS = [
    "Los tres productos se auditaron con el mismo procedimiento aplicado al "
    "núcleo: verificación del asset, del periodo, de la resolución y de las "
    "clases antes de medir la señal. Resolución de 30 m en los tres casos.",
    "Ninguno se incorpora como indicador adicional. Dos producen señal nula y el "
    "tercero se conserva únicamente como análisis de sensibilidad.",
    "La ausencia de área quemada cartografiada entre 2013 y 2024 no demuestra "
    "ausencia histórica de incendios fuera de ese periodo, ni ausencia de "
    "incendios pequeños por debajo del umbral de detección.",
    "La reconstrucción de Pérdida de Vegetación deriva de la propia Colección 3 "
    "y de las reglas del documento metodológico, de modo que no constituye una "
    "validación independiente ni debe citarse como módulo oficial.",
    "Fuente: paso 9 del protocolo, sobre los assets oficiales de MapBiomas Perú. "
    "Archivo matriz_decision_productos_complementarios.csv. Acceso: agosto de 2026.",
]


def load() -> pd.DataFrame:
    df = pd.read_csv(SOURCE)
    if set(df["producto"]) != set(ORDEN):
        raise SystemExit(
            "los productos de la fuente no son los tres esperados: "
            f"{sorted(set(df['producto']))}")

    # El dictamen mostrado debe coincidir con el registrado en la matriz.
    origen = df.set_index("producto")["dictamen"].str.upper().to_dict()
    for clave, fila in PRODUCTOS.items():
        if origen[clave] != fila["Dictamen"].upper():
            raise SystemExit(
                f"{clave}: la tabla dice {fila['Dictamen']!r} y la matriz "
                f"registra {origen[clave]!r}")

    if not (df["resolucion"].str.strip() == "30 m").all():
        raise SystemExit("la nota declara 30 m para los tres y la fuente no lo confirma")

    return pd.DataFrame([PRODUCTOS[k] for k in ORDEN])


def main():
    df = load()
    tc.escribir(df, outdir=OUTDIR, stem=STEM, caption=CAPTION, label=LABEL,
                unidades=UNIDADES, decimales=DECIMALES, notas=NOTAS)


if __name__ == "__main__":
    main()
