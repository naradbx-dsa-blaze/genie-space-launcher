"""
Genie Space Launcher — a tiny Databricks App that gives users a way into a
Genie space from inside your application.

It shows TWO patterns on one page:
  1. Open in a new tab  (a link/button)  -> always works, recommended
  2. Embedded in-app     (an iframe)      -> works only if the workspace allows framing

Configuration comes entirely from environment variables (set in app.yaml /
databricks.yml). Nothing about your workspace or space is hard-coded.
"""
import os

from flask import Flask, render_template_string

app = Flask(__name__)


# --------------------------------------------------------------------------- #
# Config — resolve the Genie space URL from the environment                    #
# --------------------------------------------------------------------------- #
def genie_space_url() -> str:
    """Full URL to the Genie space.

    Either set GENIE_SPACE_URL directly, or set GENIE_SPACE_ID and we build it
    from the workspace host (DATABRICKS_HOST is auto-injected in Databricks Apps).
    """
    explicit = os.environ.get("GENIE_SPACE_URL", "").strip()
    if explicit:
        return explicit
    host = os.environ.get("DATABRICKS_HOST", "").strip().rstrip("/")
    space_id = os.environ.get("GENIE_SPACE_ID", "").strip()
    if host and space_id:
        if not host.startswith("http"):
            host = "https://" + host
        return f"{host}/genie/rooms/{space_id}"
    return ""  # not configured yet


PAGE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{ title }}</title>
  <style>
    :root { color-scheme: light dark; }
    body { margin:0; font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;
           background:#f5f6f8; color:#1a1a1a; }
    .wrap { max-width:920px; margin:0 auto; padding:28px 20px 48px; }
    h1 { font-size:24px; margin:0 0 4px; }
    .sub { color:#555; margin:0 0 28px; }
    .card { background:#fff; border:1px solid #e2e5ea; border-radius:12px;
            padding:20px 22px; margin-bottom:22px;
            box-shadow:0 1px 2px rgba(0,0,0,.04); }
    .card h2 { font-size:17px; margin:0 0 6px; }
    .card p { color:#555; margin:0 0 16px; font-size:14px; line-height:1.5; }
    .tag { display:inline-block; font-size:11px; font-weight:600; letter-spacing:.4px;
           text-transform:uppercase; padding:2px 8px; border-radius:999px; margin-left:8px; }
    .tag.rec { background:#e6f4ea; color:#137333; }
    .tag.note { background:#fef7e0; color:#8a6d00; }
    .btn { display:inline-block; background:#1b6ec2; color:#fff; text-decoration:none;
           font-weight:600; font-size:15px; padding:12px 22px; border-radius:8px; }
    .btn:hover { background:#155a9c; }
    iframe { width:100%; height:640px; border:1px solid #d5d8dd; border-radius:8px; background:#fff; }
    code { background:#eef0f3; padding:1px 6px; border-radius:5px; font-size:13px; }
    .warn { background:#fff8e6; border:1px solid #f2d98a; border-radius:8px;
            padding:12px 14px; font-size:13px; color:#6b5300; margin-top:14px; }
    .unset { background:#fdecea; border:1px solid #f4b6b0; color:#8a1c14;
             border-radius:8px; padding:14px 16px; font-size:14px; }
  </style>
</head>
<body>
  <div class="wrap">
    <h1>{{ title }}</h1>
    <p class="sub">Two ways to get into your Genie space from this app.</p>

    {% if not space_url %}
    <div class="unset">
      <b>Not configured yet.</b> Set <code>GENIE_SPACE_URL</code> (or
      <code>GENIE_SPACE_ID</code>) in <code>app.yaml</code> / <code>databricks.yml</code>,
      then redeploy. See the README.
    </div>
    {% else %}

    <!-- Option 1: link / button -->
    <div class="card">
      <h2>Option 1 — Open in a new tab <span class="tag rec">Recommended</span></h2>
      <p>A simple link. The user clicks and lands in the full Genie space in a new browser
         tab, already signed in with their own Databricks identity. This always works.</p>
      <a class="btn" href="{{ space_url }}" target="_blank" rel="noopener">Open Genie Space ↗</a>
    </div>

    <!-- Option 2: embedded iframe -->
    <div class="card">
      <h2>Option 2 — Embedded in-app <span class="tag note">Depends on workspace</span></h2>
      <p>The same Genie space rendered inside this page via an <code>&lt;iframe&gt;</code>.
         Users stay in your app. This only renders if the workspace permits framing of the
         Genie UI — otherwise the frame shows blank or a refusal and you should use Option 1.</p>
      <iframe src="{{ space_url }}" title="Genie Space"
              sandbox="allow-same-origin allow-scripts allow-forms allow-popups"></iframe>
      <div class="warn">
        If this frame is blank: the app origin (<code>*.databricksapps.com</code>) differs from
        the workspace origin, and the workspace may block framing for security. Use Option 1,
        or build an in-app chat with the Genie Conversation API (see README).
      </div>
    </div>
    {% endif %}
  </div>
</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(
        PAGE,
        title=os.environ.get("APP_TITLE", "Genie Space Launcher"),
        space_url=genie_space_url(),
    )


@app.route("/healthz")
def healthz():
    return {"status": "ok"}


if __name__ == "__main__":
    # Databricks Apps injects DATABRICKS_APP_PORT; 8000 is the local-dev fallback.
    port = int(os.environ.get("DATABRICKS_APP_PORT", 8000))
    app.run(host="0.0.0.0", port=port)
