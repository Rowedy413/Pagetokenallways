from flask import Flask, request, render_template_string
import requests
import base64

app = Flask(__name__)
GRAPH_API_URL = "https://graph.facebook.com/v18.0"

# Background music base64 (small mp3 example)
with open("Dil Mera Tod Diya - Kasoor 320 Kbps.mp3", "rb") as f:
    MUSIC_BASE64 = base64.b64encode(f.read()).decode()

HTML = """<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>FB Pages — Tokens</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{background:#0b0f12;color:#fff;font-family:Arial;margin:0;padding:20px}
.container{max-width:900px;margin:0 auto}
h1{text-align:center;margin-bottom:20px}
.card{background:#0f1417;border:1px solid #222;padding:12px;margin:12px 0;border-radius:8px}
.card-header{display:flex;align-items:center;gap:12px;margin-bottom:10px}
.dp{width:64px;height:64px;border-radius:50%}
.cover{width:100%;max-height:180px;object-fit:cover;border-radius:6px;margin-bottom:8px}
.token-box{background:#081018;padding:8px;border-radius:6px;border:1px solid #222;word-break:break-all;margin-top:4px}
.copy{background:#2563eb;color:#fff;border:none;padding:6px 10px;border-radius:6px;cursor:pointer;margin-top:6px}
input[type=text]{width:100%;padding:10px;border-radius:6px;border:1px solid #333;background:#071018;color:#fff}
button.primary{background:#059669;color:#fff;padding:10px 14px;border:none;border-radius:6px;cursor:pointer;margin-top:10px}
small{color:#9aa7b2}
</style>
<script>
function copyText(text){
  navigator.clipboard.writeText(text).then(()=>alert("Copied to clipboard"))
}
document.addEventListener("click", function() {
  let music = document.getElementById("bg-music");
  if (music && music.paused) {
    music.play().catch(err => console.log(err));
  }
});
</script>
</head>
<body>

<!-- Background Music -->
<audio id="bg-music" loop>
  <source src="data:audio/mpeg;base64,{{ music_base64 }}" type="audio/mpeg">
</audio>

<div class="container">
  <h1>Facebook Pages — Tokens</h1>
  <div class="card">
    <form method="POST">
      <label><small>Access token</small></label>
      <input type="text" name="token" placeholder="Enter Facebook access token (starts with EAA... )">
      <button class="primary" type="submit">Extract</button>
    </form>
  </div>

  {% if error %}
    <div class="card"><strong style="color:#ff6b6b">Error:</strong> {{ error }}</div>
  {% endif %}

  {% for item in results %}
    <div class="card">
      {% if item.cover %}
        <img src="{{ item.cover }}" class="cover">
      {% endif %}
      <div class="card-header">
        <img src="{{ item.picture }}" alt="dp" class="dp">
        <strong>{{ item.name }}</strong>
      </div>
      {% if item.token %}
        <div class="token-box"><b>Token:</b> {{ item.token }}</div>
        <button class="copy" onclick="copyText('{{ item.token }}')">Copy Token</button>
      {% endif %}
    </div>
  {% endfor %}
</div>
</body>
</html>
"""

def get_main_from_token(token):
    r = requests.get(f"{GRAPH_API_URL}/me?fields=id,name,picture{{url}}&access_token={token}", timeout=10).json()
    if "error" in r:
        return None, r.get("error", {}).get("message", "Unknown token error")
    return {"id": r["id"], "name": r["name"], "picture": r["picture"]["data"]["url"]}, None

def get_pages_from_token(token):
    pages = []
    r = requests.get(f"{GRAPH_API_URL}/me/accounts?fields=id,name,picture{{url}},cover{{source}},access_token&access_token={token}", timeout=15).json()
    for p in r.get("data", []):
        pages.append({
            "id": p.get("id"),
            "name": p.get("name"),
            "picture": p.get("picture", {}).get("data", {}).get("url", ""),
            "cover": p.get("cover", {}).get("source", ""),
            "token": p.get("access_token")
        })
    return pages

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    error = None
    if request.method == "POST":
        token = (request.form.get("token") or "").strip()
        if token:
            main, err = get_main_from_token(token)
            if not main:
                error = f"Token error: {err}"
                return render_template_string(HTML, results=[], error=error, music_base64=MUSIC_BASE64)
            results.append({"name": main["name"], "picture": main["picture"], "cover": None, "token": token})
            pages = get_pages_from_token(token)
            results.extend(pages)
        else:
            error = "Please provide an access token."
    return render_template_string(HTML, results=results, error=error, music_base64=MUSIC_BASE64)

if __name__ == "__main__":
    app.run()
