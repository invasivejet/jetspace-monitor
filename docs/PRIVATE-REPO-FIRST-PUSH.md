# First push to **invasivejet** as a **private** repository

## Repo name

Use **`invasivejet/jetspace-monitor`** (matches this codebase and docs).  
If you meant a different name (e.g. typo “jetspacemonitory”), create that name on GitHub instead and set `origin` accordingly:

```powershell
git remote set-url origin git@github.com-ij:invasivejet/<YOUR-REPO-NAME>.git
```

## 1) Create the private repo (browser)

1. Sign in as **invasivejet**: https://github.com/new  
2. Owner: **invasivejet**  
3. Repository name: `jetspace-monitor`  
4. **Private** ✓  
5. **Do not** add README / .gitignore / license (avoids unrelated first commit if you already have history locally).  
6. Create repository.

## 2) Wire SSH for invasivejet

`ssh -T git@github.com-ij` must greet **invasivejet** (see `scripts/ssh-config.github.template` and `AGENTS.md`).

## 3) On your PC (PowerShell)

Install **Git for Windows** if `git` is missing: https://git-scm.com/download/win

```powershell
cd C:\Users\joela\jetspace-monitor
.\scripts\set-origin-invasivejet.ps1
.\scripts\verify-git-flow.ps1
```

If the local branch is not `main` yet:

```powershell
git branch -M main
```

Push:

```powershell
git push -u origin main
```

## 4) One-shot commit + push (after edits)

```powershell
cd C:\Users\joela\jetspace-monitor
.\scripts\commit-and-push-origin.ps1 -Message "Describe your change"
```

`commit-and-push-origin.ps1` searches common paths for `git.exe` if `git` is not on PATH.

## 5) If push is rejected

- **`Permission to invasivejet/... denied to joel-saucedo`** → GitHub accepted your SSH connection as **joel-saucedo** (wrong key). This usually means `origin` uses `git@github.com:...` instead of the **`github.com-ij`** host alias. Run `.\scripts\set-origin-invasivejet.ps1` again (it sets `git@github.com-ij:invasivejet/jetspace-monitor.git`) and confirm `ssh -T git@github.com-ij` prints **invasivejet**.
- **Permission denied (publickey)** → no key offered; add invasivejet’s public key to GitHub or fix `IdentityFile` path in `~/.ssh/config`.
- **Rejected (non-fast-forward)** → someone else pushed; `git pull --rebase origin main` then push again.  
- **Empty remote** → first push must be `git push -u origin main` from a repo that already has commits.

## 6) Automation limit

This workspace cannot run `git push` with your credentials. You must run the commands on a machine where **Git + SSH** work.
