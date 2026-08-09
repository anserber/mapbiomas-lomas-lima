#!/usr/bin/env python3
"""Congela 60 sectores y crea 6 repeticiones ciegas del Paso 8."""

from __future__ import annotations

import csv
import hashlib
import random
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PUBLIC = ROOT / "06_validacion_visual/02_final/muestra_publica_paso08.csv"
KBA = ROOT / "06_validacion_visual/kba_restricted/muestra_kba_paso08.csv"
RESTRICTED = ROOT / "06_validacion_visual/kba_restricted"
BLIND = RESTRICTED / "instrumento_evaluacion_visual_ciego_paso08.csv"
KEY = RESTRICTED / "clave_repeticiones_ciegas_paso08.csv"
MANIFEST = (
    ROOT
    / "06_validacion_visual/02_final"
    / "muestra_total_paso08_sin_coordenadas_kba.csv"
)
EVIDENCE = (
    ROOT
    / "06_validacion_visual/evidencia"
    / "control_paso08C_cierre_muestra.md"
)

SEED = 20260729
STRATA = [
    "E1_PERSISTENTE70",
    "E2_URBANO_W5",
    "E3_URBANO_CENSURADO",
    "E4_INTERCAMBIO_68_70",
    "E5_RECUPERACION_68_70",
    "E6_CAMBIO_70_13",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def rank(row: dict[str, str], salt: str) -> str:
    value = f"{SEED}|{salt}|{row['id_sector_unico']}|{row['candidate_id']}"
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def validate(public: list[dict[str, str]], kba: list[dict[str, str]]) -> None:
    if len(public) != 36 or len(kba) != 24:
        raise ValueError(
            f"Tamaños incorrectos: público={len(public)}, KBA={len(kba)}"
        )
    combined = public + kba
    if len({row["id_sector_unico"] for row in combined}) != 60:
        raise ValueError("Los id_sector_unico no son únicos")
    if len({row["candidate_id"] for row in combined}) != 60:
        raise ValueError("Los candidate_id no son únicos")
    if set(row["estrato"] for row in combined) != set(STRATA):
        raise ValueError("No están representados los seis estratos")
    if any(
        not row.get(field, "").strip()
        for row in combined
        for field in (
            "id_sector_unico",
            "candidate_id",
            "estrato",
            "dominio",
            "unidad_id",
            "nombre_unidad",
            "year_start",
            "year_end_observado",
            "longitude",
            "latitude",
        )
    ):
        raise ValueError("Hay campos obligatorios vacíos")


def choose_repeats(
    public: list[dict[str, str]], kba: list[dict[str, str]]
) -> list[dict[str, str]]:
    repeats: list[dict[str, str]] = []
    for index, stratum in enumerate(STRATA):
        source = public if index % 2 == 0 else kba
        candidates = [row for row in source if row["estrato"] == stratum]
        candidates.sort(key=lambda row: rank(row, "repeat"))
        repeats.append(candidates[0])
    return repeats


def shuffled_records(
    unique_rows: list[dict[str, str]],
    repeats: list[dict[str, str]],
) -> list[tuple[dict[str, str], bool]]:
    records = [(row, False) for row in unique_rows] + [
        (row, True) for row in repeats
    ]
    repeated_ids = {row["id_sector_unico"] for row in repeats}
    for attempt in range(10_000):
        trial = list(records)
        random.Random(SEED + attempt).shuffle(trial)
        positions: dict[str, list[int]] = {}
        for position, (row, _) in enumerate(trial, start=1):
            if row["id_sector_unico"] in repeated_ids:
                positions.setdefault(row["id_sector_unico"], []).append(position)
        if all(
            len(values) == 2 and abs(values[0] - values[1]) >= 10
            for values in positions.values()
        ):
            return trial
    raise ValueError("No se logró separar las repeticiones ciegas en el orden")


def main() -> None:
    public = read_csv(PUBLIC)
    kba = read_csv(KBA)
    validate(public, kba)
    unique_rows = public + kba
    repeats = choose_repeats(public, kba)
    records = shuffled_records(unique_rows, repeats)

    blind_rows: list[dict[str, str]] = []
    key_rows: list[dict[str, str]] = []
    for index, (row, is_repeat) in enumerate(records, start=1):
        evaluation_id = f"EVAL-{index:03d}"
        blind_rows.append(
            {
                "id_muestra": evaluation_id,
                "dominio": row["dominio"],
                "unidad_id": row["unidad_id"],
                "nombre_unidad": row["nombre_unidad"],
                "estrato": row["estrato"],
                "year_start": row["year_start"],
                "year_evento": row["year_evento"],
                "year_end_observado": row["year_end_observado"],
                "longitude": row["longitude"],
                "latitude": row["latitude"],
                "fuente_visual_1": "",
                "fecha_fuente_1": "",
                "fuente_visual_2": "",
                "fecha_fuente_2": "",
                "evidencia_suficiente": "",
                "veredicto_visual": "",
                "proceso_observado": "",
                "confianza": "",
                "observaciones": "",
                "evaluador": "",
                "fecha_revision": "",
            }
        )
        key_rows.append(
            {
                "id_muestra": evaluation_id,
                "id_sector_unico": row["id_sector_unico"],
                "candidate_id": row["candidate_id"],
                "es_repeticion_ciega": "SI" if is_repeat else "NO",
            }
        )

    with BLIND.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(blind_rows[0]))
        writer.writeheader()
        writer.writerows(blind_rows)
    with KEY.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(key_rows[0]))
        writer.writeheader()
        writer.writerows(key_rows)

    manifest_rows: list[dict[str, str]] = []
    for row in unique_rows:
        is_kba = row["dominio"] == "kba_restricted"
        manifest_rows.append(
            {
                "id_sector_unico": row["id_sector_unico"],
                "estrato": row["estrato"],
                "dominio": row["dominio"],
                "unidad_id": row["unidad_id"],
                "nombre_unidad": row["nombre_unidad"],
                "year_start": row["year_start"],
                "year_evento": row["year_evento"],
                "year_end_observado": row["year_end_observado"],
                "longitude": "" if is_kba else row["longitude"],
                "latitude": "" if is_kba else row["latitude"],
                "coordenadas_restringidas": "SI" if is_kba else "NO",
            }
        )
    with MANIFEST.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(manifest_rows[0]))
        writer.writeheader()
        writer.writerows(manifest_rows)

    repeated_domains = Counter(row["dominio"] for row in repeats)
    repeated_strata = Counter(row["estrato"] for row in repeats)
    positions: dict[str, list[int]] = {}
    for position, key in enumerate(key_rows, start=1):
        if key["id_sector_unico"] in {
            row["id_sector_unico"] for row in repeats
        }:
            positions.setdefault(key["id_sector_unico"], []).append(position)
    minimum_gap = min(abs(values[0] - values[1]) for values in positions.values())

    lines = [
        "# Control del Paso 8C — cierre de muestra",
        "",
        "**Fecha:** 2026-07-29  ",
        "**Estado:** PASS  ",
        f"**Semilla:** `{SEED}`",
        "",
        "## Muestra congelada",
        "",
        "- Sectores públicos únicos: 36.",
        "- Sectores KBA restringidos únicos: 24.",
        "- Sectores únicos totales: 60.",
        "- Repeticiones ciegas: 6.",
        "- Evaluaciones totales: 66.",
        "- Estratos representados: 6 de 6.",
        "- Una repetición ciega por estrato.",
        f"- Repeticiones públicas: {repeated_domains['acr'] + repeated_domains['anillo_sistema']}.",
        f"- Repeticiones KBA: {repeated_domains['kba_restricted']}.",
        f"- Separación mínima en el orden entre original y repetición: "
        f"{minimum_gap} evaluaciones.",
        "",
        "## Blindaje",
        "",
        "El instrumento operativo no contiene `id_sector_unico` ni el indicador "
        "`es_repeticion_ciega`. La clave permanece en la carpeta restringida y "
        "no debe abrirse durante la evaluación.",
        "",
        "El manifiesto compartible omite las coordenadas de los 24 sectores KBA.",
        "",
        "## Regla de uso",
        "",
        "No reemplazar sectores después de observar las imágenes. Los casos con "
        "evidencia insuficiente deben conservarse como `INDETERMINADO`.",
    ]
    EVIDENCE.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("PASS: 60 sectores únicos congelados")
    print("PASS: 6 repeticiones ciegas; 66 evaluaciones")
    print(f"PASS: separación mínima original-repetición = {minimum_gap}")
    print(f"Instrumento restringido: {BLIND}")
    print(f"Manifiesto sin coordenadas KBA: {MANIFEST}")
    print(f"Control: {EVIDENCE}")


if __name__ == "__main__":
    main()
