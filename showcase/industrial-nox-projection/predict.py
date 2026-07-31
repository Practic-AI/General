# -*- coding: utf-8 -*-
"""
Project NOx from humidity + ambient temperature (per unit).

Modes:
  A) Single point:
       py -3 predict.py --unit 1 --humidity 10.5 --temp 18
       py -3 predict.py --unit all --humidity 10 --temp 18

  B) Series (CSV):
       py -3 predict.py --series examples/series_input.csv --unit all

  C) List models:
       py -3 predict.py --list
"""
from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output"
MODEL_PATH = OUT / "model_bundle.joblib"


def load_bundle():
    if not MODEL_PATH.is_file():
        raise SystemExit(
            f"No model at:\n  {MODEL_PATH}\n"
            "Run:  py -3 generate_synthetic_data.py  &&  py -3 train.py"
        )
    return joblib.load(MODEL_PATH)


def resolve_unit(models, key: str) -> str:
    if key in models:
        return key
    alt = f"Unit_{key}" if not str(key).lower().startswith("unit") else key
    # normalize Unit_1 vs unit_1
    for k in models:
        if k.lower() == alt.lower() or k.lower() == f"unit_{key}".lower():
            return k
    raise SystemExit(f"Unknown unit: {key}. Available: {list(models)}")


def units_to_run(bundle, unit_arg: str) -> list[str]:
    keys = list(bundle["sklearn_models"].keys())
    if str(unit_arg).lower() == "all":
        return keys
    return [resolve_unit(bundle["sklearn_models"], unit_arg)]


def predict_matrix(bundle, unit_keys: list[str], H: np.ndarray, T: np.ndarray) -> pd.DataFrame:
    X = np.column_stack([H.astype(float), T.astype(float)])
    out = {}
    for uid in unit_keys:
        model = bundle["sklearn_models"][uid]
        out[f"nox_pred_{uid}"] = model.predict(X)
    return pd.DataFrame(out)


def find_col(columns, *needle_groups):
    for c in columns:
        n = str(c).strip().lower()
        for needles in needle_groups:
            if all(nd in n for nd in needles):
                return c
    return None


def load_series(path: Path) -> pd.DataFrame:
    path = Path(path)
    if not path.is_file():
        raise SystemExit(f"Series file not found: {path}")
    if path.suffix.lower() in (".xlsx", ".xlsm"):
        df = pd.read_excel(path)
    else:
        try:
            df = pd.read_csv(path)
        except Exception:
            df = pd.read_csv(path, sep=";")
    df.columns = [str(c).strip() for c in df.columns]

    hcol = find_col(
        df.columns,
        ("humidity",),
        ("humedad",),
        ("h_abs",),
    )
    tcol = find_col(
        df.columns,
        ("temp", "ambient"),
        ("temp", "ambiente"),
        ("temperature",),
        ("temp",),
    )
    if hcol is None or tcol is None:
        raise SystemExit(
            "Series file needs humidity and temperature columns.\n"
            f"Found: {list(df.columns)}\n"
            "Examples: humidity_abs, temp_ambient"
        )

    out = pd.DataFrame()
    dcol = find_col(df.columns, ("timestamp",), ("fecha",), ("date",), ("time",))
    if dcol:
        out["timestamp"] = df[dcol]
    out["humidity_abs"] = pd.to_numeric(df[hcol], errors="coerce")
    out["temp_ambient"] = pd.to_numeric(df[tcol], errors="coerce")
    n_before = len(out)
    out = out.dropna(subset=["humidity_abs", "temp_ambient"]).reset_index(drop=True)
    if len(out) == 0:
        raise SystemExit("No valid rows (numeric humidity/temperature).")
    if len(out) < n_before:
        print(f"Note: dropped {n_before - len(out)} incomplete rows.")
    return out


def main() -> None:
    p = argparse.ArgumentParser(description="Project NOx (Random Forest per unit) — Practic-AI demo")
    p.add_argument("--unit", type=str, default="all", help="Unit number or 'all'")
    p.add_argument("--humidity", type=float, default=None, help="Absolute humidity (single point)")
    p.add_argument("--temp", type=float, default=None, help="Ambient temperature °C (single point)")
    p.add_argument("--series", type=str, default=None, help="CSV/Excel with humidity + temp series")
    p.add_argument("--out", type=str, default=None, help="Output CSV path")
    p.add_argument("--list", action="store_true", help="List units and metrics")
    args = p.parse_args()

    bundle = load_bundle()
    meta = bundle["models"]

    if args.list:
        print("Trained units (Random Forest, synthetic demo):")
        for k, v in meta.items():
            print(
                f"  {k}: R² test={v['r2_rf_test']:.3f}  "
                f"RMSE={v['rmse_rf_test']:.1f}  n_train={v['n_train']}"
            )
        print(f"\nFeatures: {bundle['features']}")
        print(f"Data: {bundle.get('data_source', 'unknown')}")
        if "disclaimer" in bundle:
            print(f"\n{bundle['disclaimer']}")
        return

    unit_keys = units_to_run(bundle, args.unit)

    if args.series:
        serie = load_series(Path(args.series))
        pred = predict_matrix(
            bundle,
            unit_keys,
            serie["humidity_abs"].to_numpy(),
            serie["temp_ambient"].to_numpy(),
        )
        result = pd.concat([serie.reset_index(drop=True), pred], axis=1)
        out_path = Path(args.out) if args.out else OUT / "projection_nox.csv"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        result.to_csv(out_path, index=False)
        print(f"Series: {len(result)} rows | Units: {', '.join(unit_keys)}")
        print(f"Saved: {out_path.resolve()}")
        print("\nPreview:")
        print(result.head(8).to_string(index=False))
        return

    if args.humidity is None or args.temp is None:
        raise SystemExit(
            "Provide --humidity and --temp  OR  --series file.csv\n"
            "Examples:\n"
            "  py -3 predict.py --unit 1 --humidity 10.5 --temp 18\n"
            "  py -3 predict.py --series examples/series_input.csv --unit all"
        )

    print(f"Input: humidity_abs={args.humidity}  temp_ambient={args.temp} °C")
    print("-" * 50)
    H = np.array([args.humidity], dtype=float)
    T = np.array([args.temp], dtype=float)
    pred = predict_matrix(bundle, unit_keys, H, T)
    for uid in unit_keys:
        yhat = float(pred[f"nox_pred_{uid}"].iloc[0])
        r2 = meta.get(uid, {}).get("r2_rf_test", float("nan"))
        print(f"  {uid}: NOx ≈ {yhat:.1f} mg/Nm³   (R² test={r2:.3f})")
    print("\nEstimate only — synthetic demo model; not a CEMS substitute.")


if __name__ == "__main__":
    main()
