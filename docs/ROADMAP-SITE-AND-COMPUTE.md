# From this repo → **jetbundle.github.io** → paid compute (honest sequence)

This doc ties **Jetspace Monitor** (local observability) to your **public site** and a **future** revenue API—without pretending the repo already is a marketplace.

## Today: what you have

| Piece | Role |
|-------|------|
| **jetspace-monitor** (this repo) | Localhost FastAPI + optional React UI + scripts; **not** a public SaaS by default. |
| **jetbundle/jetbundle.github.io** | Static **GitHub Pages** front door (HTML/CSS/JS only unless you add client-side calls to an API elsewhere). |

**GitHub Pages does not run your FastAPI app.** The site can **link** to docs, sign-up, or an API hosted on Fly/Vercel/Railway later.

## Sensible “best move” order

1. **Keep** `invasivejet/jetspace-monitor` **private** for tooling you don’t want to expose; open-source only what you intend.  
2. **Publish** user-facing copy on **jetbundle.github.io** (what the product is, how to get access, contact).  
3. **Add a separate deploy** for any public `/compute` API (serverless or small VM)—do **not** try to serve FastAPI from `github.io`.  
4. **Charge** only after one narrow endpoint works end-to-end (API key + usage counter + Stripe).  

## Smallest paid version (aligned with your notes)

- **One** `POST /compute` (or `/price-option`, etc.) on a hosted backend.  
- **GitHub Pages** explains it and links to API docs + billing.  
- **Jetspace Monitor** stays your **operator** dashboard on your machine—not the customer product unless you productize it later.

## How Jetspace Monitor still helps

- Watch CPU/RAM/disk while you run workers locally or in cloud.  
- Modal tier for burst compute (`docs/architecture.md`, `GET /modal/workflow`).  
- Cleanup gates when disk is full (`backend/cleanup.py`).

## Trap to avoid

Building “network + Web5 + token” before **one** paid request succeeds. Constraint: **no new distributed feature until a hosted endpoint returns paid value.**

## Links

- Site repo: https://github.com/jetbundle/jetbundle.github.io  
- Org: https://github.com/jetbundle  
- Canonical app repo: https://github.com/invasivejet/jetspace-monitor (private)  
- Usage: `docs/USAGE.md`  
- Git setup: `docs/PRIVATE-REPO-FIRST-PUSH.md`, `docs/GITHUB-REMOTES-AND-ORGS.md`
