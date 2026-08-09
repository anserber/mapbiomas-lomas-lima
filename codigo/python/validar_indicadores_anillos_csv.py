#!/usr/bin/env python3
"""Audita los indicadores 1985–2024 de los anillos de influencia."""

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
SOURCE = RAW / "serie_indicadores_anillos_1985_2024.csv"
REPORT = RESULTS / "validacion_serie_indicadores_anillos_1985_2024.md"
SHA_FILE = RAW / "serie_indicadores_anillos_1985_2024.csv.sha256"

EXPECTED_COLUMNS = [
    "nivel",
    "unidad_id",
    "id_ambito",
    "nombre",
    "zona",
    "dist_min_m",
    "dist_max_m",
    "year",
    "area_ref_ha",
    "area_utm_ha",
    "area_pixeles_ha",
    "dif_pix_utm_abs_pct",
    "loma_ha",
    "loma_pct_unidad",
    "urbano_ha",
    "urbano_pct_unidad",
    "otras_clases_ha",
    "otras_clases_pct_unidad",
    "clasificada_ha",
    "sin_dato_ha",
    "sin_dato_pct",
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
NUMERIC_COLUMNS = EXPECTED_COLUMNS[5:]
PERCENT_COLUMNS = {
    "dif_pix_utm_abs_pct",
    "loma_pct_unidad",
    "urbano_pct_unidad",
    "otras_clases_pct_unidad",
    "sin_dato_pct",
}


def close(a: float, b: float, tolerance: float = 1e-6) -> bool:
    return math.isclose(a, b, rel_tol=0.0, abs_tol=tolerance)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    failures: list[str] = []
    warnings: list[str] = []
    if not SOURCE.exists():
        raise SystemExit(f"No existe: {SOURCE}")

    with SOURCE.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []
        raw_rows = list(reader)

    if fieldnames != EXPECTED_COLUMNS:
        failures.append(f"Esquema inesperado: {fieldnames!r}.")

    rows: list[dict[str, object]] = []
    blank_counts: Counter[str] = Counter()
    invalid_numeric: Counter[str] = Counter()
    for line_number, raw in enumerate(raw_rows, start=2):
        for column in EXPECTED_COLUMNS:
            if raw.get(column, "").strip() == "":
                blank_counts[column] += 1

        parsed: dict[str, object] = {
            column: raw.get(column, "").strip()
            for column in EXPECTED_COLUMNS[:5]
        }
        for column in NUMERIC_COLUMNS:
            try:
                value = float(raw[column])
            except (KeyError, TypeError, ValueError):
                invalid_numeric[column] += 1
                value = math.nan
            parsed[column] = value

        for column in ("dist_min_m", "dist_max_m", "year"):
            value = float(parsed[column])
            if math.isfinite(value) and value.is_integer():
                parsed[column] = int(value)
            else:
                failures.append(
                    f"Línea {line_number}: `{column}` no es un entero válido."
                )
        rows.append(parsed)

    if len(rows) != 720:
        failures.append(f"Filas: {len(rows)}; esperado: 720.")
    if blank_counts:
        failures.append(f"Campos vacíos: {dict(blank_counts)}.")
    if invalid_numeric:
        failures.append(f"Valores numéricos inválidos: {dict(invalid_numeric)}.")

    key_counts = Counter((r["unidad_id"], r["year"]) for r in rows)
    duplicate_keys = [key for key, count in key_counts.items() if count > 1]
    if duplicate_keys:
        failures.append(
            f"Hay {len(duplicate_keys)} claves duplicadas unidad–año."
        )

    by_unit: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        by_unit[str(row["unidad_id"])].append(row)

    expected_ambit_units = {
        f"{identifier}|{zone}"
        for identifier in EXPECTED_IDS
        for zone in EXPECTED_ZONES
    }
    expected_system_units = {f"sistema|{zone}" for zone in EXPECTED_ZONES}
    observed_ambit_units = {
        str(row["unidad_id"]) for row in rows if row["nivel"] == "ambito"
    }
    observed_system_units = {
        str(row["unidad_id"]) for row in rows if row["nivel"] == "sistema"
    }
    if observed_ambit_units != expected_ambit_units:
        failures.append("Las 15 unidades por ámbito no coinciden con lo esperado.")
    if observed_system_units != expected_system_units:
        failures.append("Las 3 unidades del sistema no coinciden con lo esperado.")

    level_counts = Counter(str(row["nivel"]) for row in rows)
    if level_counts != Counter({"ambito": 600, "sistema": 120}):
        failures.append(f"Filas por nivel inesperadas: {dict(level_counts)}.")

    unit_consistency_failures = 0
    for unit, unit_rows in by_unit.items():
        years = {int(row["year"]) for row in unit_rows}
        if len(unit_rows) != 40 or years != EXPECTED_YEARS:
            failures.append(
                f"`{unit}` tiene {len(unit_rows)} filas y {len(years)} años."
            )

        stable_fields = [
            "nivel",
            "id_ambito",
            "nombre",
            "zona",
            "dist_min_m",
            "dist_max_m",
            "area_ref_ha",
            "area_utm_ha",
        ]
        for column in stable_fields:
            values = {
                round(float(row[column]), 9)
                if isinstance(row[column], float)
                else row[column]
                for row in unit_rows
            }
            if len(values) != 1:
                unit_consistency_failures += 1

    if unit_consistency_failures:
        failures.append(
            f"Hay {unit_consistency_failures} campos que cambian dentro de una unidad."
        )

    range_failures: Counter[str] = Counter()
    formula_failures: Counter[str] = Counter()
    zone_failures = 0
    identity_failures = 0
    area_reference_differences: list[float] = []

    for row in rows:
        zone = str(row["zona"])
        expected_distances = EXPECTED_ZONES.get(zone)
        if expected_distances != (
            int(row["dist_min_m"]),
            int(row["dist_max_m"]),
        ):
            zone_failures += 1

        if row["nivel"] == "ambito":
            expected_unit = f"{row['id_ambito']}|{zone}"
            if row["id_ambito"] not in EXPECTED_IDS or row["unidad_id"] != expected_unit:
                identity_failures += 1
        elif row["nivel"] == "sistema":
            if (
                row["id_ambito"] != "sistema"
                or row["nombre"] != "Sistema disuelto"
                or row["unidad_id"] != f"sistema|{zone}"
            ):
                identity_failures += 1
        else:
            identity_failures += 1

        for column in NUMERIC_COLUMNS:
            value = float(row[column])
            if not math.isfinite(value):
                range_failures[f"{column}:no_finito"] += 1
        for column in [
            "area_ref_ha",
            "area_utm_ha",
            "area_pixeles_ha",
            "dif_pix_utm_abs_pct",
            "loma_ha",
            "loma_pct_unidad",
            "urbano_ha",
            "urbano_pct_unidad",
            "otras_clases_ha",
            "otras_clases_pct_unidad",
            "clasificada_ha",
            "sin_dato_ha",
            "sin_dato_pct",
        ]:
            if float(row[column]) < -1e-8:
                range_failures[f"{column}:negativo"] += 1
        for column in PERCENT_COLUMNS:
            value = float(row[column])
            if value < -1e-8 or value > 100 + 1e-6:
                range_failures[f"{column}:fuera_0_100"] += 1

        area_ref = float(row["area_ref_ha"])
        area_utm = float(row["area_utm_ha"])
        pixels = float(row["area_pixeles_ha"])
        classified = float(row["clasificada_ha"])
        no_data = float(row["sin_dato_ha"])
        loma = float(row["loma_ha"])
        urban = float(row["urbano_ha"])
        other = float(row["otras_clases_ha"])
        area_reference_differences.append(abs(area_ref - area_utm) / area_utm * 100)

        tests = {
            "pixeles=clasificada+sin_dato": close(pixels, classified + no_data),
            "clasificada=loma+urbano+otras": close(
                classified, loma + urban + other
            ),
            "dif_pix_utm_abs_pct": close(
                float(row["dif_pix_utm_abs_pct"]),
                abs(pixels - area_utm) / area_utm * 100,
            ),
            "loma_pct": close(
                float(row["loma_pct_unidad"]), loma / area_utm * 100
            ),
            "urbano_pct": close(
                float(row["urbano_pct_unidad"]), urban / area_utm * 100
            ),
            "otras_pct": close(
                float(row["otras_clases_pct_unidad"]), other / area_utm * 100
            ),
            "sin_dato_pct": close(
                float(row["sin_dato_pct"]),
                no_data / pixels * 100 if pixels else 0,
            ),
        }
        for name, passed in tests.items():
            if not passed:
                formula_failures[name] += 1

    if zone_failures:
        failures.append(f"Hay {zone_failures} filas con distancias incoherentes.")
    if identity_failures:
        failures.append(f"Hay {identity_failures} filas con identidad incoherente.")
    if range_failures:
        failures.append(f"Rangos inválidos: {dict(range_failures)}.")
    if formula_failures:
        failures.append(f"Fórmulas inconsistentes: {dict(formula_failures)}.")

    # Diferencia entre sumar ámbitos y usar la geometría disuelta del sistema.
    comparison: list[dict[str, object]] = []
    negative_overcount = 0
    for year in sorted(EXPECTED_YEARS):
        for zone in EXPECTED_ZONES:
            ambit_rows = [
                row
                for row in rows
                if row["nivel"] == "ambito"
                and row["year"] == year
                and row["zona"] == zone
            ]
            system_row = next(
                row
                for row in rows
                if row["nivel"] == "sistema"
                and row["year"] == year
                and row["zona"] == zone
            )
            ambit_sum = sum(float(row["clasificada_ha"]) for row in ambit_rows)
            system_area = float(system_row["clasificada_ha"])
            difference = ambit_sum - system_area
            if difference < -1e-5:
                negative_overcount += 1
            comparison.append(
                {
                    "year": year,
                    "zone": zone,
                    "ambit_sum": ambit_sum,
                    "system_area": system_area,
                    "difference": difference,
                }
            )
    if negative_overcount:
        warnings.append(
            f"{negative_overcount} comparaciones presentan una diferencia negativa "
            "pequeña; revisar efectos de borde antes de interpretar solapamientos."
        )

    ordered_rows = sorted(
        rows, key=lambda row: (str(row["unidad_id"]), int(row["year"]))
    )
    jumps: list[dict[str, object]] = []
    previous_by_unit: dict[str, dict[str, object]] = {}
    for row in ordered_rows:
        unit = str(row["unidad_id"])
        previous = previous_by_unit.get(unit)
        if previous:
            change = float(row["loma_pct_unidad"]) - float(
                previous["loma_pct_unidad"]
            )
            jumps.append(
                {
                    "unidad": unit,
                    "from": int(previous["year"]),
                    "to": int(row["year"]),
                    "change": change,
                    "absolute": abs(change),
                }
            )
        previous_by_unit[unit] = row
    jumps.sort(key=lambda item: float(item["absolute"]), reverse=True)

    max_no_data = max(rows, key=lambda row: float(row["sin_dato_pct"]))
    max_pixel_diff = max(
        rows, key=lambda row: float(row["dif_pix_utm_abs_pct"])
    )
    max_loma = max(rows, key=lambda row: float(row["loma_pct_unidad"]))
    max_urban = max(rows, key=lambda row: float(row["urbano_pct_unidad"]))
    overcount_by_zone = {
        zone: [
            float(item["difference"])
            for item in comparison
            if item["zone"] == zone
        ]
        for zone in EXPECTED_ZONES
    }

    digest = sha256(SOURCE)
    SHA_FILE.write_text(f"{digest}  {SOURCE.name}\n", encoding="utf-8")
    status = "PASS" if not failures else "FAIL"
    report = [
        "# Validación de indicadores de anillos 1985–2024",
        "",
        f"**Estado:** {status}  ",
        f"**Fecha:** {datetime.now().astimezone().isoformat(timespec='seconds')}  ",
        "**Grano:** unidad espacial × año  ",
        "",
        "## Perfil",
        "",
        f"- Filas: {len(rows)}.",
        f"- Columnas: {len(fieldnames)}.",
        f"- Claves únicas: {len(key_counts)}.",
        f"- Unidades por ámbito: {len(observed_ambit_units)}.",
        f"- Unidades del sistema: {len(observed_system_units)}.",
        "- Periodo: 1985–2024.",
        "",
        "## Controles",
        "",
        f"- Claves duplicadas: {len(duplicate_keys)}.",
        f"- Campos vacíos: {sum(blank_counts.values())}.",
        f"- Valores numéricos inválidos: {sum(invalid_numeric.values())}.",
        f"- Errores de distancias: {zone_failures}.",
        f"- Errores de identidad: {identity_failures}.",
        f"- Errores de fórmula: {sum(formula_failures.values())}.",
        f"- Errores de rango: {sum(range_failures.values())}.",
        (
            "- Diferencia máxima entre área de referencia y área UTM de GEE: "
            f"{max(area_reference_differences):.9f}%."
        ),
        (
            "- Diferencia máxima entre píxeles y área UTM: "
            f"{float(max_pixel_diff['dif_pix_utm_abs_pct']):.9f}% "
            f"({max_pixel_diff['unidad_id']}, {max_pixel_diff['year']})."
        ),
        (
            "- Sin dato máximo: "
            f"{float(max_no_data['sin_dato_pct']):.9f}% "
            f"({max_no_data['unidad_id']}, {max_no_data['year']})."
        ),
        "",
        "## Control de solapamiento",
        "",
        "La suma de los cinco anillos por ámbito no se utilizará como total del "
        "sistema. El control siguiente cuantifica su diferencia frente a la "
        "geometría disuelta:",
        "",
        "| Zona | Diferencia mínima (ha) | Diferencia máxima (ha) |",
        "|---|---:|---:|",
    ]
    for zone in EXPECTED_ZONES:
        values = overcount_by_zone[zone]
        report.append(f"| {zone} | {min(values):.6f} | {max(values):.6f} |")

    report.extend(
        [
            "",
            "## Extremos descriptivos",
            "",
            (
                "- Mayor proporción de loma: "
                f"{float(max_loma['loma_pct_unidad']):.6f}% "
                f"en `{max_loma['unidad_id']}`, {max_loma['year']}."
            ),
            (
                "- Mayor proporción urbana: "
                f"{float(max_urban['urbano_pct_unidad']):.6f}% "
                f"en `{max_urban['unidad_id']}`, {max_urban['year']}."
            ),
            "- Mayores cambios interanuales de loma para revisión posterior:",
            "",
            "| Unidad | Periodo | Cambio (puntos porcentuales) |",
            "|---|---:|---:|",
        ]
    )
    for item in jumps[:10]:
        report.append(
            f"| {item['unidad']} | {item['from']}–{item['to']} | "
            f"{float(item['change']):.6f} |"
        )

    report.extend(
        [
            "",
            "## Integridad",
            "",
            f"- SHA-256: `{digest}`.",
            f"- Fuente preservada sin editar: `{SOURCE}`.",
            "",
            "## Interpretación",
            "",
        ]
    )
    if status == "PASS":
        report.append(
            "El archivo es apto para continuar con la composición completa por "
            "clases. Los extremos temporales señalados son controles analíticos, "
            "no errores confirmados de MapBiomas."
        )
    else:
        report.append("El archivo no debe utilizarse todavía.")
    if warnings:
        report.extend(["", "## Advertencias", ""])
        report.extend(f"- {warning}" for warning in warnings)
    if failures:
        report.extend(["", "## Incumplimientos", ""])
        report.extend(f"- {failure}" for failure in failures)

    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

    print(f"Estado: {status}")
    print(f"Filas: {len(rows)}")
    print(f"Claves únicas: {len(key_counts)}")
    print(f"Duplicados: {len(duplicate_keys)}")
    print(f"Unidades: {len(by_unit)}")
    print(f"Máximo sin dato: {float(max_no_data['sin_dato_pct']):.9f}%")
    print(
        "Máxima diferencia píxeles–UTM: "
        f"{float(max_pixel_diff['dif_pix_utm_abs_pct']):.9f}%"
    )
    print(f"Reporte: {REPORT}")
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
