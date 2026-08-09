#!/usr/bin/env python3
"""Prepara las entradas ciegas para los visores del Paso 8D.

No consulta ni modifica la clave de repeticiones. Las coordenadas KBA solo se
mantienen en la carpeta restringida.
"""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path("/Users/administrador/Documents/MAPBIOMAS")
SOURCE = (
    ROOT
    / "06_validacion_visual/kba_restricted/"
    "instrumento_evaluacion_visual_ciego_paso08.csv"
)
PUBLIC_OUT = (
    ROOT
    / "06_validacion_visual/01_intermediate/paso08D_visores/"
    "puntos_publicos_ciegos_paso08.csv"
)
KBA_CSV_OUT = (
    ROOT
    / "06_validacion_visual/kba_restricted/"
    "puntos_evaluacion_ciegos_kba_paso08.csv"
)

VIEWER_FIELDS = [
    "id_muestra",
    "dominio",
    "unidad_id",
    "nombre_unidad",
    "estrato",
    "year_start",
    "year_evento",
    "year_end_observado",
    "longitude",
    "latitude",
]


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=VIEWER_FIELDS)
        writer.writeheader()
        writer.writerows({field: row[field] for field in VIEWER_FIELDS} for row in rows)


def main() -> None:
    with SOURCE.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 66, f"Se esperaban 66 evaluaciones; se encontraron {len(rows)}"
    ids = [row["id_muestra"] for row in rows]
    assert len(ids) == len(set(ids)), "Hay id_muestra duplicados"
    assert all(row["longitude"] and row["latitude"] for row in rows)

    public_rows = [row for row in rows if row["dominio"] != "kba_restricted"]
    kba_rows = [row for row in rows if row["dominio"] == "kba_restricted"]

    assert len(public_rows) == 39, len(public_rows)
    assert len(kba_rows) == 27, len(kba_rows)
    assert Counter(row["estrato"] for row in rows).keys() == {
        "E1_PERSISTENTE70",
        "E2_URBANO_W5",
        "E3_URBANO_CENSURADO",
        "E4_INTERCAMBIO_68_70",
        "E5_RECUPERACION_68_70",
        "E6_CAMBIO_70_13",
    }

    write_rows(PUBLIC_OUT, public_rows)
    write_rows(KBA_CSV_OUT, kba_rows)

    print(f"PASS: {len(public_rows)} evaluaciones públicas -> {PUBLIC_OUT}")
    print(f"PASS: {len(kba_rows)} evaluaciones KBA restringidas -> {KBA_CSV_OUT}")
    print("La clave de repeticiones no fue consultada.")


if __name__ == "__main__":
    main()
