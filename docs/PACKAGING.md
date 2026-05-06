# Repository packaging, invariants, and “where do I type this?”

## 1. WSL (bash) vs Windows (PowerShell) — same folder, different spelling

| You are in… | Go to the repo with… |
|-------------|----------------------|
| **WSL / Ubuntu bash** | `cd /mnt/c/Users/joela/jetspace-monitor` |
| **Windows PowerShell / CMD** | `cd C:\Users\joela\jetspace-monitor` |

**Do not** type `C:\Users\...` inside **bash** (WSL). Bash does not use Windows drive syntax that way.

**Do not** type `/mnt/c/...` as `cd` in **PowerShell** (PowerShell is not WSL).

### SSH keygen reminders

- **Inside WSL** (you already see `joelasaucedo@...:/mnt/c/Users/joela/jetspace-monitor$`):

  ```bash
  bash ssh-keygen-wsl.sh joel
  bash ssh-keygen-wsl.sh invasivejet
  ```

  (Run these **from the repo root**, i.e. after `cd` there — your prompt already shows you are in the right place.)

- **Windows PowerShell** (prompt like `PS C:\Users\joela>`):

  ```powershell
  cd C:\Users\joela\jetspace-monitor
  .\Run-WslSshKeygen.ps1 -KeyTag joel
  ```

  `.\Run-WslSshKeygen.ps1` only works after `cd` into **`jetspace-monitor`**, not from `C:\Users\joela` alone.

---

## 2. What must stay in Git (invariants)

These define the product; they belong on GitHub.

| Area | Purpose |
|------|---------|
| `backend/` | FastAPI app, physics, cleanup, bridge, `requirements.txt` |
| `frontend/` | Vite + React UI (`package.json`, `src/`) |
| `modal/` | Modal app entrypoints (CPU/GPU telemetry, examples) |
| `scripts/` | Automation (maintenance, WSL couple, GitHub mirror, SSH helpers) |
| `docs/` | Architecture and packaging notes |
| `.cursor/rules/` | Agent conventions for Cursor |
| `AGENTS.md` | Cross-tool agent brief |
| `README.md` | Human quick start |
| `.gitignore` / `.gitattributes` | Keep repos clean and shell scripts LF |

---

## 3. What must **not** be committed (local / secrets / reproducible)

Already excluded via `.gitignore` — do not “force add” these:

| Path / pattern | Why |
|----------------|-----|
| `backend/.venv/`, `**/.venv*` | Python environments (rebuild with `pip install -r requirements.txt`) |
| `frontend/node_modules/`, `frontend/dist/` | Node build artifacts |
| `.env`, `.env.*` | Secrets |
| `backend/secrets/` | Journal keys, bridge secrets |
| `backend/certs/` | mTLS dev certs |
| `backend/data/` | Local streams, cleanup artifacts |
| `reports/` | Generated audits (re-run scripts) |

**Invariant:** If it’s generated on your machine or contains secrets, it stays local.

---

## 4. Optional local cleanup (before zipping or auditing size)

From repo root, after pulls:

```powershell
# Remove Python cache (safe)
Get-ChildItem -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force
```

Do **not** delete `backend/secrets/` or `backend/data/` if you rely on them locally — just keep them out of Git.

---

## 5. GitHub publishing checklist

1. `git status` — no tracked secrets under `backend/secrets/` or `.env`.
2. Confirm `.gitignore` covers `reports/`, `backend/data/`, venvs.
3. Push `main` to `origin` (and `mirror` if you use two remotes — see `AGENTS.md`).
4. Tag releases when API/contract changes (`/modal/workflow` contract version in `backend/modal_workflow.py`).

---

## 6. Transparency rule

Two GitHub namespaces (e.g. personal + `invasivejet`) should differ only by **remote URL** and **SSH host alias**, not by hiding authorship. Same repo, same history, honest `LICENSE` / contributors.

## 7. Default `origin` on invasivejet + org invites

See **`docs/GITHUB-REMOTES-AND-ORGS.md`** (`set-origin-invasivejet.ps1`, **`verify-git-flow.ps1`**, `jetbundle`, **jetbundle.github.io** public audit notes).
