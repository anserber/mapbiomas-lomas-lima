#!/usr/bin/env python3
"""Consolida y audita los ocho CSV de clases de los anillos."""

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
BLOCKS = [
    (1985, 1989, 451),
    (1990, 1994, 472),
    (1995, 1999, 485),
    (2000, 2004, 458),
    (2005, 2009, 472),
    (2010, 2014, 484),
    (2015, 2019, 501),
    (2020, 2024, 516),
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
EXPECTED_YEARS = set(range(1985, 2025))
EXPECTED_COLUMNS = [
    "nivel",
    "unidad_id",
    "id_ambito",
    "nombre",
    "zona",
    "dist_min_m",
    "dist_max_m",
    "year",
    "class_id",
    "class_name",
    "class_origin",
    "area_ref_ha",
    "area_utm_ha",
    "area_ha",
    "area_pct_unidad",
]
CLASS_CATALOG = {
    0: ("Sin dato", "No definido"),
    3: ("Bosque", "Natural"),
    4: ("Bosque seco", "Natural"),
    5: ("Manglar", "Natural"),
    6: ("Bosque inundable", "Natural"),
    9: ("Plantación forestal", "Antrópico"),
    11: ("Zona pantanosa o pastizal inundable", "Natural"),
    12: ("Pastizal / herbazal", "Natural"),
    13: ("Otra formación no boscosa", "Natural"),
    15: ("Pasto", "Antrópico"),
    18: ("Agricultura", "Antrópico"),
    21: ("Mosaico agropecuario", "Antrópico"),
    23: ("Playa", "Natural"),
    24: ("Infraestructura urbana", "Antrópico"),
    25: ("Otra área antrópica sin vegetación", "Antrópico"),
    27: ("No observado", "No definido"),
    29: ("Afloramiento rocoso", "Natural"),
    30: ("Minería", "Antrópico"),
    31: ("Acuicultura", "Antrópico"),
    32: ("Salina costera", "Natural"),
    33: ("Río, lago u océano", "Natural"),
    34: ("Glaciar", "Natural"),
    35: ("Palma aceitera", "Antrópico"),
    40: ("Arroz", "Antrópico"),
    61: ("Salar", "Natural"),
    66: ("Matorral", "Natural"),
    68: ("Otra área natural sin vegetación", "Natural"),
    70: ("Loma costera", "Natural"),
    72: ("Otros cultivos", "Antrópico"),
}

INDICATORS = RAW / "serie_indicadores_anillos_1985_2024.csv"
OUT_CSV = RESULTS / "serie_clases_anillos_1985_2024.csv"
REPORT = RESULTS / "validacion_serie_clases_anillos_1985_2024.md"
OUT_SHA = RESULTS / "serie_clases_anillos_1985_2024.csv.sha256"
INPUT_MANIFEST = RAW / "manifest_sha256_serie_clases_anillos.txt"
COMPARISON_TOLERANCE_HA = 1e-5


def close(a: float, b: float, tolerance: float = 1e-6) -> bool:
    return math.isclose(a, b, rel_tol=0.0, abs_tol=tolerance)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def expected_units() -> set[str]:
    ambit = {
        f"{identifier}|{zone}"
        for identifier in EXPECTED_IDS
        for zone in EXPECTED_ZONES
    }
    system = {f"sistema|{zone}" for zone in EXPECTED_ZONES}
    return ambit | system


def main() -> None:
    failures: list[str] = []
    rows: list[dict[str, object]] = []
    source_paths: list[Path] = []
    block_counts: dict[str, int] = {}
    units_expected = expected_units()

    for start, end, expected_count in BLOCKS:
        path = RAW / f"serie_clases_anillos_{start}_{end}.csv"
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

        label = f"{start}–{end}"
        block_counts[label] = len(raw_rows)
        if len(raw_rows) != expected_count:
            failures.append(
                f"`{path.name}` tiene {len(raw_rows)} filas; "
                f"se esperaban {expected_count}."
            )

        years_seen: set[int] = set()
        units_seen: set[str] = set()
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
                    "year": int(float(raw["year"])),
                    "class_id": int(raw["class_id"]),
                    "class_name": raw["class_name"].strip(),
                    "class_origin": raw["class_origin"].strip(),
                    "area_ref_ha": float(raw["area_ref_ha"]),
                    "area_utm_ha": float(raw["area_utm_ha"]),
                    "area_ha": float(raw["area_ha"]),
                    "area_pct_unidad": float(raw["area_pct_unidad"]),
                }
            except (KeyError, TypeError, ValueError) as exc:
                failures.append(
                    f"`{path.name}`, línea {line_number}: valor inválido ({exc})."
                )
                continue

            year = int(parsed["year"])
            unit = str(parsed["unidad_id"])
            years_seen.add(year)
            units_seen.add(unit)
            if not start <= year <= end:
                failures.append(
                    f"`{path.name}` contiene el año {year} fuera del bloque."
                )
            rows.append(parsed)

        if years_seen != set(range(start, end + 1)):
            failures.append(f"`{path.name}` no contiene exactamente cinco años.")
        if units_seen != units_expected:
            failures.append(f"`{path.name}` no contiene las 18 unidades.")

    if len(rows) != 3839:
        failures.append(f"Filas consolidadas: {len(rows)}; esperado: 3839.")

    keys = [(r["unidad_id"], r["year"], r["class_id"]) for r in rows]
    key_counts = Counter(keys)
    duplicate_keys = [key for key, count in key_counts.items() if count > 1]
    if duplicate_keys:
        failures.append(
            f"Hay {len(duplicate_keys)} claves unidad–año–clase duplicadas."
        )

    pairs = {(str(r["unidad_id"]), int(r["year"])) for r in rows}
    expected_pairs = {
        (unit, year) for unit in units_expected for year in EXPECTED_YEARS
    }
    missing_pairs = expected_pairs - pairs
    extra_pairs = pairs - expected_pairs
    if missing_pairs:
        failures.append(f"Faltan {len(missing_pairs)} claves unidad–año.")
    if extra_pairs:
        failures.append(f"Hay {len(extra_pairs)} claves unidad–año adicionales.")

    blank_text = 0
    invalid_identity = 0
    invalid_distance = 0
    invalid_catalog = 0
    invalid_numeric = 0
    invalid_pct_formula = 0
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
                "class_name",
                "class_origin",
            ]
        ):
            blank_text += 1

        zone = str(row["zona"])
        expected_distance = EXPECTED_ZONES.get(zone)
        if expected_distance != (
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

        expected_definition = CLASS_CATALOG.get(int(row["class_id"]))
        if expected_definition != (row["class_name"], row["class_origin"]):
            invalid_catalog += 1

        area_ref = float(row["area_ref_ha"])
        area_utm = float(row["area_utm_ha"])
        area = float(row["area_ha"])
        pct = float(row["area_pct_unidad"])
        if (
            area_ref <= 0
            or area_utm <= 0
            or area < 0
            or pct < 0
            or pct > 100
            or not all(math.isfinite(v) for v in [area_ref, area_utm, area, pct])
        ):
            invalid_numeric += 1
        if area_utm > 0 and not close(pct, area / area_utm * 100):
            invalid_pct_formula += 1

        stable_values[str(row["unidad_id"])].add(
            (
                row["nivel"],
                row["id_ambito"],
                row["nombre"],
                row["zona"],
                row["dist_min_m"],
                row["dist_max_m"],
                round(area_ref, 9),
                round(area_utm, 9),
            )
        )

    if blank_text:
        failures.append(f"Hay {blank_text} filas con texto obligatorio vacío.")
    if invalid_identity:
        failures.append(f"Hay {invalid_identity} filas con identidad incoherente.")
    if invalid_distance:
        failures.append(f"Hay {invalid_distance} filas con distancias incoherentes.")
    if invalid_catalog:
        failures.append(
            f"Hay {invalid_catalog} filas incompatibles con el catálogo."
        )
    if invalid_numeric:
        failures.append(f"Hay {invalid_numeric} filas con valores fuera de rango.")
    if invalid_pct_formula:
        failures.append(
            f"Hay {invalid_pct_formula} porcentajes incompatibles con el área."
        )
    inconsistent_units = [
        unit for unit, values in stable_values.items() if len(values) != 1
    ]
    if inconsistent_units:
        failures.append(
            f"{len(inconsistent_units)} unidades cambian de atributos o superficie."
        )

    indicator_rows: dict[tuple[str, int], dict[str, str]] = {}
    if not INDICATORS.exists():
        failures.append(f"Falta `{INDICATORS.name}`.")
    else:
        with INDICATORS.open("r", encoding="utf-8-sig", newline="") as handle:
            for raw in csv.DictReader(handle):
                key = (raw["unidad_id"].strip(), int(float(raw["year"])))
                indicator_rows[key] = raw
        if set(indicator_rows) != expected_pairs:
            failures.append(
                "La tabla de indicadores no contiene las 720 claves esperadas."
            )

    by_pair: dict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        by_pair[(str(row["unidad_id"]), int(row["year"]))].append(row)

    comparison_diffs: dict[str, list[float]] = defaultdict(list)
    mismatch_pairs = 0
    percent_sum_min = float("inf")
    percent_sum_max = float("-inf")
    for key, group in by_pair.items():
        indicator = indicator_rows.get(key)
        if not indicator:
            continue

        total = sum(float(row["area_ha"]) for row in group)
        no_data = sum(
            float(row["area_ha"]) for row in group if int(row["class_id"]) == 0
        )
        loma = sum(
            float(row["area_ha"]) for row in group if int(row["class_id"]) == 70
        )
        urban = sum(
            float(row["area_ha"]) for row in group if int(row["class_id"]) == 24
        )
        classified = total - no_data
        other = classified - loma - urban
        pct_sum = sum(float(row["area_pct_unidad"]) for row in group)
        percent_sum_min = min(percent_sum_min, pct_sum)
        percent_sum_max = max(percent_sum_max, pct_sum)

        diffs = {
            "total": abs(total - float(indicator["area_pixeles_ha"])),
            "clasificada": abs(
                classified - float(indicator["clasificada_ha"])
            ),
            "sin_dato": abs(no_data - float(indicator["sin_dato_ha"])),
            "loma": abs(loma - float(indicator["loma_ha"])),
            "urbano": abs(urban - float(indicator["urbano_ha"])),
            "otras": abs(other - float(indicator["otras_clases_ha"])),
        }
        for metric, difference in diffs.items():
            comparison_diffs[metric].append(difference)
        if any(
            difference > COMPARISON_TOLERANCE_HA
            for difference in diffs.values()
        ):
            mismatch_pairs += 1

    if mismatch_pairs:
        failures.append(
            f"{mismatch_pairs} claves no concuerdan con los indicadores a "
            f"{COMPARISON_TOLERANCE_HA:.5f} ha."
        )

    rows.sort(
        key=lambda row: (
            str(row["nivel"]),
            str(row["unidad_id"]),
            int(row["year"]),
            int(row["class_id"]),
        )
    )
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=EXPECTED_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    INPUT_MANIFEST.write_text(
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

    observed_classes = sorted({int(row["class_id"]) for row in rows})
    class_presence: dict[int, tuple[int, int]] = {}
    for class_id in observed_classes:
        class_years = [
            int(row["year"]) for row in rows if int(row["class_id"]) == class_id
        ]
        class_presence[class_id] = (min(class_years), max(class_years))

    max_diffs = {
        metric: max(values, default=0.0)
        for metric, values in comparison_diffs.items()
    }
    status = "PASS" if not failures else "FAIL"
    report = [
        "# Validación de la serie de clases de anillos 1985–2024",
        "",
        f"**Estado:** {status}  ",
        f"**Fecha:** {datetime.now().astimezone().isoformat(timespec='seconds')}  ",
        "**Grano:** unidad espacial × año × clase  ",
        "",
        "## Perfil",
        "",
        f"- Archivos fuente: {len(source_paths)}.",
        f"- Filas consolidadas: {len(rows)}.",
        f"- Columnas: {len(EXPECTED_COLUMNS)}.",
        f"- Unidades: {len(units_expected)}.",
        f"- Combinaciones unidad–año: {len(pairs)} de 720.",
        f"- Clases observadas: {', '.join(map(str, observed_classes))}.",
        "",
        "## Filas por bloque",
        "",
        "| Bloque | Filas |",
        "|---|---:|",
    ]
    report.extend(
        f"| {label} | {count} |" for label, count in block_counts.items()
    )
    report.extend(
        [
            "",
            "## Controles",
            "",
            f"- Duplicados unidad–año–clase: {len(duplicate_keys)}.",
            f"- Combinaciones unidad–año faltantes: {len(missing_pairs)}.",
            f"- Textos obligatorios vacíos: {blank_text}.",
            f"- Errores de identidad: {invalid_identity}.",
            f"- Errores de distancias: {invalid_distance}.",
            f"- Errores de catálogo: {invalid_catalog}.",
            f"- Errores numéricos: {invalid_numeric}.",
            f"- Errores de fórmula porcentual: {invalid_pct_formula}.",
            f"- Unidades con atributos inestables: {len(inconsistent_units)}.",
            (
                "- Rango de suma porcentual por unidad–año: "
                f"{percent_sum_min:.9f}%–{percent_sum_max:.9f}%."
            ),
            "",
            "## Concordancia con indicadores",
            "",
            "- Claves comparadas: 720.",
            (
                "- Claves con diferencias > "
                f"{COMPARISON_TOLERANCE_HA:.5f} ha: {mismatch_pairs}."
            ),
            f"- Diferencia máxima total: {max_diffs['total']:.12f} ha.",
            (
                "- Diferencia máxima superficie clasificada: "
                f"{max_diffs['clasificada']:.12f} ha."
            ),
            f"- Diferencia máxima sin dato: {max_diffs['sin_dato']:.12f} ha.",
            f"- Diferencia máxima loma: {max_diffs['loma']:.12f} ha.",
            f"- Diferencia máxima urbano: {max_diffs['urbano']:.12f} ha.",
            f"- Diferencia máxima otras clases: {max_diffs['otras']:.12f} ha.",
            "",
            "## Catálogo observado",
            "",
            "| Código | Clase | Origen | Primer año | Último año |",
            "|---:|---|---|---:|---:|",
        ]
    )
    for class_id in observed_classes:
        name, origin = CLASS_CATALOG[class_id]
        first_year, last_year = class_presence[class_id]
        report.append(
            f"| {class_id} | {name} | {origin} | {first_year} | {last_year} |"
        )
    report.extend(
        [
            "",
            "## Integridad",
            "",
            f"- CSV consolidado: `{OUT_CSV.name}`.",
            f"- SHA-256: `{output_hash}`.",
            f"- Manifiesto de entradas: `{INPUT_MANIFEST.name}`.",
            "",
            "## Interpretación",
            "",
        ]
    )
    if status == "PASS":
        report.append(
            "La composición completa por clases es apta para el análisis. La clase "
            "0 representa explícitamente píxeles sin dato y no debe combinarse con "
            "las clases de cobertura. Para totales del sistema deben utilizarse "
            "únicamente las tres unidades con nivel `sistema`."
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
    print(f"Combinaciones unidad–año: {len(pairs)}/720")
    print(f"Clases: {observed_classes}")
    print(f"Discrepancias frente a indicadores: {mismatch_pairs}")
    print(f"CSV: {OUT_CSV}")
    print(f"Reporte: {REPORT}")
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
