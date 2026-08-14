#!/usr/bin/env python3
"""Emit the compact JSON the hangar explorer reads. No owner PII."""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "processed" / "cirrus_us_fleet.csv"
OUT_JSON = Path(__file__).resolve().parent / "fleet.json"
OUT_JS = Path(__file__).resolve().parent / "fleet-data.js"

REG = {
    "1": "Individual",
    "2": "Partnership",
    "3": "Corporation",
    "4": "Co-owned",
    "5": "Government",
    "7": "LLC",
    "8": "Non-citizen corp",
    "9": "Non-citizen co-owned",
}
STATUS = {
    "V": "Valid",
    "M": "Factory / dealer",
    "R": "Pending",
    "N": "Non-citizen report missing",
    "7": "Sale reported",
}


def main() -> None:
    rows = []
    with SRC.open(encoding="utf-8", newline="") as f:
        for raw in csv.DictReader(f):
            year = raw.get("year_mfr") or None
            if year:
                year = int(year)
            rows.append(
                {
                    "n": raw["n_number"],
                    "m": raw["model"],
                    "y": year,
                    "s": raw.get("state") or "",
                    "st": raw.get("status_code") or "",
                    "r": REG.get(raw.get("type_registrant") or "", "Other"),
                }
            )
    blob = json.dumps(rows, separators=(",", ":"))
    OUT_JSON.write_text(blob, encoding="utf-8")
    OUT_JS.write_text("window.FLEET = " + blob + ";\n", encoding="utf-8")
    print(f"wrote {len(rows):,} rows → {OUT_JS.name} ({OUT_JS.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
