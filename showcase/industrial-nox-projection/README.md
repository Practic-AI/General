# Industrial NOx projection (public demo)

**Practic-AI** showcase: estimate unit-level NOx (mg/Nm³) from **absolute humidity** and **ambient temperature**, with one model per unit.

| | |
|---|---|
| **Status** | Public portfolio demo |
| **Data** | **Synthetic only** — no client plant, no SCADA tags, no site IDs |
| **Models** | Random Forest (primary) + linear baseline coefficients in report |
| **Disclaimer** | Estimates ≠ certified CEMS |

Client engagements use the same *pattern* (per-unit models, train/predict CLI, metrics report) on private data that never enters this repository. See [docs/privacy.md](../../docs/privacy.md) and [docs/case-studies.md](../../docs/case-studies.md).

---

## Quick start

```bash
# from this directory
py -3 -m pip install -r requirements.txt
py -3 generate_synthetic_data.py
py -3 train.py
py -3 predict.py --list
py -3 predict.py --unit 1 --humidity 10.5 --temp 18
py -3 predict.py --series examples/series_input.csv --unit all
```

Outputs land in `output/`:

| File | Purpose |
|------|---------|
| `model_bundle.joblib` | Trained models (regenerate; may be gitignored) |
| `metrics_by_unit.csv` | Test R² / RMSE / MAE |
| `metrics.json` | Full metadata + linear coefficients |
| `REPORT.md` | Human-readable summary |
| `projection_nox.csv` | Series prediction result |

---

## Why per-unit models?

Units rarely share the same emission level or response to ambient conditions. A single global model usually predicts worse than **one model per unit** with the same features.

---

## API shape

```text
humidity_abs, temp_ambient  →  nox_unit_k   (mg/Nm³)
```

Linear form (for interpretation):

```text
NOx ≈ a + b1 · humidity_abs + b2 · temp_ambient
```

Random Forest captures mild nonlinear effects; use linear coefficients when you need a transparent equation.

---

## Project layout

```
industrial-nox-projection/
  README.md
  requirements.txt
  generate_synthetic_data.py
  train.py
  predict.py
  data/
    synthetic_units.csv      ← created by generate_*.py
  examples/
    series_input.csv
  output/                    ← created by train / predict
```

---

## What this is *not*

- Not a regulatory compliance system  
- Not trained on any real plant in the public package  
- Not a substitute for continuous emission monitoring  

---

## License

MIT — see repository root `LICENSE`.
