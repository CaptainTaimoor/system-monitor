from flask import Flask, render_template_string, jsonify
import psutil
import gpustat
import subprocess
import time
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)

# -------- CONFIGURATION --------
EMAIL_FROM = "raotamoorulamin@gmail.com"
EMAIL_TO = "taimooramin1212@gmail.com"
EMAIL_PASSWORD = "ybykhcqnhobfkpcj"  # App password
CPU_LIMIT = 1
MEM_LIMIT = 1
DISK_LIMIT = 1
# -------------------------------

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>⚡ System Monitor Live</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #0d1117; color: #e6edf3; text-align: center; }
        .grid { display: flex; flex-wrap: wrap; justify-content: center; margin-top: 30px; }
        .card { background: #161b22; padding: 20px; border-radius: 15px; width: 230px; margin: 10px; box-shadow: 0 0 10px #000; }
        .metric { font-size: 22px; margin-top: 8px; }
        h1 { color: #00bcd4; }
        .alert { color: #ff4d4d; font-weight: bold; }
        .ok { color: #00bcd4; }
    </style>
</head>
<body>
    <h1>⚙️ System Monitor Live + Alerts</h1>
    <div id="alertBox" class="alert" style="display:none; font-size:18px; margin-bottom:15px;"></div>
    <div class="grid">
        <div class="card"><h3>CPU</h3><div id="cpu" class="metric">--</div></div>
        <div class="card"><h3>Memory</h3><div id="memory" class="metric">--</div></div>
        <div class="card"><h3>Disk</h3><div id="disk" class="metric">--</div></div>
        <div class="card"><h3>Temp</h3><div id="temp" class="metric">--</div></div>
        <div class="card"><h3>Network</h3><div id="net" class="metric">--</div></div>
        <div class="card"><h3>Processes</h3><div id="proc" class="metric">--</div></div>
        <div class="card"><h3>Uptime</h3><div id="uptime" class="metric">--</div></div>
        <div class="card" id="gpuCard" style="display:none"><h3>GPU</h3><div id="gpu" class="metric">--</div></div>
    </div>

    <script>
        async function fetchData() {
            const res = await fetch('/metrics');
            const data = await res.json();

            document.getElementById("cpu").textContent = data.cpu + "%";
            document.getElementById("memory").textContent = data.memory + "%";
            document.getElementById("disk").textContent = data.disk + "%";
            document.getElementById("temp").textContent = data.temp + " °C";
            document.getElementById("net").textContent = data.net.sent + " ↑ / " + data.net.recv + " ↓ MB";
            document.getElementById("proc").textContent = data.processes;
            document.getElementById("uptime").textContent = data.uptime;

            if (data.gpu) {
                document.getElementById("gpu").textContent = data.gpu;
                document.getElementById("gpuCard").style.display = "block";
            } else {
                document.getElementById("gpuCard").style.display = "none";
            }

            const alertBox = document.getElementById("alertBox");
            if (data.alerts.length > 0) {
                alertBox.style.display = "block";
                alertBox.innerHTML = data.alerts.join("<br>");
            } else {
                alertBox.style.display = "none";
            }
        }

        setInterval(fetchData, 1000);
        fetchData();
    </script>
</body>
</html>
"""

def send_email(subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_FROM, EMAIL_PASSWORD)
            server.send_message(msg)
            print("✅ Alert email sent!")
    except Exception as e:
        print("❌ Email failed:", e)

def get_temperature():
    try:
        result = subprocess.run(["sensors"], capture_output=True, text=True)
        for line in result.stdout.split("\n"):
            if "Package id 0" in line or "Tdie" in line:
                return line.split("+")[1].split("°")[0]
    except Exception:
        pass
    return "N/A"

def get_gpu_usage():
    try:
        gpus = gpustat.GPUStatCollection.new_query()
        gpu_info = [f"{gpu.name}: {gpu.utilization}%" for gpu in gpus]
        return ", ".join(gpu_info)
    except Exception:
        return None

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/metrics")
def metrics():
    cpu = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    net_io = psutil.net_io_counters()
    net = {
        "sent": round(net_io.bytes_sent / (1024*1024), 2),
        "recv": round(net_io.bytes_recv / (1024*1024), 2)
    }
    processes = len(psutil.pids())
    uptime = time.strftime("%Hh %Mm %Ss", time.gmtime(time.time() - psutil.boot_time()))
    temp = get_temperature()
    gpu = get_gpu_usage()

    # Alerts
    alerts = []
    if cpu > CPU_LIMIT:
        alerts.append(f"⚠️ High CPU usage: {cpu}%")
    if memory > MEM_LIMIT:
        alerts.append(f"⚠️ High Memory usage: {memory}%")
    if disk > DISK_LIMIT:
        alerts.append(f"⚠️ High Disk usage: {disk}%")

    if alerts:
        send_email("🚨 System Alert!", "\n".join(alerts))

    return jsonify({
        "cpu": cpu,
        "memory": memory,
        "disk": disk,
        "temp": temp,
        "net": net,
        "processes": processes,
        "uptime": uptime,
        "gpu": gpu,
        "alerts": alerts
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

