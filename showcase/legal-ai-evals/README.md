# Legal AI reasoning evals

Curated evaluations for **AI legal training quality review**. Each case documents a deficient model response, a corrected analysis, and a scoring rubric.

Built to demonstrate domain expertise for legal / compliance AI annotation work — identifying where models hedge, misapply jurisdiction, or miss burden-shifting logic.

**Author context:** Practic-AI (legal analysis ES/EN + applied AI).

---

## Structure

```
cases/
  01-fifa-undue-influence/   ← governance & undue influence
templates/
  case-template/
showcase/                    ← local browser demo
```

## Per-case files

| File | Purpose |
|------|---------|
| `facts.md` | Record only — no argument |
| `bad-ai-response.md` | Deficient AI output + tagged errors |
| `corrected-analysis.md` | Primary analysis (English) |
| `analisis-es.md` | Spanish addendum — localized doctrine |
| `statutory-map.md` | Applicable frameworks |
| `cross-examination.md` | Witness questions |
| `rubric.md` | Gold-standard response checklist |

## Interactive showcase

```text
showcase/Show.bat
```

Opens a local browser demo: timeline, AI-vs-correct comparison, steelman cards, interactive rubric scorer.

Or open `showcase/index.html` directly in a browser.

---

## Privacy

Cases use **public-domain / published fact patterns** suitable for demos. No client matters, no sealed filings, no personal data of private parties beyond what is already public in the scenario design.

---

## License

MIT with the repository root, unless a case file states otherwise.
