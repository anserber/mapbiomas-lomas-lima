#!/usr/bin/env python3
"""Valida el CSV de indicadores del Paso 5 sin modificarlo."""

from __future__ import annotations

import csv
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path


EXPECTED_IDS = {
    "amancaes",
    "ancon",
    "carabayllo_1",
    "carabayllo_2",
    "villa_maria",
}
EXPECTED_YEARS = set(range(1985, 2025))
EXPECTED_COLUMNS = [
    "id_ambito",
    "nombre",
    "year",
    "area_ref_ha",
    "area_utm_ha",
    "area_pixeles_ha",
    "dif_pix_utm_ha",
    "dif_pix_utm_abs_pct",
    "loma_ha",
    "loma_pct_ambito",
    "urbano_ha",
    "urbano_pct_ambito",
    "otras_clases_ha",
    "otras_clases_pct_ambito",
    "clasificada_ha",
    "sin_dato_ha",
    "sin_dato_pct",
]
NUMERIC_COLUMNS = EXPECTED_COLUMNS[2:]
NONNEGATIVE_COLUMNS = {
    "area_ref_ha",
    "area_utm_ha",
    "area_pixeles_ha",
    "dif_pix_utm_abs_pct",
    "loma_ha",
    "loma_pct_ambito",
    "urbano_ha",
    "urbano_pct_ambito",
    "otras_clases_ha",
    "otras_clases_pct_ambito",
    "clasificada_ha",
    "sin_dato_ha",
    "sin_dato_pct",
}
PERCENT_COLUMNS = {
    "dif_pix_utm_abs_pct",
    "loma_pct_ambito",
    "urbano_pct_ambito",
    "otras_clases_pct_ambito",
    "sin_dato_pct",
}


def close(a: float, b: float, tolerance: float = 1e-7) -> bool:
    return abs(a - b) <= tolerance


def main(path_string: str) -> int:
    path = Path(path_string)
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []
        raw_rows = list(reader)

    errors: list[str] = []
    warnings: list[str] = []

    if fieldnames != EXPECTED_COLUMNS:
        errors.append(
            f"Esquema inesperado: {fieldnames!r}; esperado: {EXPECTED_COLUMNS!r}"
        )

    rows: list[dict[str, object]] = []
    blank_counts = Counter()
    invalid_numeric = Counter()

    for index, raw in enumerate(raw_rows, start=2):
        for column in EXPECTED_COLUMNS:
            if raw.get(column, "") == "":
                blank_counts[column] += 1

        parsed: dict[str, object] = {
            "id_ambito": raw.get("id_ambito", "").strip(),
            "nombre": raw.get("nombre", "").strip(),
        }

        for column in NUMERIC_COLUMNS:
            try:
                value = float(raw[column])
            except (KeyError, TypeError, ValueError):
                invalid_numeric[column] += 1
                value = math.nan
            parsed[column] = value

        year_value = parsed["year"]
        if isinstance(year_value, float) and math.isfinite(year_value):
            if not year_value.is_integer():
                errors.append(f"Fila {index}: año no entero {year_value}")
            parsed["year"] = int(year_value)

        rows.append(parsed)

    keys = [(row["id_ambito"], row["year"]) for row in rows]
    key_counts = Counter(keys)
    duplicate_keys = [key for key, count in key_counts.items() if count > 1]

    ids = {str(row["id_ambito"]) for row in rows}
    years = {int(row["year"]) for row in rows if isinstance(row["year"], int)}
    by_id = defaultdict(list)
    names_by_id = defaultdict(set)
    for row in rows:
        by_id[str(row["id_ambito"])].append(row)
        names_by_id[str(row["id_ambito"])].add(str(row["nombre"]))

    if len(rows) != 200:
        errors.append(f"Filas: {len(rows)}; esperado: 200")
    if duplicate_keys:
        errors.append(f"Claves ámbito-año duplicadas: {duplicate_keys!r}")
    if ids != EXPECTED_IDS:
        errors.append(f"Ámbitos: {sorted(ids)!r}; esperados: {sorted(EXPECTED_IDS)!r}")
    if years != EXPECTED_YEARS:
        errors.append(
            f"Años ausentes/adicionales: faltan={sorted(EXPECTED_YEARS - years)!r}, "
            f"adicionales={sorted(years - EXPECTED_YEARS)!r}"
        )
    if blank_counts:
        errors.append(f"Campos vacíos: {dict(blank_counts)!r}")
    if invalid_numeric:
        errors.append(f"Valores numéricos inválidos: {dict(invalid_numeric)!r}")

    for identifier in sorted(EXPECTED_IDS):
        id_years = {int(row["year"]) for row in by_id[identifier]}
        if len(by_id[identifier]) != 40 or id_years != EXPECTED_YEARS:
            errors.append(
                f"{identifier}: {len(by_id[identifier])} filas y "
                f"{len(id_years)} años distintos"
            )
        if len(names_by_id[identifier]) != 1:
            errors.append(
                f"{identifier}: nombres inconsistentes "
                f"{sorted(names_by_id[identifier])!r}"
            )

    formula_failures = Counter()
    range_failures = Counter()
    for row in rows:
        for column in NUMERIC_COLUMNS:
            value = float(row[column])
            if not math.isfinite(value):
                range_failures[f"{column}:no_finito"] += 1
        for column in NONNEGATIVE_COLUMNS:
            if float(row[column]) < -1e-9:
                range_failures[f"{column}:negativo"] += 1
        for column in PERCENT_COLUMNS:
            value = float(row[column])
            if value < -1e-9 or value > 100 + 1e-7:
                range_failures[f"{column}:fuera_0_100"] += 1

        area_utm = float(row["area_utm_ha"])
        area_pixels = float(row["area_pixeles_ha"])
        classified = float(row["clasificada_ha"])
        no_data = float(row["sin_dato_ha"])
        loma = float(row["loma_ha"])
        urban = float(row["urbano_ha"])
        other = float(row["otras_clases_ha"])
        diff = float(row["dif_pix_utm_ha"])

        tests = {
            "pixeles=clasificada+sin_dato": close(
                area_pixels, classified + no_data
            ),
            "clasificada=loma+urbano+otras": close(
                classified, loma + urban + other
            ),
            "diferencia=pixeles-utm": close(diff, area_pixels - area_utm),
            "dif_pct": close(
                float(row["dif_pix_utm_abs_pct"]),
                abs(diff) / area_utm * 100,
            ),
            "loma_pct": close(
                float(row["loma_pct_ambito"]), loma / area_utm * 100
            ),
            "urbano_pct": close(
                float(row["urbano_pct_ambito"]), urban / area_utm * 100
            ),
            "otras_pct": close(
                float(row["otras_clases_pct_ambito"]), other / area_utm * 100
            ),
            "sin_dato_pct": close(
                float(row["sin_dato_pct"]),
                no_data / area_pixels * 100 if area_pixels else 0,
            ),
        }
        for name, passed in tests.items():
            if not passed:
                formula_failures[name] += 1

    constant_failures = {}
    for identifier, id_rows in sorted(by_id.items()):
        for column in (
            "area_ref_ha",
            "area_utm_ha",
            "area_pixeles_ha",
            "dif_pix_utm_ha",
            "dif_pix_utm_abs_pct",
        ):
            values = {round(float(row[column]), 10) for row in id_rows}
            if len(values) != 1:
                constant_failures[f"{identifier}:{column}"] = len(values)

    ordered_rows = sorted(rows, key=lambda row: (str(row["id_ambito"]), int(row["year"])))
    jumps = []
    urban_declines = []
    previous_by_id = {}
    for row in ordered_rows:
        identifier = str(row["id_ambito"])
        previous = previous_by_id.get(identifier)
        if previous is not None:
            loma_change = float(row["loma_pct_ambito"]) - float(
                previous["loma_pct_ambito"]
            )
            urban_change = float(row["urbano_pct_ambito"]) - float(
                previous["urbano_pct_ambito"]
            )
            jumps.append(
                {
                    "id_ambito": identifier,
                    "from_year": int(previous["year"]),
                    "to_year": int(row["year"]),
                    "loma_change_pp": loma_change,
                    "abs_loma_change_pp": abs(loma_change),
                }
            )
            if urban_change < -1e-9:
                urban_declines.append(
                    {
                        "id_ambito": identifier,
                        "from_year": int(previous["year"]),
                        "to_year": int(row["year"]),
                        "urban_change_pp": urban_change,
                    }
                )
        previous_by_id[identifier] = row

    jumps.sort(key=lambda item: item["abs_loma_change_pp"], reverse=True)

    max_loma = max(rows, key=lambda row: float(row["loma_pct_ambito"]))
    max_urban = max(rows, key=lambda row: float(row["urbano_pct_ambito"]))
    max_no_data = max(rows, key=lambda row: float(row["sin_dato_pct"]))
    max_pixel_diff = max(rows, key=lambda row: float(row["dif_pix_utm_abs_pct"]))

    pilot_loma = next(
        row
        for row in rows
        if row["id_ambito"] == "carabayllo_2" and row["year"] == 2000
    )
    pilot_urban = next(
        row
        for row in rows
        if row["id_ambito"] == "carabayllo_1" and row["year"] == 2024
    )
    if not close(float(pilot_loma["loma_pct_ambito"]), 97.5478532921757):
        errors.append("No coincide el máximo piloto de loma")
    if not close(float(pilot_urban["urbano_pct_ambito"]), 18.929779225988465):
        errors.append("No coincide el máximo piloto urbano")

    if range_failures:
        errors.append(f"Rangos inválidos: {dict(range_failures)!r}")
    if formula_failures:
        errors.append(f"Fórmulas inconsistentes: {dict(formula_failures)!r}")
    if constant_failures:
        errors.append(f"Superficies no constantes: {constant_failures!r}")

    result = {
        "path": str(path),
        "rows": len(rows),
        "columns": len(fieldnames),
        "unique_keys": len(key_counts),
        "duplicate_keys": len(duplicate_keys),
        "ids": sorted(ids),
        "years": [min(years), max(years)] if years else [],
        "rows_per_id": {
            identifier: len(by_id[identifier]) for identifier in sorted(by_id)
        },
        "blank_counts": dict(blank_counts),
        "invalid_numeric": dict(invalid_numeric),
        "formula_failures": dict(formula_failures),
        "range_failures": dict(range_failures),
        "constant_failures": constant_failures,
        "max_loma": {
            key: max_loma[key]
            for key in (
                "id_ambito",
                "nombre",
                "year",
                "loma_ha",
                "loma_pct_ambito",
            )
        },
        "max_urban": {
            key: max_urban[key]
            for key in (
                "id_ambito",
                "nombre",
                "year",
                "urbano_ha",
                "urbano_pct_ambito",
            )
        },
        "max_no_data_pct": max_no_data["sin_dato_pct"],
        "max_pixel_difference_pct": max_pixel_diff["dif_pix_utm_abs_pct"],
        "top_loma_jumps": jumps[:10],
        "urban_decline_count": len(urban_declines),
        "top_urban_declines": sorted(
            urban_declines, key=lambda item: item["urban_change_pp"]
        )[:10],
        "warnings": warnings,
        "errors": errors,
        "status": "PASS" if not errors else "FAIL",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(f"Uso: {sys.argv[0]} ruta.csv")
    raise SystemExit(main(sys.argv[1]))
