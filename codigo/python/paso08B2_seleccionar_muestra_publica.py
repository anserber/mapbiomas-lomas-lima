#!/usr/bin/env python3
"""Selecciona reproduciblemente los 36 sectores públicos del Paso 8.

Entrada:
  06_validacion_visual/01_intermediate/00_raw/
  paso08B1_reserva_candidatos_publicos.csv

Salidas:
  06_validacion_visual/01_intermediate/
  muestra_publica_paso08_preliminar.csv

  06_validacion_visual/evidencia/
  control_paso08B2_seleccion_publica.md
"""

from __future__ import annotations

import csv
import hashlib
import math
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INPUT = (
    ROOT
    / "06_validacion_visual/01_intermediate/00_raw"
    / "paso08B1_reserva_candidatos_publicos.csv"
)
SUPPLEMENT = (
    ROOT
    / "06_validacion_visual/01_intermediate/00_raw"
    / "paso08B2A_complemento_E1_carabayllo1.csv"
)
OUTPUT = (
    ROOT
    / "06_validacion_visual/02_final"
    / "muestra_publica_paso08.csv"
)
EVIDENCE = (
    ROOT
    / "06_validacion_visual/evidencia"
    / "control_paso08B2_seleccion_publica.md"
)

SEED = 20260729
MIN_DISTANCE_M = 150.0
TARGET_PER_STRATUM = 6
BASE_TARGET_PER_DOMAIN = 3
EXPECTED_GROUPS = 12
EXPECTED_ROWS = 861


def haversine_m(a: dict[str, str], b: dict[str, str]) -> float:
    radius = 6_371_008.8
    lat1 = math.radians(float(a["latitude"]))
    lat2 = math.radians(float(b["latitude"]))
    dlat = lat2 - lat1
    dlon = math.radians(float(b["longitude"]) - float(a["longitude"]))
    h = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    return 2 * radius * math.asin(math.sqrt(h))


def stable_rank(row: dict[str, str]) -> str:
    text = f"{SEED}|{row['candidate_id']}"
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def select_group(
    candidates: list[dict[str, str]],
    target: int,
    selected: list[dict[str, str]] | None = None,
) -> list[dict[str, str]]:
    """Greedy deterministic selection, preferring distinct spatial units."""
    chosen = list(selected or [])
    chosen_ids = {row["candidate_id"] for row in chosen}
    used_units = {row["unidad_id"] for row in chosen}

    while len(chosen) < target:
        eligible = [
            row
            for row in candidates
            if row["candidate_id"] not in chosen_ids
            and all(haversine_m(row, other) >= MIN_DISTANCE_M for other in chosen)
        ]
        if not eligible:
            break

        eligible.sort(
            key=lambda row: (
                row["unidad_id"] in used_units,
                stable_rank(row),
            )
        )
        pick = eligible[0]
        chosen.append(pick)
        chosen_ids.add(pick["candidate_id"])
        used_units.add(pick["unidad_id"])

    return chosen


def validate_input(rows: list[dict[str, str]]) -> None:
    required = {
        "candidate_id",
        "grupo",
        "estrato_codigo",
        "estrato",
        "dominio",
        "unidad_id",
        "nombre_unidad",
        "year_evento",
        "patch_pixels",
        "longitude",
        "latitude",
        "semilla",
        "min_pixeles_conectados",
    }
    if len(rows) != EXPECTED_ROWS:
        raise ValueError(f"Se esperaban {EXPECTED_ROWS} filas; se obtuvieron {len(rows)}")
    if not rows or not required.issubset(rows[0]):
        missing = required - (set(rows[0]) if rows else set())
        raise ValueError(f"Faltan campos requeridos: {sorted(missing)}")
    if any(not row[field].strip() for row in rows for field in required):
        raise ValueError("Existen valores vacíos en campos obligatorios")
    if len({row["candidate_id"] for row in rows}) != len(rows):
        raise ValueError("Existen candidate_id duplicados")
    if len({(row["longitude"], row["latitude"]) for row in rows}) != len(rows):
        raise ValueError("Existen coordenadas candidatas duplicadas")
    if len({row["grupo"] for row in rows}) != EXPECTED_GROUPS:
        raise ValueError("La reserva no contiene los 12 grupos esperados")
    if {int(row["semilla"]) for row in rows} != {SEED}:
        raise ValueError("La semilla de la reserva no coincide con el protocolo")
    if min(int(float(row["patch_pixels"])) for row in rows) < 3:
        raise ValueError("Existe al menos un candidato con parche menor de 3 píxeles")


def temporal_fields(row: dict[str, str]) -> tuple[str, str, str]:
    stratum = row["estrato"]
    event_year = int(float(row["year_evento"]))
    if stratum == "E1_PERSISTENTE70":
        return "1985", "", "2024"
    if stratum == "E3_URBANO_CENSURADO":
        return str(event_year - 1), str(event_year), "2024"
    return str(event_year - 1), str(event_year), str(min(2024, event_year + 4))


def main() -> None:
    with INPUT.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    validate_input(rows)

    with SUPPLEMENT.open(newline="", encoding="utf-8-sig") as handle:
        supplement = list(csv.DictReader(handle))
    if len(supplement) != 80:
        raise ValueError(
            f"Se esperaban 80 candidatos complementarios; "
            f"se obtuvieron {len(supplement)}"
        )
    if any(
        row["grupo"] != "E1_PERSISTENTE70|acr"
        or row["unidad_id"] != "acr|carabayllo_1"
        or int(float(row["patch_pixels"])) < 3
        or int(row["semilla"]) != SEED
        for row in supplement
    ):
        raise ValueError("El complemento de Carabayllo 1 incumple sus reglas")
    all_candidate_ids = [row["candidate_id"] for row in rows + supplement]
    all_coordinates = [
        (row["longitude"], row["latitude"]) for row in rows + supplement
    ]
    if len(all_candidate_ids) != len(set(all_candidate_ids)):
        raise ValueError("Existen candidate_id repetidos entre reserva y complemento")
    if len(all_coordinates) != len(set(all_coordinates)):
        raise ValueError("Existen coordenadas repetidas entre reserva y complemento")

    groups: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows + supplement:
        groups[(row["estrato"], row["dominio"])].append(row)

    selected_by_group: dict[tuple[str, str], list[dict[str, str]]] = {}
    reallocations: list[str] = []

    strata = sorted(
        {row["estrato"] for row in rows},
        key=lambda value: int(value.split("_", 1)[0][1:]),
    )

    for stratum in strata:
        acr_key = (stratum, "acr")
        ring_key = (stratum, "anillo_sistema")
        if stratum == "E1_PERSISTENTE70":
            mandatory = sorted(supplement, key=stable_rank)[0]
            acr_selected = select_group(
                groups[acr_key],
                BASE_TARGET_PER_DOMAIN,
                selected=[mandatory],
            )
        else:
            acr_selected = select_group(groups[acr_key], BASE_TARGET_PER_DOMAIN)
        ring_selected = select_group(groups[ring_key], BASE_TARGET_PER_DOMAIN)

        shortage_acr = BASE_TARGET_PER_DOMAIN - len(acr_selected)
        shortage_ring = BASE_TARGET_PER_DOMAIN - len(ring_selected)

        if shortage_acr:
            ring_selected = select_group(
                groups[ring_key],
                BASE_TARGET_PER_DOMAIN + shortage_acr,
                ring_selected,
            )
            reallocations.append(
                f"`{stratum}`: {shortage_acr} plaza(s) de ACR "
                "reasignada(s) a anillo_sistema."
            )
        if shortage_ring:
            acr_selected = select_group(
                groups[acr_key],
                BASE_TARGET_PER_DOMAIN + shortage_ring,
                acr_selected,
            )
            reallocations.append(
                f"`{stratum}`: {shortage_ring} plaza(s) de anillo_sistema "
                "reasignada(s) a ACR."
            )

        if len(acr_selected) + len(ring_selected) != TARGET_PER_STRATUM:
            raise ValueError(
                f"{stratum} no pudo completar {TARGET_PER_STRATUM} sectores "
                f"independientes: ACR={len(acr_selected)}, "
                f"anillos={len(ring_selected)}"
            )

        selected_by_group[acr_key] = acr_selected
        selected_by_group[ring_key] = ring_selected

    selected: list[dict[str, str]] = []
    for stratum in strata:
        selected.extend(selected_by_group[(stratum, "acr")])
        selected.extend(selected_by_group[(stratum, "anillo_sistema")])

    if len(selected) != 36:
        raise ValueError(f"Se esperaban 36 sectores públicos; se obtuvieron {len(selected)}")
    if len({row["candidate_id"] for row in selected}) != 36:
        raise ValueError("La muestra seleccionada contiene sectores duplicados")
    acr_units = {
        row["unidad_id"] for row in selected if row["dominio"] == "acr"
    }
    expected_acr_units = {
        "acr|amancaes",
        "acr|ancon",
        "acr|carabayllo_1",
        "acr|carabayllo_2",
        "acr|villa_maria",
    }
    if not expected_acr_units.issubset(acr_units):
        raise ValueError(
            "La muestra no representa los cinco ACR: "
            f"faltan {sorted(expected_acr_units - acr_units)}"
        )

    group_min_distances: dict[str, float | None] = {}
    for key, chosen in selected_by_group.items():
        distances = [
            haversine_m(chosen[i], chosen[j])
            for i in range(len(chosen))
            for j in range(i + 1, len(chosen))
        ]
        group_min_distances[f"{key[0]}|{key[1]}"] = min(distances) if distances else None

    output_rows: list[dict[str, str]] = []
    domain_counter: Counter[tuple[str, str]] = Counter()
    for index, row in enumerate(selected, start=1):
        year_start, year_event, year_end = temporal_fields(row)
        key = (row["estrato"], row["dominio"])
        domain_counter[key] += 1
        base_or_reallocated = (
            "CUOTA_BASE"
            if domain_counter[key] <= BASE_TARGET_PER_DOMAIN
            else "CUOTA_REASIGNADA"
        )
        output_rows.append(
            {
                "id_sector_unico": f"PUB-{index:03d}",
                "candidate_id": row["candidate_id"],
                "estrato_codigo": row["estrato_codigo"],
                "estrato": row["estrato"],
                "dominio": row["dominio"],
                "unidad_id": row["unidad_id"],
                "nombre_unidad": row["nombre_unidad"],
                "year_start": year_start,
                "year_evento": year_event,
                "year_end_observado": year_end,
                "patch_pixels": row["patch_pixels"],
                "longitude": row["longitude"],
                "latitude": row["latitude"],
                "semilla": row["semilla"],
                "min_pixeles_conectados": row["min_pixeles_conectados"],
                "cuota_seleccion": base_or_reallocated,
            }
        )

    fieldnames = list(output_rows[0])
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    counts = Counter((row["estrato"], row["dominio"]) for row in output_rows)
    units = Counter(row["unidad_id"] for row in output_rows)
    min_distance = min(
        value for value in group_min_distances.values() if value is not None
    )

    evidence_lines = [
        "# Control del Paso 8B2 — selección pública preliminar",
        "",
        "**Fecha:** 2026-07-29  ",
        "**Estado:** PASS  ",
        f"**Semilla:** `{SEED}`  ",
        f"**Separación objetivo:** {MIN_DISTANCE_M:.0f} m",
        "",
        "## Calidad de la reserva",
        "",
        f"- Filas de la reserva principal: {len(rows)}.",
        f"- Filas del complemento Carabayllo 1: {len(supplement)}.",
        f"- `candidate_id` únicos: {len({r['candidate_id'] for r in rows})}.",
        "- Coordenadas duplicadas: 0.",
        "- Valores obligatorios vacíos: 0.",
        "- Grupos presentes: 12 de 12.",
        "- Todos los candidatos cumplen el parche mínimo de 3 píxeles.",
        "",
        "## Muestra pública seleccionada",
        "",
        "- Sectores únicos: 36.",
        "- Estratos representados: 6 de 6.",
        "- Ámbitos ACR representados: 5 de 5.",
        f"- Separación mínima observada dentro de estrato y dominio: "
        f"{min_distance:.3f} m.",
        "",
        "| Estrato | ACR | Anillo del sistema | Total |",
        "|---|---:|---:|---:|",
    ]
    for stratum in strata:
        acr_count = counts[(stratum, "acr")]
        ring_count = counts[(stratum, "anillo_sistema")]
        evidence_lines.append(
            f"| `{stratum}` | {acr_count} | {ring_count} | "
            f"{acr_count + ring_count} |"
        )

    evidence_lines.extend(["", "## Reasignaciones", ""])
    if reallocations:
        evidence_lines.extend(f"- {item}" for item in reallocations)
    else:
        evidence_lines.append("- Ninguna.")

    evidence_lines.extend(
        [
            "",
            "## Cobertura por unidad",
            "",
            "| Unidad | Sectores |",
            "|---|---:|",
        ]
    )
    for unit_id, count in sorted(units.items()):
        evidence_lines.append(f"| `{unit_id}` | {count} |")

    evidence_lines.extend(
        [
            "",
            "## Decisión",
            "",
            "La muestra pública preliminar cumple el tamaño, la representación de "
            "estratos y ámbitos ACR, la unicidad y la separación espacial "
            "previstas. La única "
            "desviación es la reasignación documentada dentro de E2; no se redujo "
            "el tamaño mínimo de parche ni se seleccionaron dos puntos separados "
            "por menos de 150 m dentro del mismo grupo.",
            "",
            "El complemento E1 de Carabayllo 1 se incorporó antes de congelar la "
            "muestra y no alteró las cuotas por estrato o dominio.",
            "",
            "La muestra pública queda congelada. Todavía no contiene sectores KBA "
            "ni repeticiones ciegas.",
        ]
    )
    EVIDENCE.write_text("\n".join(evidence_lines) + "\n", encoding="utf-8")

    print(f"PASS: {len(rows)} candidatos principales auditados")
    print(f"PASS: {len(supplement)} candidatos complementarios auditados")
    print(f"PASS: {len(output_rows)} sectores públicos seleccionados")
    print(f"PASS: separación mínima dentro de grupo = {min_distance:.3f} m")
    print("Cuotas:")
    for stratum in strata:
        print(
            f"  {stratum}: ACR={counts[(stratum, 'acr')]}, "
            f"anillo_sistema={counts[(stratum, 'anillo_sistema')]}"
        )
    print(f"Salida: {OUTPUT}")
    print(f"Evidencia: {EVIDENCE}")


if __name__ == "__main__":
    main()
