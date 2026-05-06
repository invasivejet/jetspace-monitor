# GitHub remotes: **invasivejet** (canonical), **joel-saucedo** (legacy), **jetbundle** org

## Canonical model (what you asked for)

| Role | GitHub | Git remote name (suggested) |
|------|--------|-----------------------------|
| **Primary** — all day-to-day `git pull` / `git push` | [invasivejet/jetspace-monitor](https://github.com/invasivejet/jetspace-monitor) | `origin` → `git@github.com-ij:invasivejet/jetspace-monitor.git` |
| **Legacy / archive** — original author account | joel-saucedo (same repo name if it exists) | `joel-saucedo` (saved by script when retargeting `origin`) |
| **Organization** (site + org-wide settings) | [github.com/jetbundle](https://github.com/jetbundle) | Not a git remote for this app unless you add a org-owned fork |

**Commits** stay attributed to whatever `user.name` / `user.email` you configure locally; moving “ownership” of the **repo** on GitHub is done with **transfer** or **permissions** (below), not by git magic.

## A) Make `invasivejet/jetspace-monitor` the only `origin` you use

Prereq: `ssh -T git@github.com-ij` prints **invasivejet** (your SSH host alias may differ — pass `-SshHostAlias`).

```powershell
cd C:\Users\joela\jetspace-monitor
.\scripts\set-origin-invasivejet.ps1
.\scripts\verify-git-flow.ps1
git pull origin main
git push -u origin main
```

`set-origin-invasivejet.ps1` keeps the previous `origin` URL under remote **`joel-saucedo`** when it wasn’t already invasivejet.

## B) **jetbundle** organization — not the same namespace as invasivejet

- Org: **https://github.com/jetbundle** — public profile shows one public repo as of last check: **`jetbundle.github.io`**.
- **Org permissions** (so **invasivejet** can help manage the org): an **Owner** must sign in → **Organization settings** → **People** → invite **invasivejet** (Member or Owner per your policy).  
  People URL: `https://github.com/orgs/jetbundle/people`

This repository (**jetspace-monitor**) lives under **user** `invasivejet`, not under org `jetbundle`, unless you **transfer** the repo into the org (GitHub repo **Settings → Danger zone → Transfer ownership**). That is a deliberate, irreversible-looking action — do it in the browser as an owner, not via automation here.

## C) Audit notes: **jetbundle/jetbundle.github.io** (public, read-only)

From the public GitHub page (no login):

- Repo: [jetbundle/jetbundle.github.io](https://github.com/jetbundle/jetbundle.github.io)
- Appears to be a **GitHub Pages** style site (HTML), low activity surface.
- **Private content** cannot be audited from outside; clone as an org member and run your usual secret scan / review locally.

We did **not** modify that repo from this workspace.

## D) “Overwrite both repos” / force-push

**Do not** force-push to shared `main` unless everyone agrees — it rewrites history for all collaborators.

If you truly need to replace remote history (empty invasivejet repo + local has the code):

1. Backup: `git bundle create backup.bundle --all`
2. Then only if intentional: `git push --force origin main` (requires permission on the remote)

This project does **not** run those commands for you.

## E) Invite people to **jetbundle**

1. `https://github.com/orgs/jetbundle/people`
2. **Invite member** → e.g. **invasivejet** for org management, others as needed.

## F) Sign-in pages

| Goal | URL |
|------|-----|
| GitHub login | https://github.com/login |
| SSH keys | https://github.com/settings/keys |
| jetspace-monitor (canonical) | https://github.com/invasivejet/jetspace-monitor |
| jetbundle org | https://github.com/jetbundle |
| jetbundle People | https://github.com/orgs/jetbundle/people |

## G) Windows `.exe` desktop bundle

See `scripts/build-jetspace-exe.ps1` → `backend\dist\JetspaceMonitor\JetspaceMonitor.exe`.
