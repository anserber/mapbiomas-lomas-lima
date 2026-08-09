#!/usr/bin/env python3
"""Clasifica los controles del Paso 6 sin convertirlos en impacto ecológico."""

from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[2]
INPUT = (
    ROOT
    / "05_analisis_temporal"
    / "02_final"
    / "seleccion_controles_visuales_prioritarios_paso06.csv"
)
OUTPUT = (
    ROOT
    / "05_analisis_temporal"
    / "02_final"
    / "tipologia_confianza_controles_paso06.csv"
)
REPORT = (
    ROOT
    / "05_analisis_temporal"
    / "evidencia"
    / "tipologia_confianza_paso06.md"
)
CONTROL = (
    ROOT
    / "05_analisis_temporal"
    / "evidencia"
    / "control_tipologia_confianza_paso06.json"
)


def number(row: dict[str, str], field: str) -> float:
    return float(row[field])


def key(row: dict[str, str]) -> tuple[str, str, int, int]:
    return (
        row["nivel"],
        f'{row["id_ambito"]}|{row["zona"]}',
        int(row["year_start"]),
        int(row["year_end"]),
    )


MANUAL = {
    ("acr", "villa_maria|interior_acr", 2021, 2022): {
        "codigo_tipologia": "TU_PERSISTENTE_MB",
        "tipologia": "Transición urbana persistente según MapBiomas",
        "nivel_evidencia": "media",
        "estado_revision": "revisado",
        "uso_recomendado": "usar_como_resultado_cartografico",
        "requiere_revision_adicional": "sí",
        "impacto_ecologico_confirmado": "no",
        "fuente_decision": "control manual 6E2-B y 6E2-C",
        "justificacion_tipologia": (
            "La transición 70→24 persistió al 100 % hasta 2024; "
            "Dynamic World no corroboró un aumento equivalente de built."
        ),
    },
    ("sistema", "sistema|0_500", 2022, 2023): {
        "codigo_tipologia": "TU_PERSISTENTE_MB",
        "tipologia": "Transición urbana persistente según MapBiomas",
        "nivel_evidencia": "media",
        "estado_revision": "revisado",
        "uso_recomendado": "usar_como_resultado_cartografico",
        "requiere_revision_adicional": "sí",
        "impacto_ecologico_confirmado": "no",
        "fuente_decision": "control manual 6E2-D",
        "justificacion_tipologia": (
            "El 90.947 % permaneció como clase 24 en 2024; "
            "Dynamic World no mostró una señal built equivalente."
        ),
    },
    ("acr", "ancon|interior_acr", 2000, 2001): {
        "codigo_tipologia": "RUPTURA_70_68",
        "tipologia": "Probable ruptura estable entre clases 70 y 68",
        "nivel_evidencia": "media_alta",
        "estado_revision": "revisado",
        "uso_recomendado": "usar_como_limitacion_metodologica",
        "requiere_revision_adicional": "no",
        "impacto_ecologico_confirmado": "no",
        "fuente_decision": "control manual 6E3",
        "justificacion_tipologia": (
            "Las 532.735 ha cambiaron de forma sincrónica y persistieron "
            "como 68, sin una caída equivalente del NDVI."
        ),
    },
    ("acr", "carabayllo_2|interior_acr", 2014, 2015): {
        "codigo_tipologia": "RUPTURA_70_13_68",
        "tipologia": (
            "Ruptura cartográfica estable de clase 70 hacia clases 13 y 68"
        ),
        "nivel_evidencia": "media_alta",
        "estado_revision": "revisado",
        "uso_recomendado": "usar_como_limitacion_metodologica",
        "requiere_revision_adicional": "no",
        "impacto_ecologico_confirmado": "no",
        "fuente_decision": "control manual 6F2",
        "justificacion_tipologia": (
            "Las 10.734 ha permanecieron fuera de la clase 70 hasta 2024, "
            "pero intercambiaron entre las clases naturales 13 y 68. El "
            "NDVI medio solo varió -0.465 % entre 2014 y 2015 y el control "
            "visual no mostró una alteración física equivalente."
        ),
    },
}


def decision_persistente_6f1(porcentaje: float) -> dict[str, str]:
    return {
        "codigo_tipologia": "TU_PERSISTENTE_MB",
        "tipologia": "Transición urbana persistente según MapBiomas",
        "nivel_evidencia": "media",
        "estado_revision": "revisado_persistencia",
        "uso_recomendado": "usar_como_resultado_cartografico",
        "requiere_revision_adicional": "sí",
        "impacto_ecologico_confirmado": "no",
        "fuente_decision": "control de persistencia 6F1",
        "justificacion_tipologia": (
            f"La transición permaneció como clase 24 hasta 2024 "
            f"en {porcentaje:.3f} % del área candidata."
        ),
    }


MANUAL.update(
    {
        ("sistema", "sistema|0_500", 2021, 2022):
            decision_persistente_6f1(100.0),
        ("sistema", "sistema|0_500", 2014, 2015):
            decision_persistente_6f1(100.0),
        ("sistema", "sistema|500_1000", 2021, 2022):
            decision_persistente_6f1(100.0),
        ("acr", "amancaes|interior_acr", 2021, 2022):
            decision_persistente_6f1(100.0),
        ("acr", "amancaes|interior_acr", 2019, 2020):
            decision_persistente_6f1(100.0),
        ("acr", "villa_maria|interior_acr", 2019, 2020):
            decision_persistente_6f1(100.0),
        ("acr", "villa_maria|interior_acr", 2022, 2023): {
            "codigo_tipologia": "TU_PERSISTENCIA_PARCIAL_MB",
            "tipologia": "Transición urbana con persistencia parcial según MapBiomas",
            "nivel_evidencia": "media_baja",
            "estado_revision": "revisado_persistencia",
            "uso_recomendado": "usar_como_resultado_cartografico_con_reserva",
            "requiere_revision_adicional": "sí",
            "impacto_ecologico_confirmado": "no",
            "fuente_decision": "control de persistencia 6F1",
            "justificacion_tipologia": (
                "El 51.746 % permaneció como clase 24 en 2024; "
                "el resto no mantuvo la transición."
            ),
        },
        ("acr", "amancaes|interior_acr", 2022, 2023): {
            "codigo_tipologia": "TU_NO_PERSISTENTE_MB",
            "tipologia": "Transición urbana no persistente según MapBiomas",
            "nivel_evidencia": "baja_para_impacto",
            "estado_revision": "revisado_persistencia",
            "uso_recomendado": "usar_como_alerta_metodologica",
            "requiere_revision_adicional": "no",
            "impacto_ecologico_confirmado": "no",
            "fuente_decision": "control de persistencia 6F1",
            "justificacion_tipologia": (
                "Ningún píxel candidato permaneció como clase 24 en 2024."
            ),
        },
    }
)


def automatic_rule(row: dict[str, str]) -> dict[str, str]:
    start = int(row["year_start"])
    end = int(row["year_end"])
    urban = number(row, "loma_a_urbano_ha")
    exchange = number(row, "intercambio_68_70_ha")
    gross = number(row, "flujo_bruto_clase_loma_ha")
    exchange_ratio = exchange / gross if gross else 0.0

    if row["tipo_periodo"] == "multianual":
        return {
            "codigo_tipologia": "BALANCE_MULTIANUAL",
            "tipologia": "Balance multianual descriptivo",
            "nivel_evidencia": "descriptiva",
            "estado_revision": "clasificado_por_regla",
            "uso_recomendado": "usar_como_tendencia_acumulada",
            "requiere_revision_adicional": "no",
            "impacto_ecologico_confirmado": "no",
            "fuente_decision": "regla 6F",
            "justificacion_tipologia": (
                "Resume diferencias entre dos fechas; no identifica el año "
                "exacto ni la trayectoria intermedia."
            ),
        }

    if end == 2024:
        return {
            "codigo_tipologia": "FINAL_SERIE",
            "tipologia": "Cambio de final de serie sin persistencia posterior",
            "nivel_evidencia": "provisional",
            "estado_revision": "clasificado_por_regla",
            "uso_recomendado": "reportar_como_provisional",
            "requiere_revision_adicional": "sí",
            "impacto_ecologico_confirmado": "no",
            "fuente_decision": "regla 6F",
            "justificacion_tipologia": (
                "El cambio termina en 2024 y la colección no ofrece años "
                "posteriores para comprobar persistencia."
            ),
        }

    if exchange_ratio >= 0.70:
        return {
            "codigo_tipologia": "AMBIGUEDAD_68_70",
            "tipologia": "Cambio dominado por intercambio entre clases 68 y 70",
            "nivel_evidencia": "baja_para_impacto",
            "estado_revision": "clasificado_por_regla",
            "uso_recomendado": "usar_como_alerta_metodologica",
            "requiere_revision_adicional": "sí",
            "impacto_ecologico_confirmado": "no",
            "fuente_decision": "regla 6F",
            "justificacion_tipologia": (
                f"El intercambio 68↔70 representa {exchange_ratio:.1%} "
                "del flujo bruto de clase loma."
            ),
        }

    if urban > 0:
        return {
            "codigo_tipologia": "TU_PENDIENTE",
            "tipologia": "Transición hacia clase urbana pendiente de estabilidad",
            "nivel_evidencia": "pendiente",
            "estado_revision": "clasificado_por_regla",
            "uso_recomendado": "priorizar_control_de_persistencia",
            "requiere_revision_adicional": "sí",
            "impacto_ecologico_confirmado": "no",
            "fuente_decision": "regla 6F",
            "justificacion_tipologia": (
                f"MapBiomas registra {urban:.3f} ha de 70→24; falta "
                "comprobar persistencia y contexto espacial."
            ),
        }

    return {
        "codigo_tipologia": "CAMBIO_NATURAL_PENDIENTE",
        "tipologia": "Cambio entre coberturas naturales pendiente",
        "nivel_evidencia": "pendiente",
        "estado_revision": "clasificado_por_regla",
        "uso_recomendado": "mantener_fuera_de_totales_de_impacto",
        "requiere_revision_adicional": "sí",
        "impacto_ecologico_confirmado": "no",
        "fuente_decision": "regla 6F",
        "justificacion_tipologia": (
            "No existe transición urbana relevante y el cambio requiere "
            "interpretación temática adicional."
        ),
    }


def main() -> None:
    with INPUT.open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source))

    if len(rows) != 45:
        raise RuntimeError(f"Se esperaban 45 controles y se obtuvieron {len(rows)}")

    classified: list[dict[str, str]] = []
    for index, row in enumerate(rows, start=1):
        gross = number(row, "flujo_bruto_clase_loma_ha")
        exchange = number(row, "intercambio_68_70_ha")
        urban = number(row, "loma_a_urbano_ha")
        decision = MANUAL.get(key(row), automatic_rule(row))
        enriched = dict(row)
        enriched.update(
            {
                "id_control": f"CV-{index:03d}",
                "ratio_intercambio_68_70_flujo_bruto": (
                    f"{exchange / gross:.8f}" if gross else "0.00000000"
                ),
                "ratio_loma_urbano_flujo_bruto": (
                    f"{urban / gross:.8f}" if gross else "0.00000000"
                ),
            }
        )
        enriched.update(decision)
        classified.append(enriched)

    fieldnames = list(classified[0])
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(classified)

    type_counts = Counter(row["codigo_tipologia"] for row in classified)
    use_counts = Counter(row["uso_recomendado"] for row in classified)
    reviewed = sum(
        row["estado_revision"].startswith("revisado") for row in classified
    )
    ecological = sum(
        row["impacto_ecologico_confirmado"] == "sí" for row in classified
    )

    timestamp = datetime.now(ZoneInfo("America/Lima")).isoformat(timespec="seconds")
    control = {
        "status": "PASS",
        "timestamp": timestamp,
        "input": str(INPUT.relative_to(ROOT)),
        "output": str(OUTPUT.relative_to(ROOT)),
        "rows": len(classified),
        "manual_reviews": reviewed,
        "ecological_impacts_confirmed": ecological,
        "counts_by_type": dict(sorted(type_counts.items())),
        "counts_by_recommended_use": dict(sorted(use_counts.items())),
        "rules": [
            "manual review overrides automatic rules",
            "multiyear comparisons are descriptive balances",
            "annual changes ending in 2024 are right-censored",
            "68-70 exchange >=70% of gross flow is methodological ambiguity",
            "70-24 changes are separated by their observed persistence",
        ],
    }
    CONTROL.write_text(
        json.dumps(control, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# Tipología de confianza del Paso 6",
        "",
        f"**Estado:** PASS  ",
        f"**Fecha:** {timestamp}  ",
        f"**Controles clasificados:** {len(classified)}  ",
        f"**Controles revisados manualmente:** {reviewed}  ",
        "",
        "## Conteo por tipología",
        "",
        "| Código | Registros |",
        "|---|---:|",
    ]
    lines.extend(f"| {code} | {count} |" for code, count in sorted(type_counts.items()))
    lines.extend(
        [
            "",
            "## Reglas de uso",
            "",
            "- Los balances multianuales describen diferencias acumuladas, no eventos.",
            "- Los cambios que terminan en 2024 son provisionales por censura derecha.",
            "- El intercambio dominante 68↔70 no se suma como pérdida ecológica.",
            "- La transición 70→24 se denomina transición hacia infraestructura urbana según MapBiomas.",
            "- Ningún control se declara automáticamente impacto ecológico confirmado.",
            "",
            "## Controles manuales que anclan la tipología",
            "",
            "- Villa María 2021–2022: transición urbana MapBiomas persistente al 100 %.",
            "- Sistema 0–500 m 2022–2023: transición urbana MapBiomas persistente al 90.947 %.",
            "- Ancón 2000–2001: probable ruptura estable entre clases 70 y 68.",
            "- Carabayllo 2 2014–2015: ruptura estable de clase 70 hacia clases 13 y 68, sin descenso equivalente del NDVI.",
            "- 6F1 revisó conjuntamente otras ocho transiciones urbanas.",
            "- Seis persistieron al 100 %, una al 51.746 % y una al 0 %.",
            "",
            "## Producto",
            "",
            f"`{OUTPUT.relative_to(ROOT)}`",
            "",
        ]
    )
    REPORT.write_text("\n".join(lines), encoding="utf-8")

    print("PASS")
    print(f"rows={len(classified)}")
    print(f"manual_reviews={reviewed}")
    print(f"ecological_impacts_confirmed={ecological}")
    print("counts_by_type=" + json.dumps(dict(sorted(type_counts.items())), ensure_ascii=False))


if __name__ == "__main__":
    main()
