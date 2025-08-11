import os
import requests
from flask import Flask, request, render_template_string, send_file
from io import BytesIO

app = Flask(__name__)

BACKGROUND_IMAGE_URL = "https://i.ibb.co/vCd29NJd/1751604135213.jpg"

HTML = """
<!doctype html>
<html>
<head>
<title>FB Token & Pages</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body {
    background: url('{{ bg_url }}') no-repeat center center fixed;
    background-size: cover;
    font-family: Arial, sans-serif;
    color: white;
    text-align: center;
}
.container {
    background: rgba(0, 0, 0, 0.5);
    padding: 20px;
    border-radius: 12px;
    display: inline-block;
    margin-top: 50px;
}
input, button {
    padding: 8px;
    margin: 5px;
    border-radius: 6px;
    border: none;
}
.page-box {
    background: rgba(255,255,255,0.1);
    margin: 10px;
    padding: 10px;
    border-radius: 10px;
}
.page-box img {
    border-radius: 50%;
}
.download-btn {
    background: green;
    color: white;
    cursor: pointer;
}
</style>
</head>
<body>

<canvas id="rainCanvas"></canvas>

<div class="container">
<h2>Facebook Token & Page Tool</h2>
<form method="POST" enctype="multipart/form-data">
    <textarea name="single_token" placeholder="Enter single token here" rows="3" cols="40"></textarea><br>
    <input type="file" name="token_file"><br>
    <button type="submit">Fetch Pages</button>
</form>

{% if tokens %}
    <h3>User Tokens</h3>
    <button onclick="window.location.href='/download_tokens'">Download tokens.txt</button>
{% endif %}

{% if page_tokens %}
    <h3>Page Tokens</h3>
    <button onclick="window.location.href='/download_page_tokens'">Download page_tokens.txt</button>
{% endif %}

{% for token, pages in results.items() %}
    <div class="page-box">
        <h4>User Token: {{ token[:20] }}...</h4>
        {% if pages %}
            {% for p in pages %}
                <div>
                    <img src="{{ p['picture'] }}" width="40">
                    <b>{{ p['name'] }}</b><br>
                    <small>{{ p['access_token'] }}</small>
                </div>
                <hr>
            {% endfor %}
        {% else %}
            <p>No pages found</p>
        {% endif %}
    </div>
{% endfor %}
</div>

<script>
// Slow rain effect
var canvas = document.getElementById('rainCanvas');
var ctx = canvas.getContext('2d');
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;
var raindrops = [];
for (var i = 0; i < 100; i++) {
    raindrops.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        length: Math.random() * 20 + 10,
        speed: Math.random() * 2 + 0.5
    });
}
function drawRain() {
    ctx.clearRect(0,0,canvas.width,canvas.height);
    ctx.strokeStyle = 'rgba(174,194,224,0.5)';
    ctx.lineWidth = 1;
    for (var i = 0; i < raindrops.length; i++) {
        var drop = raindrops[i];
        ctx.beginPath();
        ctx.moveTo(drop.x, drop.y);
        ctx.lineTo(drop.x, drop.y + drop.length);
        ctx.stroke();
        drop.y += drop.speed;
        if (drop.y > canvas.height) {
            drop.y = -drop.length;
            drop.x = Math.random() * canvas.width;
        }
    }
    requestAnimationFrame(drawRain);
}
drawRain();
</script>

</body>
</html>
"""

user_tokens = []
page_tokens = []

@app.route("/", methods=["GET", "POST"])
def index():
    global user_tokens, page_tokens
    results = {}
    if request.method == "POST":
        tokens = set()

        # Single token
        single_token = request.form.get("single_token", "").strip()
        if single_token:
            tokens.add(single_token)

        # File tokens
        if "token_file" in request.files:
            file = request.files["token_file"]
            if file:
                for line in file.read().decode().splitlines():
                    if line.strip():
                        tokens.add(line.strip())

        user_tokens = list(tokens)
        page_tokens = []

        for token in user_tokens:
            try:
                url = f"https://graph.facebook.com/v20.0/me/accounts?fields=id,name,picture,access_token&access_token={token}"
                data = requests.get(url).json().get("data", [])
                pages = []
                for p in data:
                    pages.append({
                        "name": p.get("name"),
                        "picture": p.get("picture", {}).get("data", {}).get("url", ""),
                        "access_token": p.get("access_token", "")
                    })
                    if p.get("access_token"):
                        page_tokens.append(p["access_token"])
                results[token] = pages
            except:
                results[token] = []

    return render_template_string(HTML, results=results, tokens=user_tokens, page_tokens=page_tokens, bg_url=BACKGROUND_IMAGE_URL)

@app.route("/download_tokens")
def download_tokens():
    global user_tokens
    buf = BytesIO("\n".join(user_tokens).encode())
    return send_file(buf, as_attachment=True, download_name="tokens.txt", mimetype="text/plain")

@app.route("/download_page_tokens")
def download_page_tokens():
    global page_tokens
    buf = BytesIO("\n".join(page_tokens).encode())
    return send_file(buf, as_attachment=True, download_name="page_tokens.txt", mimetype="text/plain")

if __name__ == "__main__":
    app.run(debug=True)
