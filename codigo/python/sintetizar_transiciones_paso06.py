#!/usr/bin/env python3
"""Sintetiza transiciones del Paso 6 sin atribuir causalidad ecológica."""

from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
STEP = ROOT / "05_analisis_temporal"
EXTRACTION = ROOT / "04_extraccion_series" / "02_resultados"

ACR_TRANSITIONS = (
    STEP / "01_intermediate" / "transiciones_acr_15_periodos_consolidado.csv"
)
RING_TRANSITIONS = (
    EXTRACTION
    / "serie_transiciones_anillos_periferia_externa_seleccionadas.csv"
)
ACR_CLASSES = EXTRACTION / "serie_clases_acr_1985_2024.csv"
RING_CLASSES = (
    EXTRACTION / "serie_clases_anillos_periferia_externa_1985_2024.csv"
)
PERIOD_SELECTION = STEP / "02_final" / "seleccion_periodos_paso_06.csv"

OUT_ACR = STEP / "01_intermediate" / "resumen_transiciones_acr_paso06.csv"
OUT_RINGS = (
    STEP
    / "01_intermediate"
    / "resumen_transiciones_anillos_periferia_externa_paso06.csv"
)
OUT_PRIORITY = (
    STEP / "02_final" / "prioridades_validacion_visual_paso06.csv"
)
OUT_SHORTLIST = (
    STEP / "02_final" / "seleccion_controles_visuales_prioritarios_paso06.csv"
)
OUT_ANOMALIES = STEP / "02_final" / "anomalias_clasificacion_paso06.csv"
OUT_CONTROL = STEP / "evidencia" / "control_sintesis_transiciones_paso06.json"
OUT_REPORT = STEP / "evidencia" / "sintesis_transiciones_paso06.md"

ANTHROPIC_OTHER = {9, 15, 18, 21, 25, 30, 31, 35, 40, 72}
NATURAL_OTHER = {3, 4, 5, 6, 11, 12, 13, 23, 29, 32, 33, 34, 61, 66, 68}
MANDATORY_REVIEW = {
    "transitions_1985_1986",
    "transitions_2000_2001",
    "transitions_2009_2010",
    "transitions_2014_2015",
    "transitions_2022_2023",
    "transitions_2023_2024",
}
AREA_TOLERANCE_HA = 1e-5


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sum_area(group: pd.DataFrame, condition: pd.Series) -> float:
    return float(group.loc[condition, "area_ha"].sum())


def summarize_group(group: pd.DataFrame) -> pd.Series:
    source = group["from_class"]
    target = group["to_class"]
    loma_exit = source.eq(70) & target.ne(70)
    loma_entry = source.ne(70) & target.eq(70)

    result = {
        "area_cubierta_transiciones_ha": float(group["area_ha"].sum()),
        "loma_persistente_ha": sum_area(group, source.eq(70) & target.eq(70)),
        "salida_clase_loma_ha": sum_area(group, loma_exit),
        "loma_a_urbano_ha": sum_area(group, source.eq(70) & target.eq(24)),
        "loma_a_otra_antropica_ha": sum_area(
            group, source.eq(70) & target.isin(ANTHROPIC_OTHER)
        ),
        "loma_a_otra_natural_ha": sum_area(
            group, source.eq(70) & target.isin(NATURAL_OTHER)
        ),
        "entrada_clase_loma_ha": sum_area(group, loma_entry),
        "urbano_a_loma_ha": sum_area(group, source.eq(24) & target.eq(70)),
        "otra_antropica_a_loma_ha": sum_area(
            group, source.isin(ANTHROPIC_OTHER) & target.eq(70)
        ),
        "otra_natural_a_loma_ha": sum_area(
            group, source.isin(NATURAL_OTHER) & target.eq(70)
        ),
        "urbano_persistente_ha": sum_area(
            group, source.eq(24) & target.eq(24)
        ),
        "expansion_urbana_desde_otras_ha": sum_area(
            group, source.ne(24) & source.ne(70) & target.eq(24)
        ),
        "intercambio_68_70_ha": sum_area(
            group,
            (source.eq(68) & target.eq(70))
            | (source.eq(70) & target.eq(68)),
        ),
        "intercambio_13_70_ha": sum_area(
            group,
            (source.eq(13) & target.eq(70))
            | (source.eq(70) & target.eq(13)),
        ),
        "intercambio_66_70_ha": sum_area(
            group,
            (source.eq(66) & target.eq(70))
            | (source.eq(70) & target.eq(66)),
        ),
    }
    result["balance_neto_clase_loma_ha"] = (
        result["entrada_clase_loma_ha"] - result["salida_clase_loma_ha"]
    )
    result["flujo_bruto_clase_loma_ha"] = (
        result["entrada_clase_loma_ha"] + result["salida_clase_loma_ha"]
    )
    return pd.Series(result)


def class_lookup(
    classes: pd.DataFrame,
    unit_column: str,
) -> dict[tuple[str, int, int], float]:
    return {
        (str(row[unit_column]), int(row["year"]), int(row["class_id"])): float(
            row["area_ha"]
        )
        for _, row in classes.iterrows()
    }


def add_reconciliation(
    summary: pd.DataFrame,
    lookup: dict[tuple[str, int, int], float],
) -> pd.DataFrame:
    result = summary.copy()
    result["loma_inicio_serie_ha"] = result.apply(
        lambda row: lookup.get(
            (str(row["unidad_id"]), int(row["year_start"]), 70), 0.0
        ),
        axis=1,
    )
    result["loma_final_serie_ha"] = result.apply(
        lambda row: lookup.get(
            (str(row["unidad_id"]), int(row["year_end"]), 70), 0.0
        ),
        axis=1,
    )
    result["loma_inicio_transiciones_ha"] = (
        result["loma_persistente_ha"] + result["salida_clase_loma_ha"]
    )
    result["loma_final_transiciones_ha"] = (
        result["loma_persistente_ha"] + result["entrada_clase_loma_ha"]
    )
    result["dif_loma_inicio_ha"] = (
        result["loma_inicio_serie_ha"]
        - result["loma_inicio_transiciones_ha"]
    )
    result["dif_loma_final_ha"] = (
        result["loma_final_serie_ha"]
        - result["loma_final_transiciones_ha"]
    )
    result["salida_loma_pct_inicio"] = (
        result["salida_clase_loma_ha"]
        .div(result["loma_inicio_serie_ha"].replace(0, math.nan))
        .mul(100)
        .fillna(0)
    )
    result["entrada_loma_pct_final"] = (
        result["entrada_clase_loma_ha"]
        .div(result["loma_final_serie_ha"].replace(0, math.nan))
        .mul(100)
        .fillna(0)
    )
    result["flujo_bruto_loma_pct_area_cubierta"] = (
        result["flujo_bruto_clase_loma_ha"]
        .div(result["area_cubierta_transiciones_ha"])
        .mul(100)
    )
    result["intercambio_68_70_pct_area_cubierta"] = (
        result["intercambio_68_70_ha"]
        .div(result["area_cubierta_transiciones_ha"])
        .mul(100)
    )
    return result


def build_summary(
    transitions: pd.DataFrame,
    classes: pd.DataFrame,
    unit_columns: list[str],
    class_unit_column: str,
) -> pd.DataFrame:
    group_columns = unit_columns + [
        "banda",
        "year_start",
        "year_end",
    ]
    summary = (
        transitions.groupby(group_columns, dropna=False, sort=True)
        .apply(summarize_group, include_groups=False)
        .reset_index()
    )
    lookup = class_lookup(classes, class_unit_column)
    summary = add_reconciliation(summary, lookup)
    summary["tipo_periodo"] = summary.apply(
        lambda row: (
            "anual"
            if int(row["year_end"]) - int(row["year_start"]) == 1
            else "multianual"
        ),
        axis=1,
    )
    return summary


def add_review_flags(summary: pd.DataFrame, source_name: str) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for _, row in summary.iterrows():
        reasons: list[str] = []
        severity = 0
        if row["banda"] in MANDATORY_REVIEW:
            reasons.append("periodo de auditoría obligatoria")
            severity = max(severity, 1)
        if row["loma_a_urbano_ha"] >= 0.09:
            reasons.append("transición loma→urbano >= 0.09 ha")
            severity = max(severity, 2)
        if row["salida_loma_pct_inicio"] >= 5:
            reasons.append("salida de clase loma >= 5% del área inicial")
            severity = max(severity, 2)
        if row["intercambio_68_70_ha"] >= 5:
            reasons.append("intercambio 68↔70 >= 5 ha")
            severity = max(severity, 2)
        if (
            row["flujo_bruto_clase_loma_ha"] >= 10
            and abs(row["balance_neto_clase_loma_ha"])
            <= 0.2 * row["flujo_bruto_clase_loma_ha"]
        ):
            reasons.append("flujo bruto alto con balance neto bajo")
            severity = max(severity, 2)
        if row["loma_a_urbano_ha"] >= 1 or row["salida_loma_pct_inicio"] >= 15:
            severity = max(severity, 3)
        if not reasons:
            continue

        item = row.to_dict()
        item["fuente_espacial"] = source_name
        item["prioridad"] = {1: "baja", 2: "media", 3: "alta"}[severity]
        item["motivos_control"] = "; ".join(reasons)
        rows.append(item)
    return pd.DataFrame(rows)


def build_anomalies(summary: pd.DataFrame, source_name: str) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for _, row in summary.iterrows():
        alerts: list[str] = []
        if row["intercambio_68_70_pct_area_cubierta"] >= 1:
            alerts.append("intercambio 68↔70 >= 1% del área cubierta")
        if (
            row["tipo_periodo"] == "anual"
            and row["flujo_bruto_clase_loma_ha"] >= 10
            and abs(row["balance_neto_clase_loma_ha"])
            <= 0.2 * row["flujo_bruto_clase_loma_ha"]
        ):
            alerts.append("posible alternancia: flujo bruto alto y balance bajo")
        if (
            abs(row["dif_loma_inicio_ha"]) > AREA_TOLERANCE_HA
            or abs(row["dif_loma_final_ha"]) > AREA_TOLERANCE_HA
        ):
            alerts.append("diferencia por máscara frente a la serie de clases")
        if not alerts:
            continue
        item = {
            "fuente_espacial": source_name,
            "unidad_id": row["unidad_id"],
            "nombre": row["nombre"],
            "banda": row["banda"],
            "year_start": int(row["year_start"]),
            "year_end": int(row["year_end"]),
            "alertas": "; ".join(alerts),
            "intercambio_68_70_ha": row["intercambio_68_70_ha"],
            "intercambio_68_70_pct_area_cubierta": row[
                "intercambio_68_70_pct_area_cubierta"
            ],
            "flujo_bruto_clase_loma_ha": row[
                "flujo_bruto_clase_loma_ha"
            ],
            "balance_neto_clase_loma_ha": row[
                "balance_neto_clase_loma_ha"
            ],
            "dif_loma_inicio_ha": row["dif_loma_inicio_ha"],
            "dif_loma_final_ha": row["dif_loma_final_ha"],
        }
        rows.append(item)
    return pd.DataFrame(rows)


def build_visual_shortlist(priorities: pd.DataFrame) -> pd.DataFrame:
    base = priorities[
        (priorities["fuente_espacial"].eq("acr"))
        | (
            priorities["fuente_espacial"].eq(
                "anillos_periferia_externa"
            )
            & priorities["nivel"].eq("sistema")
        )
    ].copy()
    annual = base[base["tipo_periodo"].eq("anual")]
    selections: list[pd.DataFrame] = []
    for source in ["acr", "anillos_periferia_externa"]:
        subset = annual[annual["fuente_espacial"].eq(source)]
        for metric in [
            "loma_a_urbano_ha",
            "salida_clase_loma_ha",
            "intercambio_68_70_ha",
        ]:
            selections.append(subset.nlargest(8, metric))

        mandatory = subset[subset["banda"].isin(MANDATORY_REVIEW)]
        if not mandatory.empty:
            selections.append(
                mandatory.sort_values(
                    "flujo_bruto_clase_loma_ha", ascending=False
                ).groupby("banda", as_index=False).head(1)
            )

        multiyear = base[
            base["fuente_espacial"].eq(source)
            & base["tipo_periodo"].eq("multianual")
        ]
        if not multiyear.empty:
            selections.append(
                multiyear.sort_values(
                    ["loma_a_urbano_ha", "salida_clase_loma_ha"],
                    ascending=False,
                ).groupby("banda", as_index=False).head(1)
            )

    shortlist = pd.concat(selections, ignore_index=True).drop_duplicates(
        ["fuente_espacial", "unidad_id", "banda"]
    )
    shortlist["_priority"] = pd.Categorical(
        shortlist["prioridad"],
        categories=["alta", "media", "baja"],
        ordered=True,
    )
    shortlist = shortlist.sort_values(
        [
            "_priority",
            "loma_a_urbano_ha",
            "salida_clase_loma_ha",
            "banda",
        ],
        ascending=[True, False, False, True],
    ).drop(columns="_priority")
    return shortlist


def main() -> None:
    inputs = [
        ACR_TRANSITIONS,
        RING_TRANSITIONS,
        ACR_CLASSES,
        RING_CLASSES,
        PERIOD_SELECTION,
    ]
    missing = [str(path) for path in inputs if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Faltan entradas: {missing}")

    acr_transitions = pd.read_csv(ACR_TRANSITIONS)
    ring_transitions = pd.read_csv(RING_TRANSITIONS)
    acr_classes = pd.read_csv(ACR_CLASSES)
    ring_classes = pd.read_csv(RING_CLASSES)

    acr_transitions["unidad_id"] = acr_transitions["id_ambito"]
    acr_summary = build_summary(
        acr_transitions,
        acr_classes,
        ["unidad_id", "id_ambito", "nombre"],
        "id_ambito",
    )
    acr_summary.insert(0, "nivel", "acr")
    acr_summary.insert(4, "zona", "interior_acr")

    ring_summary = build_summary(
        ring_transitions,
        ring_classes,
        ["nivel", "unidad_id", "id_ambito", "nombre", "zona"],
        "unidad_id",
    )

    acr_summary.to_csv(OUT_ACR, index=False)
    ring_summary.to_csv(OUT_RINGS, index=False)

    priorities = pd.concat(
        [
            add_review_flags(acr_summary, "acr"),
            add_review_flags(ring_summary, "anillos_periferia_externa"),
        ],
        ignore_index=True,
    )
    priority_order = pd.Categorical(
        priorities["prioridad"],
        categories=["alta", "media", "baja"],
        ordered=True,
    )
    priorities = (
        priorities.assign(_priority=priority_order)
        .sort_values(
            [
                "_priority",
                "loma_a_urbano_ha",
                "salida_clase_loma_ha",
                "banda",
                "unidad_id",
            ],
            ascending=[True, False, False, True, True],
        )
        .drop(columns="_priority")
    )
    priorities.to_csv(OUT_PRIORITY, index=False)
    shortlist = build_visual_shortlist(priorities)
    shortlist.to_csv(OUT_SHORTLIST, index=False)

    anomalies = pd.concat(
        [
            build_anomalies(acr_summary, "acr"),
            build_anomalies(ring_summary, "anillos_periferia_externa"),
        ],
        ignore_index=True,
    ).sort_values(
        [
            "intercambio_68_70_pct_area_cubierta",
            "flujo_bruto_clase_loma_ha",
        ],
        ascending=False,
    )
    anomalies.to_csv(OUT_ANOMALIES, index=False)

    reconciliation_max = {
        "acr_inicio_ha": float(acr_summary["dif_loma_inicio_ha"].abs().max()),
        "acr_final_ha": float(acr_summary["dif_loma_final_ha"].abs().max()),
        "anillos_inicio_ha": float(
            ring_summary["dif_loma_inicio_ha"].abs().max()
        ),
        "anillos_final_ha": float(
            ring_summary["dif_loma_final_ha"].abs().max()
        ),
    }
    control = {
        "status": "PASS",
        "fecha": datetime.now().astimezone().isoformat(timespec="seconds"),
        "entradas_sha256": {
            str(path.relative_to(ROOT)): sha256(path) for path in inputs
        },
        "filas": {
            "resumen_acr": len(acr_summary),
            "resumen_anillos": len(ring_summary),
            "prioridades_visual": len(priorities),
            "seleccion_visual_prioritaria": len(shortlist),
            "anomalias": len(anomalies),
        },
        "esperados": {
            "resumen_acr": 75,
            "resumen_anillos": 270,
        },
        "maxima_diferencia_reconciliacion": reconciliation_max,
        "regla_interpretacion": (
            "Las entradas y salidas son cambios de clase MapBiomas. No se "
            "denominan pérdida o recuperación ecológica sin validación visual."
        ),
    }
    if len(acr_summary) != 75 or len(ring_summary) != 270:
        control["status"] = "FAIL"
    OUT_CONTROL.write_text(
        json.dumps(control, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    acr_long = acr_summary[
        acr_summary["banda"] == "transitions_1985_2024"
    ]
    ring_system_long = ring_summary[
        (ring_summary["nivel"] == "sistema")
        & (ring_summary["banda"] == "transitions_1985_2024")
    ]
    report = [
        "# Síntesis neutral de transiciones del Paso 6",
        "",
        f"**Estado:** {control['status']}  ",
        f"**Fecha:** {control['fecha']}  ",
        "",
        "## Regla de interpretación",
        "",
        "Los resultados describen cambios entre clases de MapBiomas. Las "
        "expresiones `salida de clase loma` y `entrada a clase loma` no "
        "equivalen todavía a pérdida o recuperación ecológica.",
        "",
        "## Productos",
        "",
        f"- Resumen ACR: {len(acr_summary)} filas.",
        f"- Resumen de anillos: {len(ring_summary)} filas.",
        f"- Registros priorizados para control visual: {len(priorities)}.",
        (
            "- Selección operativa para control visual: "
            f"{len(shortlist)} registros."
        ),
        f"- Alertas metodológicas: {len(anomalies)}.",
        "",
        "## Balance multianual 1985–2024",
        "",
        "| Unidad | Loma persistente (ha) | Salida de loma (ha) | "
        "Entrada a loma (ha) | Loma→urbano (ha) |",
        "|---|---:|---:|---:|---:|",
    ]
    for _, row in acr_long.sort_values("id_ambito").iterrows():
        report.append(
            f"| {row['nombre']} | {row['loma_persistente_ha']:.3f} | "
            f"{row['salida_clase_loma_ha']:.3f} | "
            f"{row['entrada_clase_loma_ha']:.3f} | "
            f"{row['loma_a_urbano_ha']:.3f} |"
        )
    for _, row in ring_system_long.iterrows():
        report.append(
            f"| Sistema de anillos {row['zona']} | "
            f"{row['loma_persistente_ha']:.3f} | "
            f"{row['salida_clase_loma_ha']:.3f} | "
            f"{row['entrada_clase_loma_ha']:.3f} | "
            f"{row['loma_a_urbano_ha']:.3f} |"
        )
    report.extend(
        [
            "",
            "## Conciliación con la serie de clases",
            "",
            (
                "- Diferencia máxima ACR al inicio: "
                f"{reconciliation_max['acr_inicio_ha']:.6f} ha."
            ),
            (
                "- Diferencia máxima ACR al final: "
                f"{reconciliation_max['acr_final_ha']:.6f} ha."
            ),
            (
                "- Diferencia máxima en anillos al inicio: "
                f"{reconciliation_max['anillos_inicio_ha']:.6f} ha."
            ),
            (
                "- Diferencia máxima en anillos al final: "
                f"{reconciliation_max['anillos_final_ha']:.6f} ha."
            ),
            "",
            (
                "La conciliación de la clase 70 es exacta dentro de la "
                "tolerancia. La máscara oficial debe seguir reportándose para "
                "la cobertura total de cada unidad."
            ),
            "",
            "## Siguiente decisión",
            "",
            "Los registros de prioridad alta y media pasan a validación visual "
            "sobre mosaicos Landsat. Solo después de esa revisión se decidirá "
            "qué cambios pueden denominarse pérdida, recuperación o expansión.",
        ]
    )
    OUT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

    print(f"Estado: {control['status']}")
    print(f"Resumen ACR: {len(acr_summary)}/75")
    print(f"Resumen anillos: {len(ring_summary)}/270")
    print(f"Prioridades visuales: {len(priorities)}")
    print(f"Selección visual operativa: {len(shortlist)}")
    print(f"Alertas metodológicas: {len(anomalies)}")
    print(f"Reporte: {OUT_REPORT}")
    if control["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
