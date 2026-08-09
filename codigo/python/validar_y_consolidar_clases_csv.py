#!/usr/bin/env python3
"""Consolida y audita los ocho CSV de composición por clases de MapBiomas."""

from __future__ import annotations

import csv
import hashlib
import math
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "04_extraccion_series/02_resultados/00_raw"
RESULTS = ROOT / "04_extraccion_series/02_resultados"

BLOCKS = [
    (1985, 1989),
    (1990, 1994),
    (1995, 1999),
    (2000, 2004),
    (2005, 2009),
    (2010, 2014),
    (2015, 2019),
    (2020, 2024),
]
EXPECTED_IDS = {
    "amancaes",
    "ancon",
    "carabayllo_1",
    "carabayllo_2",
    "villa_maria",
}
EXPECTED_COLUMNS = [
    "id_ambito",
    "nombre",
    "year",
    "class_id",
    "class_name",
    "class_origin",
    "area_ref_ha",
    "area_utm_ha",
    "area_ha",
    "area_pct_ambito",
]
CLASS_CATALOG = {
    4: ("Bosque seco", "Natural"),
    13: ("Otra formación no boscosa", "Natural"),
    21: ("Mosaico agropecuario", "Antrópico"),
    24: ("Infraestructura urbana", "Antrópico"),
    66: ("Matorral", "Natural"),
    68: ("Otra área natural sin vegetación", "Natural"),
    70: ("Loma costera", "Natural"),
}

OUT_CSV = RESULTS / "serie_clases_acr_1985_2024.csv"
REPORT = RESULTS / "validacion_serie_clases_acr_1985_2024.md"
OUT_SHA = RESULTS / "serie_clases_acr_1985_2024.csv.sha256"
INPUT_MANIFEST = RAW / "manifest_sha256_serie_clases.txt"
INDICATORS = RAW / "serie_indicadores_acr_1985_2024.csv"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def close(a: float, b: float, tolerance: float = 1e-6) -> bool:
    return math.isclose(a, b, rel_tol=0.0, abs_tol=tolerance)


def main() -> None:
    failures: list[str] = []
    warnings: list[str] = []
    rows: list[dict[str, object]] = []
    input_paths: list[Path] = []
    block_counts: dict[str, int] = {}

    for start, end in BLOCKS:
        path = RAW / f"serie_clases_acr_{start}_{end}.csv"
        input_paths.append(path)
        if not path.exists():
            failures.append(f"Falta el archivo `{path.name}`.")
            continue

        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != EXPECTED_COLUMNS:
                failures.append(
                    f"`{path.name}` tiene un esquema diferente: {reader.fieldnames}."
                )
                continue

            block_rows = list(reader)
            block_counts[f"{start}–{end}"] = len(block_rows)
            years_in_block: set[int] = set()
            ids_in_block: set[str] = set()

            for line_number, raw in enumerate(block_rows, start=2):
                try:
                    year_value = float(raw["year"])
                    if not year_value.is_integer():
                        raise ValueError("año no entero")
                    year = int(year_value)
                    class_id = int(raw["class_id"])
                    parsed = {
                        "id_ambito": raw["id_ambito"].strip(),
                        "nombre": raw["nombre"].strip(),
                        "year": year,
                        "class_id": class_id,
                        "class_name": raw["class_name"].strip(),
                        "class_origin": raw["class_origin"].strip(),
                        "area_ref_ha": float(raw["area_ref_ha"]),
                        "area_utm_ha": float(raw["area_utm_ha"]),
                        "area_ha": float(raw["area_ha"]),
                        "area_pct_ambito": float(raw["area_pct_ambito"]),
                    }
                except (TypeError, ValueError) as exc:
                    failures.append(
                        f"`{path.name}`, línea {line_number}: valor inválido ({exc})."
                    )
                    continue

                years_in_block.add(year)
                ids_in_block.add(str(parsed["id_ambito"]))
                if not start <= year <= end:
                    failures.append(
                        f"`{path.name}` contiene el año {year}, fuera de {start}–{end}."
                    )
                rows.append(parsed)

            expected_years = set(range(start, end + 1))
            if years_in_block != expected_years:
                failures.append(
                    f"`{path.name}` no cubre exactamente {start}–{end}: "
                    f"{sorted(years_in_block)}."
                )
            if ids_in_block != EXPECTED_IDS:
                failures.append(
                    f"`{path.name}` no contiene exactamente los cinco ámbitos: "
                    f"{sorted(ids_in_block)}."
                )

    key_counts = Counter(
        (r["id_ambito"], r["year"], r["class_id"]) for r in rows
    )
    duplicate_keys = [key for key, count in key_counts.items() if count > 1]
    if duplicate_keys:
        failures.append(
            f"Hay {len(duplicate_keys)} claves duplicadas ámbito–año–clase."
        )

    pairs = {(r["id_ambito"], r["year"]) for r in rows}
    expected_pairs = {
        (id_ambito, year)
        for id_ambito in EXPECTED_IDS
        for year in range(1985, 2025)
    }
    missing_pairs = expected_pairs - pairs
    extra_pairs = pairs - expected_pairs
    if missing_pairs:
        failures.append(f"Faltan {len(missing_pairs)} combinaciones ámbito–año.")
    if extra_pairs:
        failures.append(f"Hay {len(extra_pairs)} combinaciones ámbito–año extra.")

    empty_required = 0
    invalid_catalog = 0
    invalid_numeric = 0
    invalid_pct_formula = 0
    for row in rows:
        if any(
            str(row[column]).strip() == ""
            for column in [
                "id_ambito",
                "nombre",
                "class_name",
                "class_origin",
            ]
        ):
            empty_required += 1

        class_id = int(row["class_id"])
        expected_definition = CLASS_CATALOG.get(class_id)
        observed_definition = (row["class_name"], row["class_origin"])
        if expected_definition != observed_definition:
            invalid_catalog += 1

        area_ref = float(row["area_ref_ha"])
        area_utm = float(row["area_utm_ha"])
        area = float(row["area_ha"])
        pct = float(row["area_pct_ambito"])
        if (
            area_ref <= 0
            or area_utm <= 0
            or area < 0
            or pct < 0
            or pct > 100
            or not all(math.isfinite(x) for x in [area_ref, area_utm, area, pct])
        ):
            invalid_numeric += 1
        if area_utm > 0 and not close(pct, area / area_utm * 100, 1e-6):
            invalid_pct_formula += 1

    if empty_required:
        failures.append(f"Hay {empty_required} filas con texto obligatorio vacío.")
    if invalid_catalog:
        failures.append(
            f"Hay {invalid_catalog} filas incompatibles con el catálogo de clases."
        )
    if invalid_numeric:
        failures.append(f"Hay {invalid_numeric} filas con áreas o porcentajes inválidos.")
    if invalid_pct_formula:
        failures.append(
            f"Hay {invalid_pct_formula} filas cuyo porcentaje no coincide con "
            "`area_ha / area_utm_ha × 100`."
        )

    reference_values: dict[str, set[tuple[float, float, str]]] = defaultdict(set)
    for row in rows:
        reference_values[str(row["id_ambito"])].add(
            (
                float(row["area_ref_ha"]),
                float(row["area_utm_ha"]),
                str(row["nombre"]),
            )
        )
    inconsistent_reference = {
        key: values for key, values in reference_values.items() if len(values) != 1
    }
    if inconsistent_reference:
        failures.append(
            f"{len(inconsistent_reference)} ámbitos cambian de nombre o superficie "
            "entre años/clases."
        )

    # Concordancia con la tabla independiente de indicadores.
    indicator_rows: dict[tuple[str, int], dict[str, str]] = {}
    if not INDICATORS.exists():
        failures.append(f"Falta la tabla de control `{INDICATORS.name}`.")
    else:
        with INDICATORS.open("r", encoding="utf-8-sig", newline="") as handle:
            for raw in csv.DictReader(handle):
                year = int(float(raw["year"]))
                indicator_rows[(raw["id_ambito"].strip(), year)] = raw

    if set(indicator_rows) != expected_pairs:
        failures.append(
            "La tabla de indicadores no contiene exactamente las 200 claves "
            "ámbito–año esperadas."
        )

    by_pair: dict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        by_pair[(str(row["id_ambito"]), int(row["year"]))].append(row)

    comparison_diffs = {
        "area_total": [],
        "loma": [],
        "urbano": [],
        "otras": [],
    }
    mismatch_pairs = 0
    sum_pct_min = float("inf")
    sum_pct_max = float("-inf")
    for key, group in by_pair.items():
        indicator = indicator_rows.get(key)
        if not indicator:
            continue
        total = sum(float(row["area_ha"]) for row in group)
        loma = sum(
            float(row["area_ha"]) for row in group if int(row["class_id"]) == 70
        )
        urbano = sum(
            float(row["area_ha"]) for row in group if int(row["class_id"]) == 24
        )
        otras = total - loma - urbano
        pct_sum = sum(float(row["area_pct_ambito"]) for row in group)
        sum_pct_min = min(sum_pct_min, pct_sum)
        sum_pct_max = max(sum_pct_max, pct_sum)

        diffs = {
            "area_total": abs(total - float(indicator["area_pixeles_ha"])),
            "loma": abs(loma - float(indicator["loma_ha"])),
            "urbano": abs(urbano - float(indicator["urbano_ha"])),
            "otras": abs(otras - float(indicator["otras_clases_ha"])),
        }
        for metric, difference in diffs.items():
            comparison_diffs[metric].append(difference)
        if any(difference > 1e-6 for difference in diffs.values()):
            mismatch_pairs += 1

    if mismatch_pairs:
        failures.append(
            f"{mismatch_pairs} claves ámbito–año no concuerdan con la tabla de "
            "indicadores al nivel de tolerancia 0.000001 ha."
        )

    rows.sort(
        key=lambda r: (
            str(r["id_ambito"]),
            int(r["year"]),
            int(r["class_id"]),
        )
    )
    RESULTS.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=EXPECTED_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    input_manifest_lines = [
        f"{sha256(path)}  {path.name}" for path in input_paths if path.exists()
    ]
    INPUT_MANIFEST.write_text(
        "\n".join(input_manifest_lines) + "\n", encoding="utf-8"
    )
    out_hash = sha256(OUT_CSV)
    OUT_SHA.write_text(f"{out_hash}  {OUT_CSV.name}\n", encoding="utf-8")

    observed_classes = sorted({int(row["class_id"]) for row in rows})
    max_diffs = {
        metric: max(values, default=0.0)
        for metric, values in comparison_diffs.items()
    }
    total_input_size = sum(path.stat().st_size for path in input_paths if path.exists())
    status = "PASS" if not failures else "FAIL"
    report_lines = [
        "# Validación de la serie de clases ACR 1985–2024",
        "",
        f"**Estado:** {status}  ",
        f"**Fecha de ejecución:** {datetime.now().astimezone().isoformat(timespec='seconds')}  ",
        "**Grano esperado:** ámbito × año × clase  ",
        "",
        "## Resumen del conjunto",
        "",
        f"- Archivos fuente: {len(input_paths)}.",
        f"- Tamaño total de fuentes: {total_input_size:,} bytes.",
        f"- Filas consolidadas: {len(rows)}.",
        f"- Columnas: {len(EXPECTED_COLUMNS)}.",
        f"- Ámbitos: {len({str(r['id_ambito']) for r in rows})}.",
        f"- Años: {min(int(r['year']) for r in rows)}–{max(int(r['year']) for r in rows)}.",
        f"- Combinaciones ámbito–año: {len(pairs)} de 200 esperadas.",
        f"- Clases observadas: {', '.join(map(str, observed_classes))}.",
        "",
        "## Filas por bloque",
        "",
        "| Bloque | Filas |",
        "|---|---:|",
    ]
    report_lines.extend(
        f"| {block} | {count} |" for block, count in block_counts.items()
    )
    report_lines.extend(
        [
            "",
            "## Controles de calidad",
            "",
            f"- Claves duplicadas ámbito–año–clase: {len(duplicate_keys)}.",
            f"- Combinaciones ámbito–año faltantes: {len(missing_pairs)}.",
            f"- Valores de texto obligatorios vacíos: {empty_required}.",
            f"- Filas incompatibles con el catálogo: {invalid_catalog}.",
            f"- Filas con áreas o porcentajes inválidos: {invalid_numeric}.",
            f"- Errores en la fórmula porcentual: {invalid_pct_formula}.",
            f"- Ámbitos con referencia inconsistente: {len(inconsistent_reference)}.",
            (
                "- Rango de la suma de clases por ámbito–año: "
                f"{sum_pct_min:.9f}%–{sum_pct_max:.9f}%."
            ),
            "",
            "## Concordancia con serie_indicadores_acr_1985_2024.csv",
            "",
            f"- Claves comparadas: {len(by_pair)}.",
            f"- Claves con diferencias > 0.000001 ha: {mismatch_pairs}.",
            f"- Diferencia máxima en superficie clasificada: {max_diffs['area_total']:.12f} ha.",
            f"- Diferencia máxima en loma costera: {max_diffs['loma']:.12f} ha.",
            f"- Diferencia máxima en infraestructura urbana: {max_diffs['urbano']:.12f} ha.",
            f"- Diferencia máxima en otras clases: {max_diffs['otras']:.12f} ha.",
            "",
            "## Catálogo observado",
            "",
            "| Código | Clase | Origen |",
            "|---:|---|---|",
        ]
    )
    report_lines.extend(
        f"| {code} | {CLASS_CATALOG[code][0]} | {CLASS_CATALOG[code][1]} |"
        for code in observed_classes
    )
    report_lines.extend(
        [
            "",
            "## Integridad y procedencia",
            "",
            f"- CSV consolidado: `{OUT_CSV.name}`.",
            f"- SHA-256 consolidado: `{out_hash}`.",
            f"- Manifiesto de fuentes: `{INPUT_MANIFEST.name}`.",
            "",
            "## Interpretación",
            "",
        ]
    )
    if status == "PASS":
        report_lines.extend(
            [
                "La serie consolidada es apta para el análisis descriptivo y temporal "
                "del proyecto. Los ocho bloques conservan el mismo esquema, cubren los "
                "cinco ámbitos y los cuarenta años, y reproducen la tabla independiente "
                "de indicadores dentro de la tolerancia numérica establecida.",
                "",
                "La ausencia de una clase en una combinación ámbito–año representa "
                "área cero para esa clase; no constituye un dato faltante.",
            ]
        )
    else:
        report_lines.append(
            "La serie no debe utilizarse todavía como insumo analítico."
        )
    if warnings:
        report_lines.extend(["", "## Advertencias", ""])
        report_lines.extend(f"- {warning}" for warning in warnings)
    if failures:
        report_lines.extend(["", "## Incumplimientos", ""])
        report_lines.extend(f"- {failure}" for failure in failures)

    REPORT.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(f"Estado: {status}")
    print(f"Filas consolidadas: {len(rows)}")
    print(f"Claves ámbito–año–clase duplicadas: {len(duplicate_keys)}")
    print(f"Combinaciones ámbito–año: {len(pairs)}/200")
    print(f"Clases observadas: {observed_classes}")
    print(f"Claves discrepantes frente a indicadores: {mismatch_pairs}")
    print(f"CSV: {OUT_CSV}")
    print(f"Reporte: {REPORT}")
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
