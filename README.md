# Genie Space Launcher

A tiny Databricks App that lets your users jump into a **Genie space** from
inside your own application. It shows **two patterns** on one page:

| # | Pattern | How it feels | Reliability |
|---|---------|--------------|-------------|
| 1 | **Open in a new tab** (link/button) | Click → full Genie space opens in a new tab, signed in as the user | ✅ Always works — **recommended** |
| 2 | **Embedded in-app** (`<iframe>`) | Genie renders inside your app page | ⚠️ Works only if the workspace allows framing (see note below) |

The app is a single `app.py` (Flask). No build step, no frontend toolchain —
easy to read and to deploy.

---

## What's in the repo

| File | Purpose |
|------|---------|
| `app.py` | The whole app: renders both patterns, reads the space URL from env vars |
| `app.yaml` | Runtime config for the Databricks Apps UI deploy (start command + env) |
| `databricks.yml` | Bundle config for CLI/DABs deploy |
| `requirements.txt` | `flask` |

---

## Step 1 — Get your Genie space URL

1. In the Databricks workspace, open **Genie** and go to your space.
2. Copy the URL from the browser. It looks like:
   ```
   https://<workspace-host>/genie/rooms/01efabc1234567890abcdef
   ```
   That last segment is the **space id**.

> Don't have a space yet? Create one under **Genie → New**, pick the tables it
> can query, then copy its URL.

## Step 2 — Configure the app

Open **`app.yaml`** and paste your URL:

```yaml
env:
  - name: GENIE_SPACE_URL
    value: "https://<workspace-host>/genie/rooms/<space-id>"
```

*(Alternative: leave `GENIE_SPACE_URL` empty and set `GENIE_SPACE_ID` — the app
builds the URL from the auto-injected `DATABRICKS_HOST` plus the id.)*

If you deploy with the CLI/bundle, set the same value in **`databricks.yml`**.

## Step 3 — Run it locally (optional)

```bash
pip install -r requirements.txt
export GENIE_SPACE_URL="https://<workspace-host>/genie/rooms/<space-id>"
python app.py
# open http://localhost:8000
```

## Step 4 — Deploy to Databricks Apps

**Option A — CLI / bundle (recommended):**
```bash
databricks bundle deploy -t dev --profile <PROFILE>
databricks bundle run genie-space-launcher -t dev --profile <PROFILE>
```

**Option B — UI:** create a new App in the workspace, upload this folder (or
point it at the repo), and the platform reads `app.yaml`.

Check status:
```bash
databricks apps get genie-space-launcher --profile <PROFILE> -o json   # look for app_status.state: RUNNING
```

## Step 5 — Grant access so users can enter the space

Clicking the link opens Genie **as the signed-in user**, so each user needs:

- **CAN RUN** (or higher) on the **Genie space** — share it with the users/group.
- Access to the **SQL warehouse** the space uses (CAN USE).
- **SELECT** on the underlying Unity Catalog tables the space queries.

Without these, the link opens but Genie shows a permission error.

---

## About the embedded (iframe) option

A Databricks App is served from `*.databricksapps.com`, while Genie lives on the
workspace domain (`*.databricks.com` / `*.azuredatabricks.net`) — a **different
origin**. For security, the workspace may refuse to be shown inside an iframe
(`X-Frame-Options` / CSP `frame-ancestors`). If so, Option 2's frame appears
blank or shows a refusal.

**What to do:**
- Use **Option 1** (open in a new tab) — reliable everywhere.
- Or build a true **in-app chat** experience using the **Genie Conversation
  API** (`POST /api/2.0/genie/spaces/{space_id}/start-conversation` and
  `.../messages`), rendering the answers in your own UI. This keeps users in
  your app without relying on iframing the Genie page. (If you're on AppKit,
  the `genie()` plugin wraps this for you.)

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Page says "Not configured yet" | Set `GENIE_SPACE_URL` (or `GENIE_SPACE_ID`) and redeploy |
| 502 Bad Gateway | App must bind `0.0.0.0` on `$DATABRICKS_APP_PORT` — already handled in `app.py`; don't hardcode a port |
| Link opens but Genie shows "permission denied" | Grant the user CAN RUN on the space + warehouse + table SELECT (Step 5) |
| Iframe is blank | Expected if the workspace blocks framing — use Option 1 or the Conversation API |
