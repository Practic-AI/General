# -*- coding: utf-8 -*-
"""
Generate synthetic multi-unit process data for the public NOx demo.

No client plant data is used. Relationships are invented so models train
meaningfully while remaining unattributable to any real site.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
OUT_CSV = ROOT / "data" / "synthetic_units.csv"
N_ROWS = 12_000
N_UNITS = 6
SEED = 42

# Per-unit coefficients (humidity tends to dominate; unit 4 is temp-heavy)
UNIT_PARAMS = {
    1: dict(base=980, b_h=-28.0, b_t=4.5, noise=35),
    2: dict(base=1050, b_h=-32.0, b_t=3.0, noise=40),
    3: dict(base=920, b_h=-24.0, b_t=5.5, noise=42),
    4: dict(base=1100, b_h=-8.0, b_t=18.0, noise=30),
    5: dict(base=1000, b_h=-30.0, b_t=4.0, noise=38),
    6: dict(base=960, b_h=-27.0, b_t=6.0, noise=33),
}


def main() -> None:
    rng = np.random.default_rng(SEED)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    # Seasonal-ish humidity and temperature (Southern Hemisphere–ish range, generic)
    t = np.arange(N_ROWS)
    humidity = (
        9.0
        + 3.5 * np.sin(2 * np.pi * t / (24 * 30))
        + 1.2 * np.sin(2 * np.pi * t / 24)
        + rng.normal(0, 0.8, N_ROWS)
    )
    humidity = np.clip(humidity, 2.0, 18.0)

    temp = (
        18.0
        + 6.0 * np.sin(2 * np.pi * t / (24 * 30) + 1.2)
        + 2.0 * np.sin(2 * np.pi * t / 24)
        + rng.normal(0, 1.2, N_ROWS)
    )
    temp = np.clip(temp, 5.0, 35.0)

    timestamps = pd.date_range("2024-01-01", periods=N_ROWS, freq="h")
    frame: dict[str, object] = {
        "timestamp": timestamps,
        "humidity_abs": np.round(humidity, 3),
        "temp_ambient": np.round(temp, 3),
    }

    for u, p in UNIT_PARAMS.items():
        # Mild nonlinearity so RF beats a pure linear fit slightly
        nox = (
            p["base"]
            + p["b_h"] * humidity
            + p["b_t"] * temp
            + 0.35 * p["b_h"] * np.maximum(humidity - 10, 0) ** 1.3
            + rng.normal(0, p["noise"], N_ROWS)
        )
        # Occasional downtime → missing target
        mask_down = rng.random(N_ROWS) < 0.04
        nox = np.where(mask_down, np.nan, nox)
        nox = np.clip(nox, 400, 2500)
        frame[f"nox_unit_{u}"] = np.round(nox, 2)

    df = pd.DataFrame(frame)
    df.to_csv(OUT_CSV, index=False)
    print(f"Wrote {len(df):,} rows × {N_UNITS} units → {OUT_CSV}")
    print(f"Columns: {list(df.columns)}")


if __name__ == "__main__":
    main()
