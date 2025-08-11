from flask import Flask, request, send_file, render_template_string
import requests, io

app = Flask(__name__)

BACKGROUND_IMAGE_URL = "https://i.ibb.co/vCd29NJd/1751604135213.jpg"

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>ROWDY KINNG - Token Tool</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
    body {
        margin: 0; padding: 0;
        font-family: Arial, sans-serif;
        background: url('{{ bg }}') no-repeat center center fixed;
        background-size: cover;
        color: white;
        text-align: center;
    }
    header {
        font-size: 2em;
        font-weight: bold;
        padding: 20px;
        background: rgba(0,0,0,0.6);
    }
    footer {
        padding: 10px;
        font-size: 0.9em;
        background: rgba(0,0,0,0.5);
        margin-top: 20px;
    }
    .profile, .page {
        background: rgba(0,0,0,0.6);
        margin: 15px auto;
        padding: 15px;
        border-radius: 10px;
        max-width: 400px;
    }
    img {
        border-radius: 50%;
        width: 80px; height: 80px;
    }
    .token {
        background: rgba(255,255,255,0.1);
        padding: 5px;
        word-wrap: break-word;
        margin-top: 5px;
        border-radius: 5px;
    }
    .download-btn {
        display: inline-block;
        padding: 10px;
        margin: 5px;
        background: limegreen;
        color: black;
        border-radius: 5px;
        text-decoration: none;
    }
    canvas {
        position: fixed;
        top: 0; left: 0;
        pointer-events: none;
        z-index: 999;
    }
</style>
</head>
<body>

<header>ROWDY KINNG</header>

<h3>Enter Token or Upload File</h3>
<form method="post" enctype="multipart/form-data">
    <input type="text" name="token" placeholder="Enter Access Token">
    <br><br>
    <input type="file" name="file">
    <br><br>
    <button type="submit">Submit</button>
</form>

{% if users %}
    <a href="/download/tokens" class="download-btn">Download All Tokens</a>
    <a href="/download/page_tokens" class="download-btn">Download Page Tokens</a>
    {% for user in users %}
        <div class="profile">
            <img src="{{ user.picture }}">
            <h3>{{ user.name }}</h3>
            <div class="token">{{ user.token }}</div>
        </div>
        {% for page in user.pages %}
            <div class="page">
                <img src="{{ page.picture }}">
                <h4>{{ page.name }}</h4>
                <div class="token">{{ page.token }}</div>
            </div>
        {% endfor %}
    {% endfor %}
{% endif %}

<footer>Developed by ROWDY KINNG</footer>

<canvas id="rain"></canvas>
<script>
var canvas = document.getElementById('rain');
var ctx = canvas.getContext('2d');
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;
var drops = [];
for(var i=0;i<500;i++){
    drops.push({x: Math.random()*canvas.width, y: Math.random()*canvas.height, l: Math.random()*1, xs: -4+Math.random()*4+2, ys: Math.random()*10+15});
}
function draw(){
    ctx.clearRect(0,0,canvas.width,canvas.height);
    ctx.strokeStyle = 'rgba(174,194,224,0.5)';
    ctx.lineWidth = 1;
    ctx.lineCap = 'round';
    for(var i=0;i<drops.length;i++){
        var d = drops[i];
        ctx.beginPath();
        ctx.moveTo(d.x, d.y);
        ctx.lineTo(d.x+d.l*d.xs, d.y+d.l*d.ys);
        ctx.stroke();
    }
    move();
}
function move(){
    for(var i=0;i<drops.length;i++){
        var d = drops[i];
        d.x += d.xs;
        d.y += d.ys;
        if(d.x > canvas.width || d.y > canvas.height){
            d.x = Math.random()*canvas.width;
            d.y = -20;
        }
    }
}
setInterval(draw, 20);
</script>

</body>
</html>
"""

all_tokens = []
page_tokens = []

@app.route("/", methods=["GET", "POST"])
def index():
    global all_tokens, page_tokens
    users = []
    if request.method == "POST":
        tokens = []
        if request.form.get("token"):
            tokens.append(request.form.get("token").strip())
        if "file" in request.files and request.files["file"].filename:
            file_tokens = request.files["file"].read().decode().splitlines()
            tokens.extend([t.strip() for t in file_tokens if t.strip()])
        tokens = list(set(tokens))  # remove duplicates
        all_tokens = tokens
        page_tokens.clear()

        for token in tokens:
            try:
                u = requests.get(f"https://graph.facebook.com/v20.0/me?fields=id,name,picture&access_token={token}").json()
                if "error" in u: 
                    continue
                pages_data = requests.get(f"https://graph.facebook.com/v20.0/me/accounts?fields=id,name,picture&access_token={token}").json()
                pages = []
                if "data" in pages_data:
                    for p in pages_data["data"]:
                        page_tokens.append(p["access_token"])
                        pages.append({
                            "name": p["name"],
                            "picture": p["picture"]["data"]["url"],
                            "token": p["access_token"]
                        })
                users.append({
                    "name": u["name"],
                    "picture": u["picture"]["data"]["url"],
                    "token": token,
                    "pages": pages
                })
            except:
                continue
    return render_template_string(HTML, users=users, bg=BACKGROUND_IMAGE_URL)

@app.route("/download/<dtype>")
def download(dtype):
    if dtype == "tokens":
        data = "\n".join(all_tokens)
    elif dtype == "page_tokens":
        data = "\n".join(page_tokens)
    else:
        data = ""
    buf = io.BytesIO()
    buf.write(data.encode())
    buf.seek(0)
    return send_file(buf, as_attachment=True, download_name=f"{dtype}.txt")

if __name__ == "__main__":
    app.run(debug=True)
