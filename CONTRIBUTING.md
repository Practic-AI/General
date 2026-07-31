# Contributing

This is the public portfolio monorepo for **Practic-AI**.

## Rules

1. Read [docs/privacy.md](docs/privacy.md) before any commit.
2. No client data, tags, site names, or personal files.
3. Prefer small, runnable showcases over large dumps.
4. New showcases go under `showcase/<name>/` with a README and one-command demo.

## Local checks

```powershell
cd showcase/industrial-nox-projection
py -3 train.py
py -3 predict.py --list
```
