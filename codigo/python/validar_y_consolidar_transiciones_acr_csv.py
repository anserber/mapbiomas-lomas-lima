#!/usr/bin/env python3
"""Consolida y audita las transiciones seleccionadas del interior del ACR."""

from __future__ import annotations

import csv
import hashlib
import math
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "04_extraccion_series/02_resultados/00_raw"
RESULTS = ROOT / "04_extraccion_series/02_resultados"

EXPECTED_BLOCKS = {
    1: (
        159,
        [
            "transitions_1985_1986",
            "transitions_1986_1987",
            "transitions_2000_2001",
            "transitions_2005_2006",
            "transitions_2009_2010",
        ],
    ),
    2: (
        182,
        [
            "transitions_2011_2012",
            "transitions_2013_2014",
            "transitions_2014_2015",
            "transitions_2019_2020",
            "transitions_2021_2022",
        ],
    ),
    3: (
        218,
        [
            "transitions_2022_2023",
            "transitions_2023_2024",
            "transitions_1985_2024",
            "transitions_2000_2024",
            "transitions_2010_2024",
        ],
    ),
}
EXPECTED_COLUMNS = [
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
EXPECTED_IDS = {
    "amancaes",
    "ancon",
    "carabayllo_1",
    "carabayllo_2",
    "villa_maria",
}
EXPECTED_NAMES = {
    "amancaes": "Lomas de Amancaes",
    "ancon": "Lomas de Ancón",
    "carabayllo_1": "Lomas de Carabayllo 1",
    "carabayllo_2": "Lomas de Carabayllo 2",
    "villa_maria": "Lomas de Villa María",
}
DOCUMENTED_CLASSES = {
    0, 3, 4, 5, 6, 7, 9, 11, 12, 13, 15, 18, 19, 21, 23, 24, 25,
    29, 30, 31, 32, 33, 34, 35, 60, 61, 62, 63, 64, 65, 66, 67, 68,
    69, 70, 72,
}
AREA_TOLERANCE_HA = 1e-5

OUT_CSV = RESULTS / "serie_transiciones_acr_seleccionadas.csv"
OUT_SHA = Path(f"{OUT_CSV}.sha256")
REPORT = RESULTS / "validacion_transiciones_acr_seleccionadas.md"
MANIFEST = RAW / "manifest_sha256_transiciones_acr.txt"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    raise ValueError(f"booleano no reconocido: {value!r}")


def main() -> None:
    failures: list[str] = []
    rows: list[dict[str, object]] = []
    source_paths: list[Path] = []
    block_counts: dict[int, int] = {}
    bands_expected = {
        band
        for _, bands in EXPECTED_BLOCKS.values()
        for band in bands
    }

    for block, (expected_count, expected_bands) in EXPECTED_BLOCKS.items():
        path = RAW / f"serie_transiciones_acr_bloque_{block}_de_3.csv"
        source_paths.append(path)
        if not path.exists():
            failures.append(f"Falta `{path.name}`.")
            continue

        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != EXPECTED_COLUMNS:
                failures.append(f"`{path.name}` tiene un esquema diferente.")
                continue
            raw_rows = list(reader)

        block_counts[block] = len(raw_rows)
        if len(raw_rows) != expected_count:
            failures.append(
                f"`{path.name}` tiene {len(raw_rows)} filas; "
                f"se esperaban {expected_count}."
            )

        bands_seen: set[str] = set()
        for line_number, raw in enumerate(raw_rows, start=2):
            try:
                parsed: dict[str, object] = {
                    "id_ambito": raw["id_ambito"].strip(),
                    "nombre": raw["nombre"].strip(),
                    "banda": raw["banda"].strip(),
                    "year_start": int(float(raw["year_start"])),
                    "year_end": int(float(raw["year_end"])),
                    "transition_code": int(float(raw["transition_code"])),
                    "from_class": int(float(raw["from_class"])),
                    "to_class": int(float(raw["to_class"])),
                    "from_documentada": parse_bool(raw["from_documentada"]),
                    "to_documentada": parse_bool(raw["to_documentada"]),
                    "area_ha": float(raw["area_ha"]),
                }
            except (KeyError, TypeError, ValueError) as exc:
                failures.append(
                    f"`{path.name}`, línea {line_number}: valor inválido ({exc})."
                )
                continue
            bands_seen.add(str(parsed["banda"]))
            rows.append(parsed)

        if bands_seen != set(expected_bands):
            failures.append(
                f"`{path.name}` no contiene exactamente sus cinco bandas."
            )

    expected_total = sum(value[0] for value in EXPECTED_BLOCKS.values())
    if len(rows) != expected_total:
        failures.append(
            f"Filas consolidadas: {len(rows)}; esperado: {expected_total}."
        )

    keys = [
        (row["id_ambito"], row["banda"], row["transition_code"])
        for row in rows
    ]
    duplicate_keys = [
        key for key, count in Counter(keys).items() if count > 1
    ]
    if duplicate_keys:
        failures.append(
            f"Hay {len(duplicate_keys)} claves ámbito–banda–transición duplicadas."
        )

    pairs = {(str(row["id_ambito"]), str(row["banda"])) for row in rows}
    expected_pairs = {
        (identifier, band)
        for identifier in EXPECTED_IDS
        for band in bands_expected
    }
    missing_pairs = expected_pairs - pairs
    extra_pairs = pairs - expected_pairs
    if missing_pairs:
        failures.append(f"Faltan {len(missing_pairs)} claves ámbito–banda.")
    if extra_pairs:
        failures.append(f"Hay {len(extra_pairs)} claves ámbito–banda adicionales.")

    blank_text = 0
    invalid_identity = 0
    invalid_period = 0
    invalid_code = 0
    undocumented = 0
    invalid_area = 0
    stable_names: dict[str, set[str]] = defaultdict(set)

    for row in rows:
        if any(
            str(row[column]).strip() == ""
            for column in ["id_ambito", "nombre", "banda"]
        ):
            blank_text += 1

        identifier = str(row["id_ambito"])
        if (
            identifier not in EXPECTED_IDS
            or row["nombre"] != EXPECTED_NAMES.get(identifier)
        ):
            invalid_identity += 1

        band_parts = str(row["banda"]).split("_")
        if (
            len(band_parts) != 3
            or band_parts[0] != "transitions"
            or int(band_parts[1]) != int(row["year_start"])
            or int(band_parts[2]) != int(row["year_end"])
        ):
            invalid_period += 1

        expected_code = int(row["from_class"]) * 100 + int(row["to_class"])
        if expected_code != int(row["transition_code"]):
            invalid_code += 1

        if (
            int(row["from_class"]) not in DOCUMENTED_CLASSES
            or int(row["to_class"]) not in DOCUMENTED_CLASSES
            or row["from_documentada"] is not True
            or row["to_documentada"] is not True
        ):
            undocumented += 1

        area = float(row["area_ha"])
        if not math.isfinite(area) or area < 0:
            invalid_area += 1

        stable_names[identifier].add(str(row["nombre"]))

    controls = {
        "textos obligatorios vacíos": blank_text,
        "errores de identidad": invalid_identity,
        "errores de periodo": invalid_period,
        "errores de codificación": invalid_code,
        "clases no documentadas": undocumented,
        "áreas inválidas": invalid_area,
    }
    for label, count in controls.items():
        if count:
            failures.append(f"Hay {count} {label}.")

    inconsistent_names = [
        identifier
        for identifier, names in stable_names.items()
        if len(names) != 1
    ]
    if inconsistent_names:
        failures.append(
            f"{len(inconsistent_names)} ámbitos cambian de nombre."
        )

    area_by_pair: dict[tuple[str, str], float] = defaultdict(float)
    for row in rows:
        area_by_pair[(str(row["id_ambito"]), str(row["banda"]))] += float(
            row["area_ha"]
        )

    area_ranges: dict[str, float] = {}
    unstable_areas: list[str] = []
    for identifier in EXPECTED_IDS:
        values = [
            area_by_pair[(identifier, band)]
            for band in bands_expected
            if (identifier, band) in area_by_pair
        ]
        difference = max(values) - min(values) if values else float("inf")
        area_ranges[identifier] = difference
        if difference > AREA_TOLERANCE_HA:
            unstable_areas.append(identifier)
    if unstable_areas:
        failures.append(
            f"{len(unstable_areas)} ámbitos cambian de cobertura entre bandas."
        )

    total_by_band: dict[str, float] = defaultdict(float)
    for row in rows:
        total_by_band[str(row["banda"])] += float(row["area_ha"])
    band_totals = [total_by_band[band] for band in bands_expected]

    rows.sort(
        key=lambda row: (
            str(row["id_ambito"]),
            int(row["year_start"]),
            int(row["year_end"]),
            int(row["transition_code"]),
        )
    )
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=EXPECTED_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    MANIFEST.write_text(
        "\n".join(
            f"{sha256(path)}  {path.name}"
            for path in source_paths
            if path.exists()
        )
        + "\n",
        encoding="utf-8",
    )
    output_hash = sha256(OUT_CSV)
    OUT_SHA.write_text(f"{output_hash}  {OUT_CSV.name}\n", encoding="utf-8")

    status = "PASS" if not failures else "FAIL"
    observed_codes = sorted({int(row["transition_code"]) for row in rows})
    observed_classes = sorted(
        {
            int(row[column])
            for row in rows
            for column in ("from_class", "to_class")
        }
    )
    report = [
        "# Validación de transiciones seleccionadas del ACR",
        "",
        f"**Estado:** {status}  ",
        f"**Fecha:** {datetime.now().astimezone().isoformat(timespec='seconds')}  ",
        "**Grano:** ámbito × banda × código de transición  ",
        "",
        "## Perfil",
        "",
        f"- Archivos fuente: {len(source_paths)}.",
        f"- Filas consolidadas: {len(rows)}.",
        f"- Columnas: {len(EXPECTED_COLUMNS)}.",
        f"- Bandas seleccionadas: {len(bands_expected)}.",
        f"- Ámbitos: {len(EXPECTED_IDS)}.",
        f"- Combinaciones ámbito–banda: {len(pairs)} de 75.",
        f"- Códigos de transición distintos: {len(observed_codes)}.",
        f"- Clases observadas: {', '.join(map(str, observed_classes))}.",
        "",
        "## Filas por bloque",
        "",
        "| Bloque | Filas |",
        "|---:|---:|",
    ]
    report.extend(
        f"| {block} | {block_counts.get(block, 0)} |"
        for block in sorted(EXPECTED_BLOCKS)
    )
    report.extend(
        [
            "",
            "## Controles",
            "",
            f"- Duplicados ámbito–banda–transición: {len(duplicate_keys)}.",
            f"- Combinaciones ámbito–banda faltantes: {len(missing_pairs)}.",
            f"- Textos obligatorios vacíos: {blank_text}.",
            f"- Errores de identidad: {invalid_identity}.",
            f"- Errores de periodo: {invalid_period}.",
            f"- Errores de codificación: {invalid_code}.",
            f"- Clases no documentadas: {undocumented}.",
            f"- Áreas inválidas: {invalid_area}.",
            f"- Ámbitos con nombres inestables: {len(inconsistent_names)}.",
            (
                "- Ámbitos con diferencias de cobertura > "
                f"{AREA_TOLERANCE_HA:.5f} ha: {len(unstable_areas)}."
            ),
            (
                "- Diferencia máxima de cobertura entre bandas por ámbito: "
                f"{max(area_ranges.values(), default=0):.12f} ha."
            ),
            "",
            "## Total de cobertura",
            "",
            (
                "- Cinco ámbitos del ACR: "
                f"{min(band_totals):.12f}–{max(band_totals):.12f} ha."
            ),
            "",
            "## Integridad",
            "",
            f"- CSV consolidado: `{OUT_CSV.name}`.",
            f"- SHA-256: `{output_hash}`.",
            f"- Manifiesto de entradas: `{MANIFEST.name}`.",
            "",
            "## Dictamen",
            "",
        ]
    )
    if status == "PASS":
        report.append(
            "Las transiciones seleccionadas del interior de los cinco ámbitos "
            "del ACR son aptas para el análisis temporal."
        )
    else:
        report.append("La serie no debe utilizarse todavía.")
    if failures:
        report.extend(["", "## Incumplimientos", ""])
        report.extend(f"- {failure}" for failure in failures)

    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

    print(f"Estado: {status}")
    print(f"Filas consolidadas: {len(rows)}")
    print(f"Duplicados: {len(duplicate_keys)}")
    print(f"Combinaciones ámbito–banda: {len(pairs)}/75")
    print(f"Bandas: {len(bands_expected)}")
    print(f"Ámbitos con cobertura inestable: {len(unstable_areas)}")
    print(f"CSV: {OUT_CSV}")
    print(f"Reporte: {REPORT}")
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
