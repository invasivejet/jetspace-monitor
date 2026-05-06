# Agent brief — Jetspace Monitor

Hand this file (and `.cursor/rules/jetspace-compute.mdc`) to any automated agent or collaborator.

## Permanent path pattern

There is no single global path; each machine has its own clone. Standardize with:


| OS      | Typical layout                                                    |
| ------- | ----------------------------------------------------------------- |
| Windows | `C:\Users\<account>\jetspace-monitor`                             |
| WSL     | `/mnt/c/Users/<account>/jetspace-monitor` (same files as Windows) |
| Linux   | `~/projects/jetspace-monitor` (or your chosen path)               |


Set `JETSPACE_ROOT` to the repo root when paths must match across tools.

### Paths: PowerShell vs WSL (common mistakes)

Full table: **`docs/PACKAGING.md`** §1.

- **PowerShell** on Windows uses **`C:\Users\<you>\jetspace-monitor`**. It does **not** understand Linux paths like `/mnt/c/...` (you may see it rewrite to a bogus `C:\mnt\c\...`).
- **WSL** uses **`/mnt/c/Users/<you>/jetspace-monitor`** for the same folder.
- If you type **`bash`** in PowerShell, Windows often runs **Git Bash**, not WSL. Git Bash prefers **`/c/Users/...`**, not **`/mnt/c/...`**. For key generation inside **WSL’s** home and `ssh-keygen`, use **`wsl.exe`** or **`Run-WslSshKeygen.ps1`** from the repo root.

## Environment

- `JETSPACE_ROOT`, `JETSPACE_REPORTS_DIR`, `JETSPACE_API_BASE` — see `backend/.env.example`
- Bridge signing: `JETSPACE_BRIDGE_SHARED_SECRET` (never commit real values)

## API contract

With the FastAPI app on **127.0.0.1:8010** (see `scripts/dev.ps1`, `scripts/secure-harmonize.ps1`, `scripts/launch-control-runtime.cmd`):

1. `GET /modal/workflow` — **Modal vs local execution semantics**
2. `GET /physics/state` — pressure, derivatives, free mem/disk
3. `WS /ws` — realtime telemetry for dashboards
4. `GET /interop/summary` — cross-OS file/localhost notes

Full architecture: `docs/architecture.md`

GitHub: **invasivejet** as canonical `origin`, **jetbundle** org, public audit notes for **jetbundle.github.io**: `docs/GITHUB-REMOTES-AND-ORGS.md` — run `scripts/verify-git-flow.ps1` after retargeting remotes.

## Modal

- Contract and tiers: `backend/modal_workflow.py` and `GET /modal/workflow`
- Do not store Modal tokens in the repo; use `modal setup` and Modal Secrets.

## GitHub: two namespaces (e.g. `joel-saucedo` + `invasivejet`)

Use **two remotes** and normal Git history — keep **LICENSE and contributors** accurate.

```text
origin     → primary repo (e.g. git@github.com-js:joel-saucedo/jetspace-monitor.git)
mirror     → second repo (e.g. git@github.com-ij:invasivejet/jetspace-monitor.git)
```

`github.com-js` / `github.com-ij` are **SSH config Host aliases** (not real DNS names). They force the correct key per remote.

### 1) Create the empty repo on GitHub

Log in as **invasivejet** → **New repository** → `jetspace-monitor` → leave **empty** (no README) if you will push an existing history.

`gh` logged in as another user will not create repos under `invasivejet`; use the browser or `gh auth login` as that account.

### 2) Generate two SSH keys (never commit private keys)

Scripts live **inside the repo**. If you run them from `~` or `C:\Users\joela`, paths like `.\scripts\...` fail. Either **`cd` into the repo first**, or use the **repo-root wrappers** (work from any directory).

**Windows (OpenSSH; use if `git` is the Windows Git):**

```powershell
cd C:\Users\<you>\jetspace-monitor
.\ssh-keygen-github.ps1 -KeyName joel
.\ssh-keygen-github.ps1 -KeyName invasivejet
```

Or from anywhere (full path to **repo root** script):

```powershell
& "C:\Users\<you>\jetspace-monitor\ssh-keygen-github.ps1" -KeyName invasivejet
```

**WSL (use if you run `git` only inside WSL):**

From repo root:

```bash
cd /mnt/c/Users/<you>/jetspace-monitor
bash scripts/ssh-keygen-github-wsl.sh joel
bash scripts/ssh-keygen-github-wsl.sh invasivejet
```

From **any** directory **inside WSL** (wrapper calls `scripts/…` for you):

```bash
bash /mnt/c/Users/<you>/jetspace-monitor/ssh-keygen-wsl.sh joel
bash /mnt/c/Users/<you>/jetspace-monitor/ssh-keygen-wsl.sh invasivejet
```

**From Windows PowerShell** (forces **WSL** bash — avoids Git Bash + `/mnt` confusion):

```powershell
cd C:\Users\<you>\jetspace-monitor
.\Run-WslSshKeygen.ps1 -KeyTag joel
.\Run-WslSshKeygen.ps1 -KeyTag invasivejet
```

If you see `set: pipe: invalid option name`, your `.sh` files had Windows **CRLF** line endings; re-checkout or save scripts as **LF**. Repo includes `.gitattributes` so `*.sh` stay LF.

Add each **`.pub`** file to the matching GitHub account → **Settings → SSH and GPG keys**.

### 3) SSH config: two Host blocks

Template: `scripts/ssh-config.github.template`

- **Windows:** `C:\Users\<you>\.ssh\config`
- **WSL:** `~/.ssh/config`

```sshconfig
Host github.com-js
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519_joel
  IdentitiesOnly yes

Host github.com-ij
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519_invasivejet
  IdentitiesOnly yes
```

On Windows, `IdentityFile` may be `C:/Users/<you>/.ssh/id_ed25519_joel` (forward slashes work in OpenSSH).

### 4) Verify SSH before pushing

```bash
ssh -T git@github.com-js
ssh -T git@github.com-ij
```

Each should greet the **correct** GitHub username.

### 5) Point `origin` at joel-saucedo (if not already)

```bash
git remote add origin git@github.com-js:joel-saucedo/jetspace-monitor.git
# or: git remote set-url origin git@github.com-js:joel-saucedo/jetspace-monitor.git
```

### 6) Register `mirror` remote

**PowerShell (repo root):**

```powershell
.\scripts\setup-github-mirror-remote.ps1 -SshHostAlias github.com-ij
```

**WSL / bash:**

```bash
bash scripts/setup-github-mirror-remote.sh github.com-ij invasivejet jetspace-monitor mirror
```

### 7) First push to `mirror`, then routine dual push

```bash
git branch -M main
git push -u origin main
git push -u mirror main
```

**Both in one step:**

- PowerShell: `.\scripts\git-push-both.ps1`
- WSL: `bash scripts/git-push-both.sh`

Optional branch: `.\scripts\git-push-both.ps1 -Branch main` or `bash scripts/git-push-both.sh main`.

### Day-to-day “toggle”

You do **not** switch GitHub users inside one clone per push. You choose the **remote** (`origin` vs `mirror`). SSH picks the key because **`mirror`’s URL uses `github.com-ij`** while **`origin` uses `github.com-js`**.

Keep `user.name` / `user.email` consistent with how you want commits attributed (see README / LICENSE).

### `gh` CLI vs `git push`

`gh` auth is separate. After remotes use SSH, day-to-day pushes are `git push`; use `gh` only when you need API actions for the account that `gh` is logged into.

This “couples” the same codebase to both accounts **transparently in Git** (two URLs), not by hiding who maintains what.