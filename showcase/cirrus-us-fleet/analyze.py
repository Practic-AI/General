#!/usr/bin/env python3
"""Run DuckDB SQL over the PII-stripped Cirrus extract and write charts + a dashboard."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent
FLEET = ROOT / "data" / "processed" / "cirrus_us_fleet.csv"
LOOKUPS = ROOT / "data" / "lookups"
OUT = ROOT / "output"
CHARTS = OUT / "charts"
SQL_FILE = ROOT / "sql" / "fleet_kpis.sql"
NAVY = "#1B365D"
GOLD = "#C4A35A"
INK = "#2C2C2C"
MUTED = "#6B7280"
GRID = "#E5E7EB"

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "axes.facecolor": "white",
        "figure.facecolor": "white",
        "axes.edgecolor": GRID,
        "axes.labelcolor": INK,
        "xtick.color": INK,
        "ytick.color": INK,
        "text.color": INK,
        "axes.titlesize": 12,
        "axes.titleweight": "bold",
    }
)


def connect() -> duckdb.DuckDBPyConnection:
    if not FLEET.exists():
        raise SystemExit("Missing processed extract. Run: py -3 ingest.py")
    con = duckdb.connect(database=":memory:")
    con.execute(
        f"CREATE TABLE fleet AS SELECT * FROM read_csv_auto('{FLEET.as_posix()}', header=true, nullstr='');"
    )
    con.execute(
        f"CREATE TABLE status AS SELECT * FROM read_csv_auto('{(LOOKUPS / 'status_codes.csv').as_posix()}', header=true);"
    )
    con.execute(
        f"CREATE TABLE registrant AS SELECT * FROM read_csv_auto('{(LOOKUPS / 'registrant_types.csv').as_posix()}', header=true);"
    )
    con.execute(
        f"CREATE TABLE engines AS SELECT * FROM read_csv_auto('{(LOOKUPS / 'engine_types.csv').as_posix()}', header=true);"
    )
    con.execute(
        f"CREATE TABLE regions AS SELECT * FROM read_csv_auto('{(LOOKUPS / 'regions.csv').as_posix()}', header=true);"
    )
    return con


def statements() -> list[str]:
    text = SQL_FILE.read_text(encoding="utf-8")
    chunks: list[str] = []
    buf: list[str] = []
    for line in text.splitlines():
        if line.strip().startswith("--") and not buf:
            continue
        buf.append(line)
        if line.strip().endswith(";"):
            stmt = "\n".join(buf).strip()
            if stmt:
                chunks.append(stmt)
            buf = []
    return chunks


def run_sql(con: duckdb.DuckDBPyConnection) -> list[pd.DataFrame]:
    year = datetime.now().year
    frames = []
    for stmt in statements():
        sql = stmt.replace("$snapshot_year", str(year))
        frames.append(con.execute(sql).df())
    return frames


def save_table(df: pd.DataFrame, name: str) -> None:
    path = OUT / name
    df.to_csv(path, index=False)
    print(f"  {path.name:28s} {len(df):5d} rows")


def barh(ax, labels, values, color=NAVY) -> None:
    ax.barh(labels[::-1], values[::-1], color=color, height=0.7)
    ax.set_axisbelow(True)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)


def chart_mix(by_model: pd.DataFrame) -> Path:
    plot = by_model[by_model["n"] >= 10]
    fig, ax = plt.subplots(figsize=(8, 3.6))
    barh(ax, plot["model"].tolist(), plot["n"].tolist())
    ax.set_title("US-registered Cirrus airframes by model")
    ax.set_xlabel("Airframes on the FAA register")
    fig.tight_layout()
    path = CHARTS / "by_model.png"
    fig.savefig(path, dpi=140)
    plt.close(fig)
    return path


def chart_year(by_year: pd.DataFrame) -> Path:
    fig, ax = plt.subplots(figsize=(9, 3.8))
    ax.stackplot(
        by_year["year_mfr"],
        by_year["sr20"],
        by_year["sr22"],
        by_year["sr22t"],
        by_year["sf50"],
        labels=["SR20", "SR22", "SR22T", "SF50"],
        colors=["#93A4BD", NAVY, "#3F6FA6", GOLD],
        alpha=0.95,
    )
    ax.legend(loc="upper left", frameon=False, ncol=4)
    ax.set_title("Surviving US registry by year of manufacture (not factory deliveries)")
    ax.set_xlabel("Year manufactured")
    ax.set_ylabel("Airframes still registered")
    ax.set_axisbelow(True)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    path = CHARTS / "by_year.png"
    fig.savefig(path, dpi=140)
    plt.close(fig)
    return path


def chart_state(by_state: pd.DataFrame) -> Path:
    top = by_state.head(12)
    fig, ax = plt.subplots(figsize=(8, 4.2))
    barh(ax, top["state"].tolist(), top["n"].tolist())
    ax.set_title("Registration state (legal domicile — DE/WY are often paper homes)")
    ax.set_xlabel("Airframes")
    fig.tight_layout()
    path = CHARTS / "by_state.png"
    fig.savefig(path, dpi=140)
    plt.close(fig)
    return path


def chart_registrant(by_reg: pd.DataFrame) -> Path:
    fig, ax = plt.subplots(figsize=(8, 3.2))
    barh(ax, by_reg["registrant"].tolist(), by_reg["n"].tolist(), color="#3F6FA6")
    ax.set_title("Who holds the registration")
    ax.set_xlabel("Airframes")
    fig.tight_layout()
    path = CHARTS / "by_registrant.png"
    fig.savefig(path, dpi=140)
    plt.close(fig)
    return path


def write_report(kpis: pd.DataFrame, by_model: pd.DataFrame, by_reg: pd.DataFrame, age: pd.DataFrame, meta: dict) -> Path:
    k = kpis.iloc[0]
    llc = by_reg.loc[by_reg["registrant"].str.contains("LLC", na=False)]
    llc_pct = float(llc["pct"].iloc[0]) if len(llc) else 0
    lines = [
        "# Cirrus US fleet snapshot",
        "",
        f"- Source: FAA Releasable Aircraft Database, extracted {meta.get('extracted_at_utc', 'unknown')}.",
        "- Not affiliated with Cirrus Aircraft. Public registry data only. Owner names and addresses stripped.",
        "",
        "## Headlines",
        "",
        f"- **{int(k['registered_airframes']):,}** Cirrus airframes currently on the US register.",
        f"- **{int(k['production_models']):,}** are production models (SR20 / SR22 / SR22T / SF50).",
        f"- **{int(k['valid_registration']):,}** have a valid registration (`V`); **{int(k['manufacturer_held']):,}** sit on a manufacturer dealer certificate (`M`, almost all Minnesota).",
        f"- **{k['pct_missing_year']}%** of rows have no usable manufacture year — a real data-quality issue, not a rounding error.",
        f"- Median age of airframes with a year: **{age.iloc[0]['median_age_years']} years**.",
        f"- Registrations are LLC-heavy (**{llc_pct:.1f}%**).",
        "",
        "## How to read this",
        "",
        "The FAA file is **who holds a US N-number today**, not Cirrus factory shipments.",
        "A 2024 SR22 delivered to Europe never appears. A 2006 SR22 still flying in Florida does.",
        "Delaware and Wyoming rank high because of how aircraft are titled, not because everyone flies there.",
        "",
        "## Model mix",
        "",
        "| Model | n | % |",
        "|---|---:|---:|",
    ]
    for _, row in by_model.iterrows():
        lines.append(f"| {row['model']} | {int(row['n']):,} | {row['pct_of_us_registry']} |")
    lines += [
        "",
        "## Talking points (for a screen-share)",
        "",
        "1. Registry ≠ deliveries. Compare this file to Cirrus/GAMA shipment numbers and the gap is exports + write-offs + foreign registers.",
        "2. Factory inventory is visible: status `M` clusters in Minnesota.",
        "3. Ownership is mostly LLCs — a liability/tax pattern, not a flying pattern.",
        "4. Always publish the missing-year rate. 8% blank is material if someone uses vintage for residual values.",
        "",
    ]
    path = OUT / "REPORT.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_dashboard(kpis: pd.DataFrame, by_model: pd.DataFrame, age: pd.DataFrame, meta: dict) -> Path:
    k = kpis.iloc[0]
    extracted = meta.get("extracted_at_utc", "")
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Cirrus US fleet snapshot — Practic-AI</title>
  <style>
    :root {{ --navy:#1B365D; --gold:#C4A35A; --ink:#1f2937; --muted:#6b7280; --bg:#f6f7f9; }}
    body {{ margin:0; font-family: Calibri, Segoe UI, sans-serif; color:var(--ink); background:var(--bg); }}
    header {{ background:var(--navy); color:#fff; padding:28px 24px 22px; }}
    header p {{ margin:6px 0 0; color:#d5dde8; max-width:720px; }}
    main {{ max-width:980px; margin:0 auto; padding:24px; }}
    .kpis {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(160px,1fr)); gap:12px; margin:18px 0 28px; }}
    .kpi {{ background:#fff; border:1px solid #e5e7eb; padding:14px 16px; }}
    .kpi b {{ display:block; font-size:26px; color:var(--navy); }}
    .kpi span {{ color:var(--muted); font-size:13px; }}
    figure {{ background:#fff; border:1px solid #e5e7eb; padding:12px 12px 6px; margin:0 0 18px; }}
    figure img {{ width:100%; height:auto; display:block; }}
    figcaption {{ color:var(--muted); font-size:12px; padding:6px 4px 8px; }}
    .note {{ font-size:14px; color:var(--muted); line-height:1.45; }}
    footer {{ padding:20px 24px 40px; color:var(--muted); font-size:13px; max-width:980px; margin:0 auto; }}
  </style>
</head>
<body>
  <header>
    <h1>Cirrus US fleet snapshot</h1>
    <p>FAA Releasable Aircraft Database. Public data. Owner names and addresses stripped. Not affiliated with Cirrus Aircraft.</p>
  </header>
  <main>
    <div class="kpis">
      <div class="kpi"><b>{int(k['registered_airframes']):,}</b><span>US-registered Cirrus airframes</span></div>
      <div class="kpi"><b>{int(k['valid_registration']):,}</b><span>Valid registrations (V)</span></div>
      <div class="kpi"><b>{int(k['manufacturer_held']):,}</b><span>On manufacturer dealer cert (M)</span></div>
      <div class="kpi"><b>{age.iloc[0]['median_age_years']}</b><span>Median age (years, known vintage)</span></div>
      <div class="kpi"><b>{k['pct_missing_year']}%</b><span>Rows missing manufacture year</span></div>
    </div>
    <figure>
      <img src="output/charts/by_model.png" alt="Airframes by model" />
      <figcaption>Production mix on the US register. SR22 / SR22T dominate.</figcaption>
    </figure>
    <figure>
      <img src="output/charts/by_year.png" alt="Vintage stack" />
      <figcaption>This is surviving US registry by year built — not GAMA deliveries. 2026 is a partial year.</figcaption>
    </figure>
    <figure>
      <img src="output/charts/by_state.png" alt="Registration state" />
      <figcaption>Florida / California / Texas are flying markets. Delaware and Wyoming are often where the LLC lives.</figcaption>
    </figure>
    <figure>
      <img src="output/charts/by_registrant.png" alt="Registrant type" />
      <figcaption>Most Cirrus airframes are held by an LLC, not an individual name.</figcaption>
    </figure>
    <p class="note">Extracted {extracted}. SQL lives in <code>sql/fleet_kpis.sql</code>. Refresh with <code>py -3 ingest.py</code> then <code>py -3 analyze.py</code>.</p>
  </main>
  <footer>
    Practic-AI public showcase. Source: <a href="https://registry.faa.gov/database/ReleasableAircraft.zip">registry.faa.gov</a>.
    Do not treat this as official Cirrus fleet reporting.
  </footer>
</body>
</html>
"""
    path = ROOT / "dashboard.html"
    path.write_text(html, encoding="utf-8")
    return path


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    CHARTS.mkdir(parents=True, exist_ok=True)
    meta_path = ROOT / "data" / "processed" / "snapshot_meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}

    con = connect()
    frames = run_sql(con)
    kpis, by_model, by_year, by_state, by_reg, by_status, age, jet_share = frames

    print("writing tables")
    save_table(kpis, "kpis.csv")
    save_table(by_model, "by_model.csv")
    save_table(by_year, "by_year.csv")
    save_table(by_state, "by_state.csv")
    save_table(by_reg, "by_registrant.csv")
    save_table(by_status, "by_status.csv")
    save_table(age, "age.csv")
    save_table(jet_share, "sf50_share_by_year.csv")

    print("writing charts")
    chart_mix(by_model)
    chart_year(by_year)
    chart_state(by_state)
    chart_registrant(by_reg)

    write_report(kpis, by_model, by_reg, age, meta)
    dash = write_dashboard(kpis, by_model, age, meta)
    (OUT / "kpis.json").write_text(
        json.dumps(
            {
                **kpis.iloc[0].to_dict(),
                **{f"age_{c}": age.iloc[0][c] for c in age.columns},
                "extracted_at_utc": meta.get("extracted_at_utc"),
                "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )
    print(f"dashboard → {dash}")


if __name__ == "__main__":
    main()
