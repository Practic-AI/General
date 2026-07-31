# Push this monorepo to GitHub (`Practic-AI/General`)

This machine did **not** have authenticated access to `https://github.com/Practic-AI/General` when the portfolio was built (repo returned 404 or was private; GitHub CLI `gh` was not installed). You push from your account.

## One-time setup

1. Create the org **Practic-AI** (if not done) and empty repo **General** (no README if you already have local commits).
2. Install [GitHub CLI](https://cli.github.com/) *or* use Git Credential Manager (already common on Windows Git).
3. Authenticate:

```powershell
# Option A — GitHub CLI
winget install GitHub.cli
gh auth login
# follow browser prompts; choose HTTPS or SSH

# Option B — first git push will open a browser login via Git Credential Manager
```

4. Set your identity (if not already):

```powershell
git config --global user.name "Your Name"
git config --global user.email "you@email.com"
```

## First push (from this folder)

```powershell
cd "C:\Users\dranz\Grok folder\practic-ai"

# if not already a git repo:
git init
git branch -M main
git remote add origin https://github.com/Practic-AI/General.git

git add .
git status   # confirm no client data, no huge binaries
git commit -m "Initial Practic-AI portfolio: NOx demo + legal evals"
git push -u origin main
```

If the remote already has a commit (e.g. empty README):

```powershell
git pull origin main --rebase
git push -u origin main
```

## Recommended org hygiene

| Item | Recommendation |
|------|----------------|
| Repo visibility | **Public** for portfolio; keep client work in **private** repos |
| Default branch | `main` |
| Topics | `machine-learning`, `industrial-analytics`, `emissions`, `legal-ai`, `portfolio` |
| About blurb | `Practical AI & industrial analytics — models you can run.` |
| Separate private repos | `client-*` never mirrored here |
| GitHub Pages (optional) | Point Pages at `/docs` or a `site/` later |

## Name: Practic-AI

Works well:

- Suggests **practical** (vs hype)
- Easy to say in EN/ES contexts
- Available as org handle on your side

Use the same spelling everywhere: GitHub, LinkedIn, invoices, PDF one-pager.

## What never goes in this remote

See [privacy.md](privacy.md). Especially: UTE/client packs, recruiting CVs, `Modelo projectivo lineal/Datos.xlsx`, personal folders, NSFW, prank exes.
