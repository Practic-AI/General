# Rubric — Gold-Standard Response (Influence / Governance Prompts)

Score each dimension 0–2. **Pass = 8+ / 10.**

| # | Criterion | 0 | 1 | 2 |
|---|-----------|---|---|---|
| 1 | **Correct lead framework** | US bribery only | Mixed | FIFA Ethics + Disciplinary Code (Art. 27) first |
| 2 | **Factual precision** | "Ban lifted" / sloppy outcome | Partial | Distinguishes suspension of implementation vs. vacatur; cites Art. 27 |
| 3 | **Uses admissions as evidence** | Rumor / "appearance" only | Acknowledges | Integrates admitted contact into element map |
| 4 | **Element mapping** | Unstructured | Partial | Full table with **contested** elements marked |
| 5 | **Steelmans real defense** | Strawman only | Mentions Art. 27 | Engages comparators (Ronaldo/Otamendi/Caicedo) + limits |
| 6 | **Burden allocation** | All on critic | Ambiguous | Governance burden on institution after political contact |
| 7 | **Causation** | "Correlation only" | Mixed | Factual/legal/proximate; addresses "would've happened anyway" |
| 8 | **Citation discipline** | Misattributes instruments | Mostly correct | CoE/UNCAC for influence; OECD Anti-Bribery not cited for trading-in-influence |
| 9 | **Anchor question** | Omits | Implicit | *Why was intervention entertained before review?* |
| 10 | **Accessibility** | Hedge / jargon | Thin | Concise, connected, survives informed cross-check |

---

## Automatic fail flags

- [ ] Ignores FIFA's **Article 27** defense entirely
- [ ] Treats comparator deferrals as irrelevant without distinguishing political contact
- [ ] "No neutral criteria" asserted as ✓ when FIFA cited Art. 27 + precedents
- [ ] Attributes trading-in-influence to **OECD Anti-Bribery Convention**
- [ ] Equates appearance with full exculpation when admissions exist
- [ ] Ends without institutional conclusion

---

## Tutor annotation template

```markdown
**Error type:** [jurisdiction / fact / strawman / citation / burden]
**Model said:** "..."
**Should say:** "..."
**Training note:** [what data would fix this pattern]
```

---

## Example training note (this case)

Models must **steelman the defendant's real rule-based defense** before attacking independence. Reward responses that: (1) cite Art. 27 accurately, (2) distinguish Balogun's political entry point from Ronaldo/Otamendi/Caicedo comparators, (3) preserve the anchor question on **why intervention was entertained**.