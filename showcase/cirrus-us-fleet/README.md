# Cirrus US fleet snapshot

Public FAA aircraft-registry analysis. **Not affiliated with Cirrus Aircraft.**

| | |
|---|---|
| **Status** | Public portfolio demo |
| **Data** | [FAA Releasable Aircraft Database](https://registry.faa.gov/database/ReleasableAircraft.zip) |
| **Question** | What does the *US-registered* Cirrus fleet look like right now? |
| **Stack** | Python ingest → DuckDB SQL → charts + static dashboard |

This is a **registry snapshot**, not factory deliveries. An SR22 delivered to Europe never appears. A 2006 SR22 still on a US N-number does. Delaware and Wyoming rank high because of how airplanes are titled, not because everyone flies there.

Owner **name, street, city, ZIP, county** are dropped in ingest and never written to `data/processed/`.

---

## Quick start

```bash
cd showcase/cirrus-us-fleet
py -3 -m pip install -r requirements.txt
py -3 ingest.py          # download FAA zip (cached under _raw/) and write the PII-stripped extract
py -3 analyze.py         # DuckDB SQL → output/ + dashboard.html
```

Then open `dashboard.html`.

If `data/processed/cirrus_us_fleet.csv` is already in the clone, you can skip ingest and just run `analyze.py`.

---

## What it shows

- Model mix (SR20 / SR22 / SR22T / SF50 Vision Jet)
- Surviving US registry by year of manufacture (with a running total)
- Registration state, including factory-held `M` certificates (almost all Minnesota)
- Registrant type (the file is LLC-heavy)
- Data-quality rate: share of rows with no usable `year_mfr`
- Median age of airframes that have a year

SQL for every number is in [`sql/fleet_kpis.sql`](sql/fleet_kpis.sql) — joins, `FILTER`, window shares, running totals.

---

## Layout

```
cirrus-us-fleet/
  ingest.py                 download + PII strip
  analyze.py                DuckDB + charts + dashboard
  sql/fleet_kpis.sql        the analysis
  data/lookups/             FAA code labels
  data/processed/           committed extract (no owner PII)
  output/                   tables, REPORT.md, charts
  dashboard.html
  _raw/                     gitignored FAA zip + MASTER.txt
```

---

## What this is *not*

- Not Cirrus internal data, GAMA official shipments, or ADS-B flying hours
- Not a safety study and not an accident database
- Not a claim that the author works at Cirrus
- Not worldwide fleet (US N-numbers only)

Cirrus public delivery figures (for example 691 SR Series + 106 Vision Jets in 2025, 11,000 lifetime SR Series) live in their press room. Use those to talk about **the gap** between shipments and this register. Do not paste them into the SQL as if they came from the FAA file.

---

## Privacy

See [docs/privacy.md](../../docs/privacy.md). Raw `MASTER.txt` stays in `_raw/` (gitignored). The processed CSV has tail number, serial, model, year, state, and registration codes only.
