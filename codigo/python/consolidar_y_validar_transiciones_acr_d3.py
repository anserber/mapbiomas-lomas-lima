#!/usr/bin/env python3
"""Consolida y audita los tres bloques de transiciones ACR del Paso 6D3."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "00_raw" / "transiciones_acr"
OUTPUT_CSV = (
    ROOT / "01_intermediate" / "transiciones_acr_15_periodos_consolidado.csv"
)
OUTPUT_JSON = ROOT / "evidencia" / "control_transiciones_acr_d3.json"

FILES = {
    1: RAW_DIR / "serie_transiciones_acr_bloque_1_de_3.csv",
    2: RAW_DIR / "serie_transiciones_acr_bloque_2_de_3.csv",
    3: RAW_DIR / "serie_transiciones_acr_bloque_3_de_3.csv",
}

FIELDS = [
    "id_ambito",
    "nombre",
    "banda",
    "year_start",
    "year_end",
    "transition_code",
    "from_class",
    "to_class",
    "from_documentada",
    "to_documentada",
    "area_ha",
]

EXPECTED_NAMES = {
    "amancaes": "Lomas de Amancaes",
    "ancon": "Lomas de Ancón",
    "carabayllo_1": "Lomas de Carabayllo 1",
    "carabayllo_2": "Lomas de Carabayllo 2",
    "villa_maria": "Lomas de Villa María",
}

EXPECTED_BLOCKS = {
    1: {
        "transitions_1985_1986",
        "transitions_1986_1987",
        "transitions_2000_2001",
        "transitions_2005_2006",
        "transitions_2009_2010",
    },
    2: {
        "transitions_2011_2012",
        "transitions_2013_2014",
        "transitions_2014_2015",
        "transitions_2019_2020",
        "transitions_2021_2022",
    },
    3: {
        "transitions_2022_2023",
        "transitions_2023_2024",
        "transitions_1985_2024",
        "transitions_2000_2024",
        "transitions_2010_2024",
    },
}

EXPECTED_ROWS = {1: 159, 2: 182, 3: 218}
EXPECTED_TOTAL_ROWS = 559
EXPECTED_BAND_AREA_HA = 13468.7528934133
AREA_TOLERANCE_HA = 0.000001


def parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized not in {"true", "false"}:
        raise ValueError(f"Booleano no válido: {value!r}")
    return normalized == "true"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_block(block: int, path: Path) -> list[dict[str, object]]:
    if not path.exists():
        raise FileNotFoundError(path)

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != FIELDS:
            raise ValueError(
                f"Esquema inesperado en bloque {block}: {reader.fieldnames}"
            )

        rows: list[dict[str, object]] = []
        for line_number, raw in enumerate(reader, start=2):
            if any(raw[field] is None or raw[field].strip() == "" for field in FIELDS):
                raise ValueError(
                    f"Valor nulo o vacío en bloque {block}, línea {line_number}"
                )

            row: dict[str, object] = {
                "id_ambito": raw["id_ambito"].strip(),
                "nombre": raw["nombre"].strip(),
                "banda": raw["banda"].strip(),
                "year_start": int(raw["year_start"]),
                "year_end": int(raw["year_end"]),
                "transition_code": int(raw["transition_code"]),
                "from_class": int(raw["from_class"]),
                "to_class": int(raw["to_class"]),
                "from_documentada": parse_bool(raw["from_documentada"]),
                "to_documentada": parse_bool(raw["to_documentada"]),
                "area_ha": float(raw["area_ha"]),
                "_block": block,
            }
            rows.append(row)

    return rows


def main() -> None:
    rows: list[dict[str, object]] = []
    rows_by_block: dict[int, int] = {}
    bands_by_block: dict[int, list[str]] = {}

    for block, path in FILES.items():
        block_rows = read_block(block, path)
        rows.extend(block_rows)
        rows_by_block[block] = len(block_rows)
        bands_by_block[block] = sorted(
            {str(row["banda"]) for row in block_rows}
        )

    exact_rows = [
        tuple(row[field] for field in FIELDS)
        for row in rows
    ]
    exact_duplicates = len(exact_rows) - len(set(exact_rows))

    key_counter = Counter(
        (
            row["id_ambito"],
            row["banda"],
            row["transition_code"],
        )
        for row in rows
    )
    duplicate_keys = sum(count - 1 for count in key_counter.values() if count > 1)

    formula_errors = sum(
        int(row["transition_code"])
        != int(row["from_class"]) * 100 + int(row["to_class"])
        for row in rows
    )

    year_errors = 0
    for row in rows:
        parts = str(row["banda"]).split("_")
        year_errors += (
            len(parts) != 3
            or int(parts[1]) != int(row["year_start"])
            or int(parts[2]) != int(row["year_end"])
        )

    name_errors = sum(
        EXPECTED_NAMES.get(str(row["id_ambito"])) != row["nombre"]
        for row in rows
    )
    undocumented_rows = sum(
        not bool(row["from_documentada"])
        or not bool(row["to_documentada"])
        for row in rows
    )
    invalid_areas = sum(
        not math.isfinite(float(row["area_ha"]))
        or float(row["area_ha"]) <= 0
        for row in rows
    )

    area_by_band: dict[str, float] = defaultdict(float)
    ids_by_band: dict[str, set[str]] = defaultdict(set)
    area_by_band_id: dict[tuple[str, str], float] = defaultdict(float)
    for row in rows:
        band = str(row["banda"])
        area = float(row["area_ha"])
        area_by_band[band] += area
        ids_by_band[band].add(str(row["id_ambito"]))
        area_by_band_id[(band, str(row["id_ambito"]))] += area

    band_area_differences = {
        band: total - EXPECTED_BAND_AREA_HA
        for band, total in sorted(area_by_band.items())
    }
    max_band_area_abs_difference = max(
        abs(value) for value in band_area_differences.values()
    )

    expected_ids = set(EXPECTED_NAMES)
    incomplete_bands = {
        band: sorted(expected_ids - ids)
        for band, ids in ids_by_band.items()
        if ids != expected_ids
    }

    id_area_ranges: dict[str, float] = {}
    for id_ambito in sorted(expected_ids):
        values = [
            area_by_band_id[(band, id_ambito)]
            for band in sorted(area_by_band)
        ]
        id_area_ranges[id_ambito] = max(values) - min(values)

    checks = {
        "files_present": all(path.exists() for path in FILES.values()),
        "headers_exact": True,
        "rows_by_block_expected": rows_by_block == EXPECTED_ROWS,
        "total_rows_expected": len(rows) == EXPECTED_TOTAL_ROWS,
        "bands_by_block_expected": all(
            set(bands_by_block[block]) == expected
            for block, expected in EXPECTED_BLOCKS.items()
        ),
        "total_bands_expected": len(area_by_band) == 15,
        "ids_expected": {str(row["id_ambito"]) for row in rows} == expected_ids,
        "all_bands_cover_five_ids": not incomplete_bands,
        "no_exact_duplicates": exact_duplicates == 0,
        "composite_key_unique": duplicate_keys == 0,
        "transition_formula_valid": formula_errors == 0,
        "band_years_match": year_errors == 0,
        "names_match_ids": name_errors == 0,
        "documented_classes_only": undocumented_rows == 0,
        "areas_positive_and_finite": invalid_areas == 0,
        "band_area_control_pass": (
            max_band_area_abs_difference <= AREA_TOLERANCE_HA
        ),
    }

    report = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "grain": "id_ambito × banda × transition_code",
        "source_files": [str(path.relative_to(ROOT)) for path in FILES.values()],
        "source_sha256": {
            str(path.relative_to(ROOT)): sha256(path)
            for path in FILES.values()
        },
        "output_csv": str(OUTPUT_CSV.relative_to(ROOT)),
        "row_count": len(rows),
        "column_count": len(FIELDS),
        "rows_by_block": rows_by_block,
        "band_count": len(area_by_band),
        "id_ambito_count": len(expected_ids),
        "transition_code_count": len(
            {int(row["transition_code"]) for row in rows}
        ),
        "exact_duplicates": exact_duplicates,
        "duplicate_composite_keys": duplicate_keys,
        "formula_errors": formula_errors,
        "year_errors": year_errors,
        "name_errors": name_errors,
        "undocumented_rows": undocumented_rows,
        "invalid_areas": invalid_areas,
        "incomplete_bands": incomplete_bands,
        "expected_band_area_ha": EXPECTED_BAND_AREA_HA,
        "area_by_band_ha": dict(sorted(area_by_band.items())),
        "max_band_area_abs_difference_ha": max_band_area_abs_difference,
        "area_range_by_id_across_bands_ha": id_area_ranges,
        "checks": checks,
    }

    if report["status"] != "PASS":
        OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_JSON.write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        raise RuntimeError(
            "La auditoría falló. Revisar control_transiciones_acr_d3.json"
        )

    rows.sort(
        key=lambda row: (
            int(row["year_start"]),
            int(row["year_end"]),
            str(row["id_ambito"]),
            int(row["transition_code"]),
        )
    )

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    field: (
                        str(row[field]).lower()
                        if isinstance(row[field], bool)
                        else row[field]
                    )
                    for field in FIELDS
                }
            )

    report["output_sha256"] = sha256(OUTPUT_CSV)
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
