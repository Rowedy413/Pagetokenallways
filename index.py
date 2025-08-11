import requests
from flask import Flask, request, render_template_string, send_file
from io import BytesIO

app = Flask(__name__)

# === SETTINGS ===
# Change this URL to update the background image
BACKGROUND_IMAGE_URL = "https://i.ibb.co/vCd29NJd/1751604135213.jpg"

GRAPH_API_VERSION = "v20.0"  # FB Graph API version

HTML = """
<!doctype html>
<html>
<head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta charset="utf-8">
<title>ROWEDY KIING OWNER - FB Tokens & Pages</title>
<style>
:root{
  --card-bg: rgba(0,0,0,0.65);
  --accent: #10b981;
  --muted: #9aa7b2;
}
html,body{height:100%;margin:0}
body {
  background: url("{{ bg_url }}") no-repeat center center fixed;
  background-size: cover;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial;
  color: #fff;
  -webkit-font-smoothing:antialiased;
  -moz-osx-font-smoothing:grayscale;
  padding: 16px;
  box-sizing: border-box;
}
.app {
  max-width: 920px;
  margin: 8px auto;
  position: relative;
  z-index: 2;
}
.top-card {
  background: var(--card-bg);
  padding: 14px;
  border-radius: 12px;
  box-shadow: 0 6px 18px rgba(0,0,0,0.5);
  margin-bottom: 12px;
}
.form-row {display:flex;flex-direction:column;gap:8px}
textarea,input[type=file],button.input-btn {
  width:100%;
  padding:10px;
  border-radius:8px;
  border:1px solid rgba(255,255,255,0.08);
  background: rgba(7,16,24,0.6);
  color: #fff;
  resize: vertical;
}
.controls {display:flex;gap:8px;flex-wrap:wrap;margin-top:8px}
.button {
  padding:10px 12px;border-radius:8px;border:0;cursor:pointer;
  background: var(--accent); color:#062022; font-weight:600;
}
.button.secondary { background: #2563eb; color: #fff; }
.small { font-size: 13px; color: var(--muted); }

.result-block {
  background: linear-gradient(180deg, rgba(0,0,0,0.55), rgba(0,0,0,0.45));
  padding: 12px;
  margin: 12px 0;
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  align-items: stretch;
  border: 1px solid rgba(255,255,255,0.04);
}

/* user header */
.user-header {
  display:flex;
  gap: 12px;
  align-items: center;
  border-bottom: 1px solid rgba(255,255,255,0.04);
  padding-bottom: 10px;
}
.user-header img { width:72px;height:72px;border-radius:50%;object-fit:cover;border:2px solid rgba(255,255,255,0.06) }
.user-meta { display:flex;flex-direction:column;gap:4px }
.user-meta .name { font-size:18px;font-weight:700 }
.user-meta .muted { color: var(--muted); font-size:13px }

/* pages list */
.pages { display:flex;flex-direction:column;gap:8px;padding-top:8px }
.page {
  display:flex;gap:10px;align-items:center;padding:8px;border-radius:8px;background:rgba(255,255,255,0.02);
}
.page img { width:46px;height:46px;border-radius:8px;object-fit:cover }
.token-box { background: rgba(7,16,24,0.6); padding:8px;border-radius:8px;border:1px solid rgba(255,255,255,0.03); font-family:monospace; font-size:13px; word-break:break-all; max-width:100%}
.row-right { margin-left:auto; display:flex; gap:8px; align-items:center; }

/* responsive */
@media (max-width:600px) {
  .user-header img { width:64px;height:64px }
  .token-box { font-size:12px }
}

/* rain canvas sits behind content */
#rainCanvas { position: fixed; left:0; top:0; width:100%; height:100%; z-index:1; pointer-events:none; opacity:0.9; }
.app { position: relative; z-index:2; }
</style>
</head>
<body> 
<canvas id="rainCanvas"></canvas>

<div class="app">
  <div class="top-card">
    <h2 style="margin:0 0 8px 0">FB Tokens & Pages</h2>
    <div class="form-row">
      <form method="POST" enctype="multipart/form-data" id="tokenForm">
        <label class="small">Single User Token (optional)</label>
        <textarea name="single_token" rows="3" placeholder="Paste a user access token (EAA...)"></textarea>
        <label class="small">Or upload .txt file with one token per line</label>
        <input type="file" name="token_file" accept=".txt">
        <div class="controls">
          <button type="submit" class="button">Fetch Pages</button>
          {% if user_tokens %}
            <a href="/download_tokens"><button type="button" class="button secondary">Download tokens.txt</button></a>
          {% endif %}
          {% if page_tokens %}
            <a href="/download_page_tokens"><button type="button" class="button secondary">Download page_tokens.txt</button></a>
          {% endif %}
        </div>
        <div class="small">Duplicate tokens are automatically removed; results show user profile (top) and pages (below).</div>
      </form>
    </div>
  </div>

  {% for token_data in results %}
    <div class="result-block">
      <div class="user-header">
        <img src="{{ token_data.user.picture or '' }}" alt="user dp">
        <div class="user-meta">
          <div class="name">{{ token_data.user.name or "Unknown User" }}</div>
          <div class="muted">User token: <span style="font-family:monospace">{{ token_data.token }}</span></div>
        </div>
        <div class="row-right">
          <button class="button secondary" onclick="copyText('{{ token_data.token }}')">Copy User Token</button>
        </div>
      </div>

      <div class="pages">
        {% if token_data.pages %}
          {% for p in token_data.pages %}
          <div class="page">
            <img src="{{ p.picture or '' }}" alt="page dp">
            <div style="display:flex;flex-direction:column;align-items:flex-start;">
              <div style="font-weight:700">{{ p.name }}</div>
              <div class="token-box">{{ p.access_token }}</div>
            </div>
            <div class="row-right">
              <button class="button" onclick="copyText('{{ p.access_token }}')">Copy Page Token</button>
            </div>
          </div>
          {% endfor %}
        {% else %}
          <div class="small muted">No pages found for this token or token invalid.</div>
        {% endif %}
      </div>
    </div>
  {% endfor %}
</div>

<script>
// copy helper
function copyText(txt){
  navigator.clipboard.writeText(txt).then(()=>{ alert("Copied to clipboard"); }).catch(()=>{ alert("Copy failed") });
}

/* Slow subtle rain canvas */
const canvas = document.getElementById('rainCanvas');
const ctx = canvas.getContext('2d');

function resizeCanvas(){
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
}
resizeCanvas();
window.addEventListener('resize', resizeCanvas);

const drops = [];
const DROP_COUNT = Math.round(Math.max(40, window.innerWidth / 20));
for(let i=0;i<DROP_COUNT;i++){
  drops.push({
    x: Math.random()*canvas.width,
    y: Math.random()*canvas.height,
    len: Math.random()*12 + 8,
    speed: Math.random()*0.9 + 0.3,
    alpha: Math.random()*0.4 + 0.15
  });
}

function frame(){
  ctx.clearRect(0,0,canvas.width,canvas.height);
  ctx.lineWidth = 1;
  ctx.lineCap = 'round';
  for(let d of drops){
    ctx.strokeStyle = 'rgba(200,220,255,' + d.alpha + ')';
    ctx.beginPath();
    ctx.moveTo(d.x, d.y);
    ctx.lineTo(d.x, d.y + d.len);
    ctx.stroke();
    d.y += d.speed;
    if(d.y > canvas.height + 10){ d.y = -d.len; d.x = Math.random()*canvas.width; }
  }
  requestAnimationFrame(frame);
}
frame();
</script>
</body>
</html>
"""

from collections import namedtuple
TokenData = namedtuple("TokenData", ["token", "user", "pages"])

# In-memory sets (per app instance). These are reset on restart.
_user_tokens_set = set()
_page_tokens_set = set()

def fetch_user_info(token):
    """Return dict {id,name,picture} or empty dict on error."""
    try:
        url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/me?fields=id,name,picture&access_token={token}"
        r = requests.get(url, timeout=10).json()
        if "error" in r:
            return {}
        pic = r.get("picture", {}).get("data", {}).get("url", "")
        return {"id": r.get("id"), "name": r.get("name"), "picture": pic}
    except Exception:
        return {}

def fetch_pages_for_token(token):
    """Return list of pages each as dict with keys: id,name,picture,access_token"""
    pages = []
    try:
        url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/me/accounts?fields=id,name,picture,access_token&access_token={token}"
        r = requests.get(url, timeout=12).json()
        if "error" in r:
            return pages
        for p in r.get("data", []):
            pic = p.get("picture", {}).get("data", {}).get("url", "")
            pages.append({
                "id": p.get("id"),
                "name": p.get("name"),
                "picture": pic,
                "access_token": p.get("access_token", "")
            })
    except Exception:
        pass
    return pages

@app.route("/", methods=["GET", "POST"])
def index():
    global _user_tokens_set, _page_tokens_set
    results = []
    user_tokens = []
    page_tokens = []

    if request.method == "POST":
        tokens_set = set()

        # Single token
        single = (request.form.get("single_token") or "").strip()
        if single:
            tokens_set.add(single)

        # File upload
        file = request.files.get("token_file")
        if file and file.filename:
            try:
                content = file.read().decode("utf-8", errors="ignore")
                for line in content.splitlines():
                    t = line.strip()
                    if t:
                        tokens_set.add(t)
            except Exception:
                pass

        # Remove duplicates and sort for stable order
        tokens_list = sorted(tokens_set)

        for t in tokens_list:
            # fetch user info + pages
            user_info = fetch_user_info(t)
            pages = fetch_pages_for_token(t)
            # add to in-memory global sets
            _user_tokens_set.add(t)
            for p in pages:
                if p.get("access_token"):
                    _page_tokens_set.add(p["access_token"])
            results.append(TokenData(token=t, user=user_info, pages=pages))

        user_tokens = sorted(_user_tokens_set)
        page_tokens = sorted(_page_tokens_set)

    # Render the page. results is a list of TokenData namedtuples
    return render_template_string(
        HTML,
        results=results,
        user_tokens=user_tokens,
        page_tokens=page_tokens,
        bg_url=BACKGROUND_IMAGE_URL
    )

@app.route("/download_tokens")
def download_tokens():
    data = "\n".join(sorted(_user_tokens_set))
    if not data:
        return "No user tokens available", 400
    buf = BytesIO(data.encode())
    return send_file(buf, as_attachment=True, download_name="tokens.txt", mimetype="text/plain")

@app.route("/download_page_tokens")
def download_page_tokens():
    data = "\n".join(sorted(_page_tokens_set))
    if not data:
        return "No page tokens available", 400
    buf = BytesIO(data.encode())
    return send_file(buf, as_attachment=True, download_name="page_tokens.txt", mimetype="text/plain")

if __name__ == "__main__":
    # When running locally
    app.run(host="0.0.0.0", port=5000, debug=True)
