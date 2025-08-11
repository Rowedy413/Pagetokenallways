from flask import Flask, request, send_file, render_template_string
import io

app = Flask(__name__)

# ==== SETTINGS ====
BACKGROUND_IMAGE_URL = "https://i.ibb.co/vCd29NJd/1751604135213.jpg"  # Change this to update background

HTML = """
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>FB Token Extractor</title>
<meta name="viewport" content="width=device-width, initial-scale=1">

<style>
body {
    background: url('{{ bg_url }}') no-repeat center center fixed;
    background-size: cover;
    color: white;
    font-family: Arial, sans-serif;
    text-align: center;
}
.container {
    margin-top: 50px;
    background: rgba(0, 0, 0, 0.6);
    padding: 20px;
    border-radius: 10px;
    display: inline-block;
}
textarea, input[type=file] {
    width: 300px;
    margin: 10px 0;
    padding: 8px;
}
button {
    padding: 10px 20px;
    margin-top: 10px;
    background: #28a745;
    color: white;
    border: none;
    cursor: pointer;
}
#rain {
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    pointer-events: none;
    z-index: 0;
}
</style>
</head>
<body>

<canvas id="rain"></canvas>

<div class="container" style="z-index:1; position: relative;">
    <h2>FB Token Extractor</h2>
    <form method="post" enctype="multipart/form-data">
        <div>
            <label>Single Token:</label><br>
            <textarea name="single_token" rows="3" placeholder="Enter single token here..."></textarea>
        </div>
        <div>
            <label>Upload Token File (.txt):</label><br>
            <input type="file" name="token_file" accept=".txt">
        </div>
        <button type="submit">Process Tokens</button>
    </form>

    {% if tokens %}
        <h3>Clean Tokens ({{ tokens|length }})</h3>
        <textarea rows="10" style="width:300px;">{{ tokens|join('\\n') }}</textarea><br>
        <a href="/download" target="_blank">
            <button>Download tokens.txt</button>
        </a>
    {% endif %}
</div>

<script>
// Slow rain effect
var canvas = document.getElementById('rain');
var ctx = canvas.getContext('2d');
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

var raindrops = [];
for (var i = 0; i < 100; i++) {
    raindrops.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        length: Math.random() * 15 + 10,
        speed: Math.random() * 1 + 0.5
    });
}

function drawRain() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.5)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    for (var i = 0; i < raindrops.length; i++) {
        var drop = raindrops[i];
        ctx.moveTo(drop.x, drop.y);
        ctx.lineTo(drop.x, drop.y + drop.length);
    }
    ctx.stroke();
    moveRain();
}

function moveRain() {
    for (var i = 0; i < raindrops.length; i++) {
        var drop = raindrops[i];
        drop.y += drop.speed;
        if (drop.y > canvas.height) {
            drop.y = -drop.length;
            drop.x = Math.random() * canvas.width;
        }
    }
}

function animateRain() {
    drawRain();
    requestAnimationFrame(animateRain);
}
animateRain();
</script>

</body>
</html>
"""

clean_tokens = []

@app.route("/", methods=["GET", "POST"])
def index():
    global clean_tokens
    clean_tokens = []
    if request.method == "POST":
        tokens_set = set()

        # Single token
        single = request.form.get("single_token", "").strip()
        if single:
            tokens_set.add(single)

        # File upload
        if "token_file" in request.files:
            file = request.files["token_file"]
            if file and file.filename.endswith(".txt"):
                content = file.read().decode("utf-8", errors="ignore")
                for line in content.splitlines():
                    line = line.strip()
                    if line:
                        tokens_set.add(line)

        clean_tokens = sorted(tokens_set)

    return render_template_string(HTML, tokens=clean_tokens, bg_url=BACKGROUND_IMAGE_URL)

@app.route("/download")
def download():
    global clean_tokens
    if not clean_tokens:
        return "No tokens available!", 400
    data = "\n".join(clean_tokens)
    return send_file(io.BytesIO(data.encode()), as_attachment=True, download_name="tokens.txt", mimetype="text/plain")

if __name__ == "__main__":
    app.run(debug=True)
