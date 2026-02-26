import cv2
import threading
import queue
from multiprocessing import Queue
from flask import Flask, Response, jsonify, render_template_string
from utils.Logger import Logger
from colorama import Fore

def WebNode(data_queue: Queue, stop_event):
    log = Logger("WEB", Fore.CYAN)
    app = Flask(__name__)

    state = {
        "frames": {},      
        "telemetry": {},   
    }

    def data_processor():
        while not stop_event.is_set():
            try:
                packet = data_queue.get(timeout=0.1)
                p_type = packet.get("type")
                name = packet.get("name")
                value = packet.get("value")

                if p_type == "frame":
                    state["frames"][name] = value
                elif p_type == "telemetry":
                    state["telemetry"][name] = value
            except queue.Empty:
                continue

    def generate_mjpeg(stream_name):
        while not stop_event.is_set():
            frame = state["frames"].get(stream_name)
            if frame is None:
                continue
            ret, buffer = cv2.imencode(".jpg", frame)
            if not ret: continue
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

    @app.route("/")
    def index():
        return render_template_string(HTML_TEMPLATE)

    @app.route("/video/<stream_name>")
    def video_feed(stream_name):
        return Response(generate_mjpeg(stream_name),
                        mimetype='multipart/x-mixed-replace; boundary=frame')

    @app.route("/state")
    def get_state():
        # Enviamos los nombres de las cámaras activas y la telemetría
        return jsonify({
            "streams": list(state["frames"].keys()),
            "telemetry": state["telemetry"]
        })

    threading.Thread(target=data_processor, daemon=True).start()
    log.Info("Dashboard Starfall X running on http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)

# --- UI TEMPLATE BASADA EN TU BOCETO ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Starfall X Console</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --bg-color: #f0f4f8;
            --header-color: #a0d2eb;
            --card-color: #ffffff;
            --accent-blue: #95ccff;
            --text-dark: #333;
        }
        body { font-family: 'Arial', sans-serif; background: var(--bg-color); color: var(--text-dark); margin: 0; padding: 0; overflow-x: hidden; }
        
        /* Header */
        header { 
            background: var(--header-color); padding: 10px 20px; 
            display: flex; justify-content: space-between; align-items: center;
            border-bottom: 2px solid #888; border-radius: 0 0 15px 15px; margin: 0 10px;
        }
        .buttons button { border: none; padding: 8px 25px; border-radius: 8px; font-weight: bold; cursor: pointer; margin-left: 10px; }
        .btn-start { background: #a2f2a2; border: 1px solid #77c777 !important; }
        .btn-stop { background: #ffb3b3; border: 1px solid #e68a8a !important; }

        /* Layout Principal */
        .main-container { display: grid; grid-template-columns: 350px 1fr; gap: 20px; padding: 20px; height: calc(100vh - 100px); }

        /* Columna de Videos */
        .video-sidebar { display: flex; flex-direction: column; gap: 15px; overflow-y: auto; }
        .video-box { background: var(--card-color); border: 2px solid #555; border-radius: 12px; min-height: 200px; position: relative; overflow: hidden; }
        .video-box img { width: 100%; height: 100%; object-fit: cover; }
        .video-label { position: absolute; top: 5px; left: 5px; background: rgba(0,0,0,0.5); color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px; }

        /* Derecha: Telemetria y Graficas */
        .content-area { display: flex; flex-direction: column; gap: 20px; }
        
        /* Grid de Telemetría */
        .telemetry-grid { 
            display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 15px; 
            background: transparent;
        }
        .tele-card { 
            background: var(--accent-blue); padding: 15px; border-radius: 12px; 
            border: 1px solid #77aadd; text-align: center; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
        }
        .tele-card .label { font-size: 0.8em; font-weight: bold; display: block; margin-bottom: 5px; opacity: 0.8; }
        .tele-card .value { font-size: 1.2em; font-weight: bold; }

        /* Sección de Gráficas */
        .graphics-row { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; flex-grow: 1; }
        .chart-container { background: var(--accent-blue); border-radius: 15px; border: 1px solid #77aadd; padding: 15px; min-height: 250px; }
    </style>
</head>
<body>

<header>
    <h1 style="margin:0">Starfall X</h1>
    <div class="buttons">
        <button class="btn-start">start</button>
        <button class="btn-stop">stop</button>
    </div>
</header>

<div class="main-container">
    <div class="video-sidebar" id="video-sidebar">
        </div>

    <div class="content-area">
        <div class="telemetry-grid" id="telemetry-grid">
            </div>

        <div class="graphics-row">
            <div class="chart-container">
                <canvas id="chartError"></canvas>
            </div>
            <div class="chart-container">
                <canvas id="chartCorrection"></canvas>
            </div>
        </div>
    </div>
</div>

<script>
    let activeStreams = [];
    
    function updateUI() {
        fetch('/state')
            .then(res => res.json())
            .then(data => {
                // 1. Manejar Videos Dinámicos
                const videoSidebar = document.getElementById('video-sidebar');
                data.streams.forEach(stream => {
                    if (!activeStreams.includes(stream)) {
                        const div = document.createElement('div');
                        div.className = 'video-box';
                        div.innerHTML = `<span class="video-label">${stream.toUpperCase()}</span>
                                         <img src="/video/${stream}">`;
                        videoSidebar.appendChild(div);
                        activeStreams.push(stream);
                    }
                });

                // 2. Manejar Telemetría Dinámica
                const teleGrid = document.getElementById('telemetry-grid');
                teleGrid.innerHTML = ''; // Limpiar para actualizar
                for (const [key, value] of Object.entries(data.telemetry)) {
                    const card = document.createElement('div');
                    card.className = 'tele-card';
                    card.innerHTML = `<span class="label">${key.replace('_', ' ').toUpperCase()}</span>
                                      <span class="value">${value}</span>`;
                    teleGrid.appendChild(card);
                }
                
                // 3. Actualizar Gráficas (Ejemplo con Error)
                if(data.telemetry.error !== undefined) {
                    updateChart(chartError, data.telemetry.error);
                }
            });
    }

    // Configuración básica de Gráficas
    const ctxError = document.getElementById('chartError').getContext('2d');
    const chartError = new Chart(ctxError, {
        type: 'line',
        data: { labels: [], datasets: [{ label: 'Error de Línea', data: [], borderColor: 'white', tension: 0.4 }] },
        options: { maintainAspectRatio: false, scales: { y: { beginAtZero: false } } }
    });

    function updateChart(chart, newValue) {
        if(chart.data.labels.length > 20) {
            chart.data.labels.shift();
            chart.data.datasets[0].data.shift();
        }
        chart.data.labels.push("");
        chart.data.datasets[0].data.push(newValue);
        chart.update('none'); // Update sin animación para rendimiento
    }

    setInterval(updateUI, 200);
</script>

</body>
</html>
"""