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

## 2. Legal AI reasoning evaluations

**Problem**  
Generic LLM answers on legal scenarios often hedge, mis-map jurisdiction, or miss burden-shifting logic. Buyers of legal/compliance AI annotation need **gold-standard packs**, not vibes.

**What we built**

- Structured case folders: facts → deficient AI response → corrected analysis → statutory map → cross-examination → rubric
- Bilingual material (English primary + Spanish addendum where doctrine is local)
- Browser showcase for demos (`showcase/` interactive UI)

**Public demo**  
[`showcase/legal-ai-evals/`](../showcase/legal-ai-evals/)

---

## 3. Workflow micro-tools (selected)

Internal and client-adjacent tools (token/cost dashboards, clippers, recruiting helpers) prove we can ship **usable software**, not only notebooks. Specific client branding and personal data stay out of public repos; structure and patterns can be re-implemented as open examples on request.

---

## How to cite this work

> Practic-AI. Industrial NOx projection demo (synthetic). https://github.com/Practic-AI/General
