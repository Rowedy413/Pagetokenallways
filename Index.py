import os
import requests
from flask import Flask, request, render_template_string, send_file
from io import BytesIO

app = Flask(__name__)

# ==== SETTINGS ====
BACKGROUND_IMAGE_URL = "https://i.ibb.co/vCd29NJd/1751604135213.jpg"  # Change here

# ====== HTML TEMPLATE ======
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>FB Token Checker</title>
    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
            color: white;
            background: url('{{ bg_url }}') no-repeat center center fixed;
            background-size: cover;
            overflow-y: scroll;
        }
        .rain {
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            pointer-events: none;
            background-image: url('https://i.ibb.co/F6XcbLQ/rain-light.png');
            animation: rain 0.5s linear infinite;
            opacity: 0.3;
        }
        @keyframes rain {
            from {background-position: 0 0;}
            to {background-position: 20% 100%;}
        }
        .container {
            background: rgba(0,0,0,0.6);
            padding: 20px;
            margin: 20px auto;
            max-width: 800px;
            border-radius: 10px;
        }
        input, button {
            padding: 8px;
            margin: 5px 0;
            width: 100%;
            border: none;
            border-radius: 5px;
        }
        button {
            background: #4CAF50;
            color: white;
            cursor: pointer;
        }
        img { border-radius: 50%; }
        .token-box { background: rgba(255,255,255,0.1); padding: 10px; margin: 5px 0; border-radius: 5px; }
    </style>
</head>
<body>
<div class="rain"></div>

<div class="container">
    <h2>Single Token Checker</h2>
    <form method="POST" enctype="multipart/form-data" action="/check_single">
        <input type="text" name="token" placeholder="Enter Facebook Token" required>
        <button type="submit">Check Token</button>
    </form>
    {% if single_result is defined %}
        <div>{{ single_result }}</div>
    {% endif %}
</div>

<div class="container">
    <h2>Multiple Tokens Checker (Upload TXT)</h2>
    <form method="POST" enctype="multipart/form-data" action="/check_multiple">
        <input type="file" name="file" accept=".txt" required>
        <button type="submit">Check Tokens</button>
    </form>
    {% if multiple_results is defined %}
        <h3>Valid Tokens:</h3>
        {% for token in valid_tokens %}
            <div class="token-box">{{ token }}</div>
        {% endfor %}
        {% if valid_tokens %}
            <a href="/download_valid" style="color:yellow;">Download valid_tokens.txt</a>
        {% endif %}
    {% endif %}
</div>

<div class="container">
    <h2>Valid Tokens → All Pages Extract</h2>
    <form method="POST" action="/extract_pages">
        <button type="submit">Extract Pages</button>
    </form>
    {% if pages_data is defined %}
        {% for page in pages_data %}
            <div class="token-box">
                <img src="{{ page.picture }}" width="40" height="40">
                <b>{{ page.name }}</b><br>
                Token: {{ page.token }}
            </div>
        {% endfor %}
        {% if pages_data %}
            <a href="/download_pages" style="color:yellow;">Download pages_tokens.txt</a>
        {% endif %}
    {% endif %}
</div>

</body>
</html>
"""

valid_tokens_global = []
pages_tokens_global = []

# ====== ROUTES ======

@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML_TEMPLATE, bg_url=BACKGROUND_IMAGE_URL)

@app.route("/check_single", methods=["POST"])
def check_single():
    token = request.form.get("token")
    if is_token_valid(token):
        result = f"<span style='color:lightgreen;'>Valid Token ✅</span>"
    else:
        result = f"<span style='color:red;'>Invalid Token ❌</span>"
    return render_template_string(HTML_TEMPLATE, bg_url=BACKGROUND_IMAGE_URL, single_result=result)

@app.route("/check_multiple", methods=["POST"])
def check_multiple():
    global valid_tokens_global
    file = request.files["file"]
    tokens = file.read().decode().splitlines()
    valid_tokens_global = [t for t in tokens if is_token_valid(t)]
    return render_template_string(HTML_TEMPLATE, bg_url=BACKGROUND_IMAGE_URL,
                                  multiple_results=True, valid_tokens=valid_tokens_global)

@app.route("/extract_pages", methods=["POST"])
def extract_pages():
    global pages_tokens_global
    pages_tokens_global.clear()
    pages_data = []
    for token in valid_tokens_global:
        try:
            r = requests.get(
                f"https://graph.facebook.com/me/accounts?fields=id,name,picture,access_token&access_token={token}"
            ).json()
            if "data" in r:
                for page in r["data"]:
                    pages_tokens_global.append(page["access_token"])
                    pages_data.append({
                        "name": page["name"],
                        "picture": page["picture"]["data"]["url"],
                        "token": page["access_token"]
                    })
        except:
            pass
    return render_template_string(HTML_TEMPLATE, bg_url=BACKGROUND_IMAGE_URL, pages_data=pages_data)

@app.route("/download_valid")
def download_valid():
    output = BytesIO("\n".join(valid_tokens_global).encode())
    return send_file(output, mimetype="text/plain", as_attachment=True, download_name="valid_tokens.txt")

@app.route("/download_pages")
def download_pages():
    output = BytesIO("\n".join(pages_tokens_global).encode())
    return send_file(output, mimetype="text/plain", as_attachment=True, download_name="pages_tokens.txt")

# ====== TOKEN VALIDATOR ======
def is_token_valid(token):
    try:
        r = requests.get(f"https://graph.facebook.com/me?access_token={token}").json()
        return "id" in r
    except:
        return False

# ==== Vercel handler ====
def handler(event, context):
    return app(event, context)

if __name__ == "__main__":
    app.run(debug=True)
