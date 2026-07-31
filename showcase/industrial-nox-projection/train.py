# -*- coding: utf-8 -*-
"""
Train per-unit Random Forest models: humidity + ambient temp → NOx.

Public demo only — trains on synthetic_units.csv (see generate_synthetic_data.py).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "synthetic_units.csv"
OUT = ROOT / "output"

FEATURES = ["humidity_abs", "temp_ambient"]
TEST_SIZE = 0.2
RANDOM_STATE = 42
NOX_MIN = 400.0
NOX_MAX = 2500.0

RF_PARAMS = dict(
    n_estimators=120,
    max_depth=10,
    min_samples_leaf=15,
    n_jobs=-1,
    random_state=RANDOM_STATE,
)


def unit_id(col: str) -> str:
    m = re.search(r"unit[_\s]*(\d+)", col, re.I)
    return f"Unit_{m.group(1)}" if m else col


def load_matrix(path: Path) -> tuple[pd.DataFrame, list[str]]:
    if not path.is_file():
        raise SystemExit(
            f"Missing data file:\n  {path}\n"
            "Run first:  py -3 generate_synthetic_data.py"
        )
    df = pd.read_csv(path)
    df.columns = [str(c).strip() for c in df.columns]
    rename = {}
    for c in df.columns:
        n = c.lower()
        if n in ("humidity_abs", "humedad_absoluta") or (
            "humidity" in n or ("humedad" in n and "abs" in n)
        ):
            rename[c] = "humidity_abs"
        elif n in ("temp_ambient", "temp_ambiente") or (
            "temp" in n and ("ambient" in n or "ambiente" in n)
        ):
            rename[c] = "temp_ambient"
        elif "temp" in n and "ambient" not in rename.values():
            if c not in rename and "nox" not in n:
                pass
    df = df.rename(columns=rename)
    for f in FEATURES:
        if f not in df.columns:
            raise SystemExit(f"Missing column {f}. Found: {list(df.columns)}")
        df[f] = pd.to_numeric(df[f], errors="coerce")
    nox_cols = [c for c in df.columns if re.search(r"nox", c, re.I)]
    for c in nox_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    print(f"Loaded {path.name}: {len(df):,} rows, units={[unit_id(c) for c in nox_cols]}")
    return df, nox_cols


def frame_for_unit(df: pd.DataFrame, nox_col: str) -> pd.DataFrame:
    sub = df[FEATURES + [nox_col]].copy().rename(columns={nox_col: "nox"})
    sub = sub.dropna()
    sub = sub[(sub["nox"] >= NOX_MIN) & (sub["nox"] <= NOX_MAX)]
    sub = sub[sub["humidity_abs"] > 0]
    return sub


def train_pair(sub: pd.DataFrame) -> dict:
    X = sub[FEATURES].to_numpy(dtype=float)
    y = sub["nox"].to_numpy(dtype=float)
    Xtr, Xte, ytr, yte = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
    )

    rf = RandomForestRegressor(**RF_PARAMS)
    rf.fit(Xtr, ytr)
    pred_rf = rf.predict(Xte)

    lin = LinearRegression()
    lin.fit(Xtr, ytr)
    pred_lin = lin.predict(Xte)

    return {
        "rf": rf,
        "linear": lin,
        "r2_rf": float(r2_score(yte, pred_rf)),
        "r2_linear": float(r2_score(yte, pred_lin)),
        "rmse_rf": float(np.sqrt(mean_squared_error(yte, pred_rf))),
        "mae_rf": float(mean_absolute_error(yte, pred_rf)),
        "n_train": int(len(ytr)),
        "n_test": int(len(yte)),
        "coef_humidity": float(lin.coef_[0]),
        "coef_temp": float(lin.coef_[1]),
        "intercept": float(lin.intercept_),
        "feature_importance": {
            FEATURES[i]: float(rf.feature_importances_[i]) for i in range(len(FEATURES))
        },
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    df, nox_cols = load_matrix(DATA)

    metric_rows = []
    rf_models = {}
    linear_models = {}
    meta = {}

    for c in nox_cols:
        uid = unit_id(c)
        sub = frame_for_unit(df, c)
        if len(sub) < 200:
            print(f"  {uid}: too few rows ({len(sub)}), skip")
            continue
        print(f"Training {uid}  n={len(sub):,} ...")
        res = train_pair(sub)
        rf_models[uid] = res["rf"]
        linear_models[uid] = res["linear"]
        meta[uid] = {
            "features": FEATURES,
            "r2_rf_test": res["r2_rf"],
            "r2_linear_test": res["r2_linear"],
            "rmse_rf_test": res["rmse_rf"],
            "mae_rf_test": res["mae_rf"],
            "n_train": res["n_train"],
            "n_test": res["n_test"],
            "feature_importance": res["feature_importance"],
            "linear_equation": {
                "intercept": res["intercept"],
                "coef_humidity": res["coef_humidity"],
                "coef_temp": res["coef_temp"],
            },
            "model_type": "RandomForestRegressor + LinearRegression",
            "rf_params": RF_PARAMS,
            "data": "synthetic_public_demo",
        }
        metric_rows.append(
            {
                "unit": uid,
                "n_train": res["n_train"],
                "n_test": res["n_test"],
                "r2_rf_test": res["r2_rf"],
                "r2_linear_test": res["r2_linear"],
                "rmse_rf_test": res["rmse_rf"],
                "mae_rf_test": res["mae_rf"],
                "imp_humidity": res["feature_importance"]["humidity_abs"],
                "imp_temp": res["feature_importance"]["temp_ambient"],
            }
        )
        print(
            f"  RF R²={res['r2_rf']:.3f}  Linear R²={res['r2_linear']:.3f}  "
            f"RMSE={res['rmse_rf']:.1f}"
        )

    metrics = pd.DataFrame(metric_rows)
    metrics.to_csv(OUT / "metrics_by_unit.csv", index=False)

    bundle = {
        "features": FEATURES,
        "models": meta,
        "sklearn_models": rf_models,
        "linear_models": linear_models,
        "model_family": "random_forest_primary",
        "data_source": "synthetic",
        "disclaimer": (
            "Synthetic demo data only. Not trained on any client plant. "
            "Estimates are not a substitute for certified continuous emission monitoring."
        ),
    }
    joblib.dump(bundle, OUT / "model_bundle.joblib")
    with open(OUT / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False, default=str)

    lines = [
        "# Industrial NOx projection — public demo report",
        "",
        "- **Data:** synthetic multi-unit series (`data/synthetic_units.csv`)",
        f"- **Features:** {', '.join(FEATURES)}",
        "- **Target:** NOx (mg/Nm³) per unit",
        f"- **Split:** train {int((1 - TEST_SIZE) * 100)}% / test {int(TEST_SIZE * 100)}%",
        "",
        "## Disclaimer",
        "",
        "This package uses **synthetic data** for portfolio and training purposes. "
        "It is not linked to any real plant. Projections are estimates, not CEMS replacements.",
        "",
        "## Test metrics",
        "",
        "```",
        metrics.to_string(index=False),
        "```",
        "",
        "## Predict",
        "",
        "```bash",
        "py -3 predict.py --unit 1 --humidity 10.5 --temp 18",
        "py -3 predict.py --unit all --humidity 10 --temp 18",
        "py -3 predict.py --series examples/series_input.csv --unit all",
        "```",
        "",
    ]
    (OUT / "REPORT.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"\nDone. Bundle → {OUT / 'model_bundle.joblib'}")
    print(metrics.to_string(index=False))


if __name__ == "__main__":
    main()
