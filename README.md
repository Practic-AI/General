# Practic-AI

**Practical AI & industrial analytics.**  
We ship models and tools people can run — not slideware.

| | |
|---|---|
| **Org** | [github.com/Practic-AI](https://github.com/Practic-AI) |
| **This repo** | Company portfolio, public showcases, and service overview |
| **Focus** | Industrial ML · applied AI evals · small production tools |

---

## What we do

1. **Industrial analytics** — turn plant Excel / CEMS-style exports into correlation reports, per-unit models, and operator-ready CLIs.
2. **AI evaluation for professional domains** — legal and compliance reasoning packs (facts → bad AI → corrected analysis → rubric).
3. **Micro-tools** — dashboards and workflow helpers when a spreadsheet is no longer enough.

Engagements are usually **fixed-scope packages**: discovery → deliverable ZIP + handoff, not open-ended retainers (unless you want that).

---

## Public showcases

| Showcase | What it demonstrates | Path |
|----------|----------------------|------|
| **Industrial NOx projection** | Per-unit Random Forest + linear baseline; humidity & ambient temp → NOx estimate; train / predict CLI | [`showcase/industrial-nox-projection/`](showcase/industrial-nox-projection/) |
| **Cirrus US fleet snapshot** | FAA public registry → DuckDB SQL, QC, and a dashboard of US-registered Cirrus airframes (not affiliated) | [`showcase/cirrus-us-fleet/`](showcase/cirrus-us-fleet/) |
| **Legal AI reasoning evals** | Domain evaluation design for legal training quality (bilingual ES/EN) | [`showcase/legal-ai-evals/`](showcase/legal-ai-evals/) |
| **Clip for WhatsApp** | Windows system-audio recorder → lean/HD WAV + M4A for chat (no mic, no samples in repo) | [`showcase/whatsapp-system-clipper/`](showcase/whatsapp-system-clipper/) |

> **Client work is confidential.** Public demos use **synthetic or public-domain material only**. No plant tags, site names, operator IDs, or personal data.

See [docs/privacy.md](docs/privacy.md) and [docs/case-studies.md](docs/case-studies.md).

---

## Quick start — NOx demo

```bash
cd showcase/industrial-nox-projection
py -3 -m pip install -r requirements.txt
py -3 generate_synthetic_data.py
py -3 train.py
py -3 predict.py --unit 1 --humidity 10.5 --temp 18
py -3 predict.py --series examples/series_input.csv --unit all
```

---

## Repo layout

```
General/                     ← this repository (github.com/Practic-AI/General)
  README.md                  ← you are here
  docs/                      ← company, privacy, case studies
  services/                  ← what we sell (productized offers)
  showcase/
    industrial-nox-projection/
    cirrus-us-fleet/
    legal-ai-evals/
    whatsapp-system-clipper/
```

### Local disk separation

```text
C:\Users\dranz\Practic-AI\General\   ← public git (this folder)
C:\Users\dranz\Grok folder\          ← private work only (no overlap)
```

Private client packages, raw plant files, and recruiting data **never** live in this repo.

---

## Contact

Open an issue in this repo or reach out via the org profile.  
For paid work, include: industry, data shape (columns / volume), and deadline.

---

© 2026 Practic-AI · Practical over theatrical.
