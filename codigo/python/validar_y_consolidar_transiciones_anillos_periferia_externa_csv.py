#!/usr/bin/env python3
"""Consolida y audita las transiciones de la periferia externa corregida."""

from __future__ import annotations

import csv
import hashlib
import math
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RAW = (
    ROOT
    / "04_extraccion_series/02_resultados/00_raw"
    / "correccion_enclave_20260728"
)
RESULTS = ROOT / "04_extraccion_series/02_resultados"

EXPECTED_BLOCKS = {
    1: (
        979,
        [
            "transitions_1985_1986",
            "transitions_1986_1987",
            "transitions_2000_2001",
            "transitions_2005_2006",
            "transitions_2009_2010",
        ],
    ),
    2: (
        1160,
        [
            "transitions_2011_2012",
            "transitions_2013_2014",
            "transitions_2014_2015",
            "transitions_2019_2020",
            "transitions_2021_2022",
        ],
    ),
    3: (
        1218,
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
    "nivel",
    "unidad_id",
    "id_ambito",
    "nombre",
    "zona",
    "dist_min_m",
    "dist_max_m",
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
EXPECTED_ZONES = {
    "0_500": (0, 500),
    "500_1000": (500, 1000),
    "1000_2000": (1000, 2000),
}
DOCUMENTED_CLASSES = {
    0, 3, 4, 5, 6, 7, 9, 11, 12, 13, 15, 18, 19, 21, 23, 24, 25,
    29, 30, 31, 32, 33, 34, 35, 60, 61, 62, 63, 64, 65, 66, 67, 68,
    69, 70, 72,
}
AREA_TOLERANCE_HA = 1e-5

OUT_CSV = (
    RESULTS
    / "serie_transiciones_anillos_periferia_externa_seleccionadas.csv"
)
OUT_SHA = Path(f"{OUT_CSV}.sha256")
REPORT = (
    RESULTS
    / "validacion_transiciones_anillos_periferia_externa_seleccionadas.md"
)
MANIFEST = (
    RAW
    / "manifest_sha256_transiciones_anillos_periferia_externa.txt"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def expected_units() -> set[str]:
    units = {
        f"{identifier}|{zone}"
        for identifier in EXPECTED_IDS
        for zone in EXPECTED_ZONES
    }
    units.update(f"sistema|{zone}" for zone in EXPECTED_ZONES)
    return units


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
    units_expected = expected_units()
    bands_expected = {
        band
        for _, bands in EXPECTED_BLOCKS.values()
        for band in bands
    }

    for block, (expected_count, expected_bands) in EXPECTED_BLOCKS.items():
        path = RAW / (
            "serie_transiciones_anillos_periferia_externa_"
            f"bloque_{block}_de_3.csv"
        )
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
                    "nivel": raw["nivel"].strip(),
                    "unidad_id": raw["unidad_id"].strip(),
                    "id_ambito": raw["id_ambito"].strip(),
                    "nombre": raw["nombre"].strip(),
                    "zona": raw["zona"].strip(),
                    "dist_min_m": int(float(raw["dist_min_m"])),
                    "dist_max_m": int(float(raw["dist_max_m"])),
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
        (row["unidad_id"], row["banda"], row["transition_code"])
        for row in rows
    ]
    duplicate_keys = [
        key for key, count in Counter(keys).items() if count > 1
    ]
    if duplicate_keys:
        failures.append(
            f"Hay {len(duplicate_keys)} claves unidad–banda–transición duplicadas."
        )

    pairs = {(str(row["unidad_id"]), str(row["banda"])) for row in rows}
    expected_pairs = {
        (unit, band) for unit in units_expected for band in bands_expected
    }
    missing_pairs = expected_pairs - pairs
    extra_pairs = pairs - expected_pairs
    if missing_pairs:
        failures.append(f"Faltan {len(missing_pairs)} claves unidad–banda.")
    if extra_pairs:
        failures.append(f"Hay {len(extra_pairs)} claves unidad–banda adicionales.")

    blank_text = 0
    invalid_identity = 0
    invalid_distance = 0
    invalid_period = 0
    invalid_code = 0
    undocumented = 0
    invalid_area = 0
    stable_values: dict[str, set[tuple[object, ...]]] = defaultdict(set)

    for row in rows:
        if any(
            str(row[column]).strip() == ""
            for column in [
                "nivel",
                "unidad_id",
                "id_ambito",
                "nombre",
                "zona",
                "banda",
            ]
        ):
            blank_text += 1

        zone = str(row["zona"])
        if EXPECTED_ZONES.get(zone) != (
            int(row["dist_min_m"]),
            int(row["dist_max_m"]),
        ):
            invalid_distance += 1

        if row["nivel"] == "ambito":
            expected_unit = f"{row['id_ambito']}|{zone}"
            if (
                row["id_ambito"] not in EXPECTED_IDS
                or row["unidad_id"] != expected_unit
            ):
                invalid_identity += 1
        elif row["nivel"] == "sistema":
            if (
                row["unidad_id"] != f"sistema|{zone}"
                or row["id_ambito"] != "sistema"
                or row["nombre"] != "Sistema disuelto"
            ):
                invalid_identity += 1
        else:
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

        stable_values[str(row["unidad_id"])].add(
            (
                row["nivel"],
                row["id_ambito"],
                row["nombre"],
                row["zona"],
                row["dist_min_m"],
                row["dist_max_m"],
            )
        )

    controls = {
        "textos obligatorios vacíos": blank_text,
        "errores de identidad": invalid_identity,
        "errores de distancia": invalid_distance,
        "errores de periodo": invalid_period,
        "errores de codificación": invalid_code,
        "clases no documentadas": undocumented,
        "áreas inválidas": invalid_area,
    }
    for label, count in controls.items():
        if count:
            failures.append(f"Hay {count} {label}.")

    inconsistent_units = [
        unit for unit, values in stable_values.items() if len(values) != 1
    ]
    if inconsistent_units:
        failures.append(
            f"{len(inconsistent_units)} unidades cambian de atributos."
        )

    area_by_pair: dict[tuple[str, str], float] = defaultdict(float)
    for row in rows:
        area_by_pair[(str(row["unidad_id"]), str(row["banda"]))] += float(
            row["area_ha"]
        )

    area_ranges: dict[str, float] = {}
    unstable_area_units: list[str] = []
    for unit in units_expected:
        values = [
            area_by_pair[(unit, band)]
            for band in bands_expected
            if (unit, band) in area_by_pair
        ]
        difference = max(values) - min(values) if values else float("inf")
        area_ranges[unit] = difference
        if difference > AREA_TOLERANCE_HA:
            unstable_area_units.append(unit)
    if unstable_area_units:
        failures.append(
            f"{len(unstable_area_units)} unidades cambian de cobertura entre bandas."
        )

    totals_by_level_band: dict[tuple[str, str], float] = defaultdict(float)
    for row in rows:
        totals_by_level_band[(str(row["nivel"]), str(row["banda"]))] += float(
            row["area_ha"]
        )
    ambit_totals = [
        totals_by_level_band[("ambito", band)] for band in bands_expected
    ]
    system_totals = [
        totals_by_level_band[("sistema", band)] for band in bands_expected
    ]

    rows.sort(
        key=lambda row: (
            str(row["nivel"]),
            str(row["unidad_id"]),
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
        "# Validación de transiciones de la periferia externa",
        "",
        f"**Estado:** {status}  ",
        f"**Fecha:** {datetime.now().astimezone().isoformat(timespec='seconds')}  ",
        "**Grano:** unidad espacial × banda × código de transición  ",
        "",
        "## Perfil",
        "",
        f"- Archivos fuente: {len(source_paths)}.",
        f"- Filas consolidadas: {len(rows)}.",
        f"- Columnas: {len(EXPECTED_COLUMNS)}.",
        f"- Bandas seleccionadas: {len(bands_expected)}.",
        f"- Unidades espaciales: {len(units_expected)}.",
        f"- Combinaciones unidad–banda: {len(pairs)} de 270.",
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
            f"- Duplicados unidad–banda–transición: {len(duplicate_keys)}.",
            f"- Combinaciones unidad–banda faltantes: {len(missing_pairs)}.",
            f"- Textos obligatorios vacíos: {blank_text}.",
            f"- Errores de identidad: {invalid_identity}.",
            f"- Errores de distancia: {invalid_distance}.",
            f"- Errores de periodo: {invalid_period}.",
            f"- Errores de codificación: {invalid_code}.",
            f"- Clases no documentadas: {undocumented}.",
            f"- Áreas inválidas: {invalid_area}.",
            f"- Unidades con atributos inestables: {len(inconsistent_units)}.",
            (
                "- Unidades con diferencias de cobertura > "
                f"{AREA_TOLERANCE_HA:.5f} ha: {len(unstable_area_units)}."
            ),
            (
                "- Diferencia máxima de cobertura entre bandas por unidad: "
                f"{max(area_ranges.values(), default=0):.12f} ha."
            ),
            "",
            "## Totales de cobertura",
            "",
            (
                "- Anillos por ámbito: "
                f"{min(ambit_totals):.12f}–{max(ambit_totals):.12f} ha."
            ),
            (
                "- Sistema disuelto: "
                f"{min(system_totals):.12f}–{max(system_totals):.12f} ha."
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
            "Las transiciones seleccionadas de los anillos corregidos son aptas "
            "para el análisis temporal. El enclave interno de SEDAPAL permanece "
            "excluido. Los totales del sistema deben obtenerse solo de las tres "
            "unidades con `nivel = sistema`, sin sumar las unidades por ámbito."
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
    print(f"Combinaciones unidad–banda: {len(pairs)}/270")
    print(f"Bandas: {len(bands_expected)}")
    print(f"Unidades con cobertura inestable: {len(unstable_area_units)}")
    print(f"CSV: {OUT_CSV}")
    print(f"Reporte: {REPORT}")
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
