# Case studies (portfolio)

Public summaries only. Client identities withheld unless written permission exists.

---

## 1. Industrial NOx projection (confidential energy / industrial client)

**Problem**  
Operations needed a way to **estimate unit-level NOx** from ambient conditions (absolute humidity + ambient temperature) for analysis and projection — without treating the estimate as a CEMS replacement.

**What we delivered**

- Per-unit models (units behave differently; one global model underperforms)
- **Linear** package for transparent coefficients (paper / explanation)
- **Random Forest** package for stronger series projection
- Train + predict CLIs, metrics tables, operator-facing `LEE_PRIMERO`-style guides
- Correlation heatmaps and ranking of drivers

**Method (public)**  
Features: absolute humidity, ambient temperature → target: NOx (mg/Nm³).  
Train/test split 80/20. One model per unit.

**Illustrative quality (real engagement; exact site confidential)**  
On held-out real operational data, Random Forest test R² was typically in the **~0.87–0.96** range depending on unit. Public demo metrics will differ because they use **synthetic** data — see the showcase README after you run `train.py`.

**Stack**  
Python, pandas, scikit-learn, joblib, CSV/Excel I/O.

**Public demo**  
[`showcase/industrial-nox-projection/`](../showcase/industrial-nox-projection/)

---

## 2. Cirrus US fleet snapshot (public FAA registry)

**Problem**  
A business analyst interviewing into personal aviation should be able to describe the **US-registered** Cirrus fleet from public data — without pretending to have internal Cirrus tables, and without publishing owner names.

**What we delivered**

- Ingest of the FAA Releasable Aircraft Database, filtered to Cirrus make/model codes
- PII strip (name, street, city, ZIP, county dropped before write)
- DuckDB SQL: model mix, vintage, state, registrant type, factory-held `M` certificates, missing-year QC
- Static dashboard + `REPORT.md`

**Method (public)**  
Registry snapshot ≠ factory deliveries. `year_mfr` is the manufacture year of airframes still on a US N-number. Delaware/Wyoming ranks are legal domicile, not flight activity.

**Stack**  
Python, DuckDB, pandas, matplotlib.

**Public demo**  
[`showcase/cirrus-us-fleet/`](../showcase/cirrus-us-fleet/)

---

## 3. Legal AI reasoning evaluations

**Problem**  
Generic LLM answers on legal scenarios often hedge, mis-map jurisdiction, or miss burden-shifting logic. Buyers of legal/compliance AI annotation need **gold-standard packs**, not vibes.

**What we built**

- Structured case folders: facts → deficient AI response → corrected analysis → statutory map → cross-examination → rubric
- Bilingual material (English primary + Spanish addendum where doctrine is local)
- Browser showcase for demos (`showcase/` interactive UI)

**Public demo**  
[`showcase/legal-ai-evals/`](../showcase/legal-ai-evals/)

---

## 4. Clip for WhatsApp (system audio micro-tool)

**Problem**  
People need a short clip of **what the PC is playing** (a video, a call in a browser tab, a game cue) to send on WhatsApp — without a full screen recorder or mic capture.

**What we built**

- Windows WASAPI loopback recorder (playback only, not microphone)
- Lean mono 22 kHz path + HD stereo path
- One-click **M4A** export for WhatsApp attach
- Global hotkey, portable `clips\` folder, optional PyInstaller build

**Public demo**  
[`showcase/whatsapp-system-clipper/`](../showcase/whatsapp-system-clipper/) — source only; no sample recordings.

---

## 5. Other workflow micro-tools

Internal tools (token/cost dashboards, recruiting helpers) prove product sense. Client branding and personal data stay out of public repos.

---

## How to cite this work

> Practic-AI. Industrial NOx projection demo (synthetic). https://github.com/Practic-AI/General
