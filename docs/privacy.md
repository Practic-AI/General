# Privacy, client data & public demos

Practic-AI public repositories are built so that **nothing on GitHub can identify a client plant, person, or commercial engagement**.

## Rules (non-negotiable)

| Never publish | Why |
|---------------|-----|
| Client / operator names | Direct attribution |
| Site, station, or city clues tied to a plant | Geographic fingerprint |
| SCADA / DCS tag IDs | Unique to a facility |
| Real minute-level process series | Operational data |
| People names from chats, voice notes, emails | PII / internal process |
| Recruiting pipelines, CVs, InMails | Personal data |
| Anything under NDA | Legal risk |

## What *is* OK publicly

- Method descriptions (features, model family, train/test split)
- **Metrics on synthetic or fully scrubbed data**
- Generic unit labels (`Unit_1` … `Unit_N`)
- Generic variable names (`humidity_abs`, `temp_ambient`, `nox_mg_nm3`)
- Architecture diagrams and CLI UX
- Public-domain legal facts used in eval cases

## Industrial NOx showcase

The public package:

- Generates **synthetic** multi-unit series with realistic physical-ish relationships
- Trains models **only** on that synthetic data
- Does **not** include production `.joblib` weights from any real plant

Confidential client deliveries stay offline (or in private repos with access control). Public wording:

> *Work for a confidential industrial client. This repository demonstrates the method with synthetic process data.*

## Before every push

```text
[ ] No client names in paths, README, commits, or zip names
[ ] No SCADA tags or station names
[ ] No real plant Excel / CSV dumps
[ ] No personal emails, phones, photos
[ ] git log does not contain previously committed secrets
[ ] .gitignore covers data/raw, *.joblib from client runs, credentials
```

## Contact for data deletion

If you believe something identifying was published by mistake, open a private security advisory or contact the org owners for immediate removal and history scrub.
