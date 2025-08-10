import base64
import os
import requests
from flask import Flask, request, render_template_string

app = Flask(__name__)

# Background settings
BACKGROUND_IMAGE_URL = "https://i.ibb.co/7JfqXxB/forest-bg.jpg"  # <-- Change to your image URL

# Music file embed (Base64)
with open("music.mp3", "rb") as f:
    MUSIC_BASE64 = base64.b64encode(f.read()).decode()

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>FB Pages — Tokens</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{
  background: #0b0f12 url('{{ bg_image }}') no-repeat center center fixed;
  background-size: cover;
  color: #fff;
  font-family: Arial;
  margin: 0;
  padding: 20px;
  overflow: hidden;
}
.container{max-width:900px;margin:auto;position:relative;z-index:2;}
h1{text-align:center;margin-bottom:20px}
.page-box{
  background:rgba(0,0,0,0.6);
  padding:15px;
  border-radius:10px;
  margin-bottom:20px;
  display:flex;
  align-items:center;
  gap:15px;
}
.page-info img{
  border-radius:8px;
  width:80px;
  height:80px;
  object-fit:cover;
}
.page-info{flex:1}
button{
  padding:8px 12px;
  background:#00bcd4;
  color:#fff;
  border:none;
  border-radius:5px;
  cursor:pointer;
}
canvas{
  position:fixed;
  top:0;
  left:0;
  width:100%;
  height:100%;
  z-index:1;
  pointer-events:none;
}
</style>
<script>
function copyText(text){
  navigator.clipboard.writeText(text).then(()=>alert("Copied to clipboard"));
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

<!-- Rain Canvas -->
<canvas id="rain"></canvas>

<!-- Background Music -->
<audio id="bg-music" loop>
  <source src="data:audio/mpeg;base64,{{ music_data }}" type="audio/mpeg">
</audio>

<div class="container">
  <h1>Facebook Pages — Tokens</h1>
  {% for page in pages %}
  <div class="page-box">
    <div class="page-info">
      <img src="{{ page['cover'] }}" alt="cover">
    </div>
    <div class="page-info">
      <strong>{{ page['name'] }}</strong><br>
      <img src="{{ page['picture'] }}" alt="profile pic" width="50">
    </div>
    <button onclick="copyText('{{ page['access_token'] }}')">Copy Token</button>
  </div>
  {% endfor %}
</div>

<script>
// Heavy rain effect
const canvas = document.getElementById('rain');
const ctx = canvas.getContext('2d');
let drops = [];

function resizeCanvas(){
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
}
window.addEventListener('resize', resizeCanvas);
resizeCanvas();

for(let i=0;i<500;i++){
  drops.push({
    x: Math.random()*canvas.width,
    y: Math.random()*canvas.height,
    l: Math.random()*1+14,
    xs: Math.random()*4-2,
    ys: Math.random()*10+10
  });
}

function draw(){
  ctx.clearRect(0,0,canvas.width,canvas.height);
  ctx.strokeStyle = 'rgba(174,194,224,0.5)';
  ctx.lineWidth = 1;
  ctx.lineCap = 'round';
  for(let i=0;i<drops.length;i++){
    let d = drops[i];
    ctx.beginPath();
    ctx.moveTo(d.x, d.y);
    ctx.lineTo(d.x+d.xs* d.l, d.y+d.l*1);
    ctx.stroke();
  }
  move();
}

function move(){
  for(let i=0;i<drops.length;i++){
    let d = drops[i];
    d.x += d.xs;
    d.y += d.ys;
    if(d.x > canvas.width || d.y > canvas.height){
      d.x = Math.random() * canvas.width;
      d.y = -20;
    }
  }
}

function loop(){
  draw();
  requestAnimationFrame(loop);
}
loop();
</script>

</body>
</html>
"""

@app.route("/")
def index():
    token = request.args.get("token")
    pages = []
    if token:
        r = requests.get(f"https://graph.facebook.com/me/accounts?access_token={token}")
        data = r.json()
        for p in data.get("data", []):
            pid = p['id']
            pic_url = f"https://graph.facebook.com/{pid}/picture?type=large"
            cover_url = ""
            try:
                cover_data = requests.get(
                    f"https://graph.facebook.com/{pid}?fields=cover&access_token={p['access_token']}"
                ).json()
                cover_url = cover_data.get("cover", {}).get("source", "")
            except:
                pass
            pages.append({
                "name": p['name'],
                "picture": pic_url,
                "cover": cover_url or pic_url,
                "access_token": p['access_token']
            })
    return render_template_string(HTML, pages=pages, music_data=MUSIC_BASE64, bg_image=BACKGROUND_IMAGE_URL)

if __name__ == "__main__":
    app.run(debug=True)
