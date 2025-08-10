from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)
GRAPH_API_URL = "https://graph.facebook.com/v18.0"

# --- Customize these ---
BACKGROUND_IMAGE_URL = "https://i.ibb.co/vCd29NJd/1751604135213.jpg"   # change to your background image URL
MUSIC_URL = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"  # change to your mp3 URL or data URI
# -----------------------

HTML = """
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>FB Pages — Tokens</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
  html,body{height:100%;margin:0}
  body{
    background: #0b0f12 url('{{ bg_image }}') no-repeat center center fixed;
    background-size: cover;
    color:#fff;
    font-family: Arial, Helvetica, sans-serif;
    -webkit-font-smoothing:antialiased;
    overflow-x:hidden;
    padding:20px;
  }
  .container{max-width:980px;margin:0 auto;position:relative;z-index:3}
  h1{text-align:center;margin:6px 0 20px;font-size:22px}
  .form-card{
    background:rgba(0,0,0,0.55);padding:14px;border-radius:10px;margin-bottom:18px;border:1px solid rgba(255,255,255,0.04)
  }
  input[type=text]{width:100%;padding:10px;border-radius:6px;border:1px solid #333;background:rgba(7,16,24,0.6);color:#fff}
  button.primary{margin-top:10px;background:#059669;color:#fff;border:none;padding:10px 14px;border-radius:8px;cursor:pointer}
  .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:14px;margin-top:12px}
  .card{
    background: rgba(0,0,0,0.55);
    border-radius:10px;
    padding:12px;
    border:1px solid rgba(255,255,255,0.04);
    display:flex;
    flex-direction:column;
    gap:8px;
    min-height:140px;
  }
  .cover{width:100%;height:140px;border-radius:8px;object-fit:cover;background:#111}
  .row{display:flex;align-items:center;gap:12px}
  .dp{width:64px;height:64px;border-radius:8px;object-fit:cover;border:2px solid rgba(255,255,255,0.06)}
  .name{font-weight:700}
  .token-box{background:rgba(7,16,24,0.6);padding:8px;border-radius:6px;font-size:13px;word-break:break-all;border:1px solid rgba(255,255,255,0.02)}
  .copy{background:#2563eb;color:#fff;border:none;padding:8px 10px;border-radius:6px;cursor:pointer}
  small{color:#c6d0d8}
  /* Canvas sits behind content but above background image */
  canvas#rain{position:fixed;left:0;top:0;width:100%;height:100%;z-index:2;pointer-events:none}
  /* container should be above canvas */
  .container{z-index:3;position:relative}
</style>
</head>
<body>

<canvas id="rain"></canvas>

<!-- Background music -->
<audio id="bg-music" loop>
  <source src="{{ music_url }}" type="audio/mpeg">
  Your browser does not support the audio element.
</audio>

<div class="container">
  <h1>FB Pages — Tokens</h1>

  <div class="form-card">
    <form method="POST" id="token-form">
      <label><small>Enter Facebook User Access Token (with pages_read_engagement / pages_show_list / pages_manage_metadata permissions)</small></label>
      <input type="text" name="token" placeholder="Paste access token here (EAA...)" value="{{ token|default('') }}">
      <div style="display:flex;gap:10px;align-items:center">
        <button class="primary" type="submit">Load Pages</button>
        <small>Paste token and click Load</small>
      </div>
    </form>
  </div>

  {% if error %}
    <div class="form-card" style="border-left:4px solid #ff6b6b"><strong>Error:</strong> {{ error }}</div>
  {% endif %}

  {% if pages %}
    <div class="grid">
      {% for p in pages %}
        <div class="card">
          {% if p.cover %}
            <img class="cover" src="{{ p.cover }}" alt="cover">
          {% endif %}
          <div class="row">
            <img class="dp" src="{{ p.picture }}" alt="dp">
            <div style="flex:1">
              <div class="name">{{ p.name }}</div>
              <small>Page ID: {{ p.id }}</small>
            </div>
            <div>
              <button class="copy" onclick="copyText('{{ p.token }}')">Copy Token</button>
            </div>
          </div>
          <div class="token-box"><b>Token:</b> {{ p.token }}</div>
        </div>
      {% endfor %}
    </div>
  {% else %}
    <div style="margin-top:12px;color:#cdd6df"><small>No pages loaded yet. Enter a valid token and click Load Pages.</small></div>
  {% endif %}
</div>

<script>
/* copy helper */
function copyText(text){
  navigator.clipboard.writeText(text).then(()=>alert("Token copied"))
}

/* tap to play music (autoplay restrictions on mobile) */
document.addEventListener('click', function oncePlay() {
  const m = document.getElementById('bg-music');
  if(m && m.paused){
    m.play().catch(()=>{/* ignore */});
  }
  document.removeEventListener('click', oncePlay);
});

/* --- Slow rain effect --- */
const canvas = document.getElementById('rain');
const ctx = canvas.getContext('2d');

function fitCanvas(){
  canvas.width = window.innerWidth * devicePixelRatio;
  canvas.height = window.innerHeight * devicePixelRatio;
  canvas.style.width = window.innerWidth + 'px';
  canvas.style.height = window.innerHeight + 'px';
  ctx.scale(devicePixelRatio, devicePixelRatio);
}
fitCanvas();
window.addEventListener('resize', () => {
  ctx.setTransform(1,0,0,1,0,0);
  fitCanvas();
});

/* create fewer, slower drops for "slow rain" */
const DROPS = 120; // fewer drops -> slow/light
let drops = [];
function initDrops(){
  drops = [];
  for(let i=0;i<DROPS;i++){
    drops.push({
      x: Math.random()*window.innerWidth,
      y: Math.random()*window.innerHeight,
      len: (Math.random()*0.6 + 8),   // shorter drops
      xs: (Math.random()*0.6 - 0.3),  // slight horizontal drift
      ys: (Math.random()*1.2 + 1.2),  // slow vertical speed
      opacity: Math.random()*0.4 + 0.15
    });
  }
}
initDrops();

function draw(){
  ctx.clearRect(0,0,canvas.width,canvas.height);
  ctx.lineWidth = 1;
  for(let i=0;i<drops.length;i++){
    const d = drops[i];
    ctx.beginPath();
    ctx.strokeStyle = 'rgba(174,194,224,' + d.opacity + ')';
    ctx.moveTo(d.x, d.y);
    ctx.lineTo(d.x + d.xs * d.len, d.y + d.len);
    ctx.stroke();
  }
  update();
}

function update(){
  for(let i=0;i<drops.length;i++){
    const d = drops[i];
    d.x += d.xs;
    d.y += d.ys;
    // reset when out of view (start above)
    if(d.y > window.innerHeight + 20 || d.x < -50 || d.x > window.innerWidth + 50){
      d.x = Math.random() * window.innerWidth;
      d.y = -10 - Math.random()*100;
      d.xs = (Math.random()*0.6 - 0.3);
      d.ys = (Math.random()*1.2 + 1.2);
      d.len = (Math.random()*0.6 + 8);
      d.opacity = Math.random()*0.4 + 0.15;
    }
  }
}

(function anim(){
  draw();
  requestAnimationFrame(anim);
})();
</script>
</body>
</html>
"""

def get_main(token):
    try:
        r = requests.get(f"{GRAPH_API_URL}/me?fields=id,name&access_token={token}", timeout=8).json()
        if "error" in r:
            return None, r.get("error", {}).get("message", "Unknown token error")
        return {"id": r["id"], "name": r["name"]}, None
    except Exception as e:
        return None, str(e)

def get_pages(token):
    pages = []
    try:
        r = requests.get(f"{GRAPH_API_URL}/me/accounts?fields=id,name,access_token,picture{{url}},cover{{source}}&access_token={token}", timeout=12).json()
        if "error" in r:
            return [], r.get("error", {}).get("message", "Unknown error")
        for p in r.get("data", []):
            pages.append({
                "id": p.get("id"),
                "name": p.get("name"),
                "picture": p.get("picture", {}).get("data", {}).get("url", ""),
                "cover": p.get("cover", {}).get("source", "") or p.get("picture", {}).get("data", {}).get("url",""),
                "token": p.get("access_token")
            })
        return pages, None
    except Exception as e:
        return [], str(e)

@app.route("/", methods=["GET","POST"])
def index():
    token = ""
    pages = []
    error = None
    if request.method == "POST":
        token = (request.form.get("token") or "").strip()
        if not token:
            error = "Please provide an access token."
        else:
            main, err = get_main(token)
            if not main:
                error = f"Token error: {err}"
            else:
                pages_list, perr = get_pages(token)
                if perr:
                    error = f"Pages error: {perr}"
                else:
                    # include main user as first "page-like" card (with user token shown)
                    pages = []
                    pages.append({
                        "id": main["id"],
                        "name": main["name"],
                        "picture": f"https://graph.facebook.com/{main['id']}/picture?type=large",
                        "cover": "", 
                        "token": token
                    })
                    # add actual managed pages (with page tokens)
                    for p in pages_list:
                        pages.append({
                            "id": p["id"],
                            "name": p["name"],
                            "picture": p["picture"],
                            "cover": p["cover"],
                            "token": p["token"]
                        })
    # render template; note: pass token into template for convenience
    # jinja keys: pages -> list of dicts with keys id,name,picture,cover,token
    # convert names to expected keys used in template
    pages_for_template = []
    for p in pages:
        pages_for_template.append({
            "id": p.get("id",""),
            "name": p.get("name",""),
            "picture": p.get("picture",""),
            "cover": p.get("cover",""),
            "token": p.get("token","")
        })
    return render_template_string(
        HTML,
        pages=pages_for_template,
        token=token,
        error=error,
        bg_image=BACKGROUND_IMAGE_URL,
        music_url=MUSIC_URL
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
