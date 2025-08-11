import os
import requests
from flask import Flask, request, render_template_string, send_file
from io import BytesIO

app = Flask(__name__)

BACKGROUND_IMAGE_URL = "https://i.ibb.co/vCd29NJd/1751604135213.jpg"  # Change as needed

HTML_TEMPLATE = """
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>ROWDY KINNG - Facebook Token & Page Viewer</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
    body {
        margin: 0; 
        font-family: Arial, sans-serif; 
        background: url('{{ background_url }}') no-repeat center center fixed;
        background-size: cover;
        color: white; 
        text-align: center;
    }
    header {
        background: rgba(0, 0, 0, 0.6);
        padding: 15px;
        font-size: 28px;
        font-weight: bold;
        letter-spacing: 2px;
    }
    footer {
        background: rgba(0, 0, 0, 0.6);
        padding: 10px;
        font-size: 14px;
        font-style: italic;
        margin-top: 20px;
    }
    .token-box {
        background: rgba(0,0,0,0.5);
        margin: 10px auto;
        padding: 10px;
        border-radius: 10px;
        width: 95%;
        max-width: 500px;
    }
    img {
        border-radius: 50%;
        margin: 5px;
    }
    .download-btn {
        background: #28a745;
        color: white;
        padding: 10px 15px;
        margin: 10px;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        font-size: 14px;
    }
    textarea {
        width: 90%;
        height: 100px;
        border-radius: 5px;
        padding: 10px;
    }
    canvas {
        position: fixed;
        top: 0;
        left: 0;
        pointer-events: none;
    }
</style>
</head>
<body>
<canvas id="rain"></canvas>
<header>ROWDY KINNG</header>

<h3>Enter Single Token or Upload Token File</h3>
<form method="post" enctype="multipart/form-data">
    <textarea name="single_token" placeholder="Enter a single token..."></textarea><br><br>
    OR<br><br>
    <input type="file" name="token_file"><br><br>
    <button class="download-btn" type="submit">Get Pages & Tokens</button>
</form>

{% if results %}
    <h3>Results</h3>
    <button class="download-btn" onclick="window.location.href='/download/all_tokens'">Download All Main Tokens</button>
    <button class="download-btn" onclick="window.location.href='/download/page_tokens'">Download All Page Tokens</button>

    {% for user in results %}
        <div class="token-box">
            <img src="{{ user['picture'] }}" width="80" height="80"><br>
            <b>{{ user['name'] }}</b><br>
            <small>{{ user['token'] }}</small>
        </div>
        {% if user['pages'] %}
            {% for page in user['pages'] %}
                <div class="token-box">
                    <img src="{{ page['picture'] }}" width="50" height="50"><br>
                    {{ page['name'] }}<br>
                    <small>{{ page['token'] }}</small>
                </div>
            {% endfor %}
        {% endif %}
    {% endfor %}
{% endif %}

<footer>Developed by ROWDY KINNG</footer>

<script>
// Fast Rain Effect
const canvas = document.getElementById('rain');
const ctx = canvas.getContext('2d');
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

let drops = [];
for (let i = 0; i < 200; i++) {
    drops.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        l: Math.random() * 1,
        xs: -4 + Math.random() * 4,
        ys: 10 + Math.random() * 10
    });
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.strokeStyle = 'rgba(174,194,224,0.5)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    for (let i = 0; i < drops.length; i++) {
        let d = drops[i];
        ctx.moveTo(d.x, d.y);
        ctx.lineTo(d.x + d.l * d.xs, d.y + d.l * d.ys);
    }
    ctx.stroke();
    move();
}

function move() {
    for (let i = 0; i < drops.length; i++) {
        let d = drops[i];
        d.x += d.xs;
        d.y += d.ys;
        if (d.x > canvas.width || d.y > canvas.height) {
            d.x = Math.random() * canvas.width;
            d.y = -20;
        }
    }
}

setInterval(draw, 15);
</script>
</body>
</html>
"""

# Store tokens for download
ALL_TOKENS = []
PAGE_TOKENS = []

def fetch_user_info(token):
    try:
        url = f"https://graph.facebook.com/v20.0/me?fields=id,name,picture&access_token={token}"
        r = requests.get(url).json()
        if "error" in r:
            return None
        return {
            "name": r["name"],
            "picture": r["picture"]["data"]["url"],
            "token": token
        }
    except:
        return None

def fetch_pages(token):
    try:
        url = f"https://graph.facebook.com/v20.0/me/accounts?fields=id,name,picture&access_token={token}"
        r = requests.get(url).json()
        pages = []
        if "data" in r:
            for p in r["data"]:
                pages.append({
                    "name": p["name"],
                    "picture": p["picture"]["data"]["url"],
                    "token": p["access_token"]
                })
        return pages
    except:
        return []

@app.route("/", methods=["GET", "POST"])
def index():
    global ALL_TOKENS, PAGE_TOKENS
    ALL_TOKENS, PAGE_TOKENS = [], []
    results = []

    if request.method == "POST":
        tokens = []

        # Single token
        single_token = request.form.get("single_token", "").strip()
        if single_token:
            tokens.append(single_token)

        # File tokens
        token_file = request.files.get("token_file")
        if token_file:
            file_tokens = token_file.read().decode().splitlines()
            tokens.extend(file_tokens)

        # Remove duplicates & empty
        tokens = list(set([t.strip() for t in tokens if t.strip()]))

        for token in tokens:
            user = fetch_user_info(token)
            if user:
                ALL_TOKENS.append(token)
                user_pages = fetch_pages(token)
                for p in user_pages:
                    PAGE_TOKENS.append(p["token"])
                user["pages"] = user_pages
                results.append(user)

    return render_template_string(HTML_TEMPLATE, background_url=BACKGROUND_IMAGE_URL, results=results)

@app.route("/download/<filetype>")
def download(filetype):
    data = []
    filename = "tokens.txt"
    if filetype == "all_tokens":
        data = ALL_TOKENS
        filename = "tokens.txt"
    elif filetype == "page_tokens":
        data = PAGE_TOKENS
        filename = "page_tokens.txt"

    buffer = BytesIO("\n".join(data).encode())
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=filename, mimetype="text/plain")

if __name__ == "__main__":
    app.run(debug=True)
