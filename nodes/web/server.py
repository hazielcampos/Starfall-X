import cv2
import time
import queue
from multiprocessing import Queue
from flask import Flask, Response
from utils.Logger import Logger
from colorama import Fore

def WebNode(frame_queue: Queue, stop_event):

    log = Logger("WEB", Fore.CYAN)
    app = Flask(__name__)

    latest_frame = {"frame": None}

    def frame_updater():
        """Thread interno que actualiza el último frame disponible."""
        while not stop_event.is_set():
            try:
                frame = frame_queue.get(timeout=0.1)
                latest_frame["frame"] = frame
            except queue.Empty:
                continue

    def generate():
        """Generador MJPEG."""
        while not stop_event.is_set():
            frame = latest_frame["frame"]

            if frame is None:
                time.sleep(0.01)
                continue

            ret, buffer = cv2.imencode(".jpg", frame)
            if not ret:
                continue

            jpg_bytes = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpg_bytes + b'\r\n')

    @app.route("/")
    def index():
        return """
        <html>
            <head>
                <title>Robot Camera</title>
            </head>
            <body>
                <h1>Live Camera</h1>
                <img src="/video">
            </body>
        </html>
        """

    @app.route("/video")
    def video():
        return Response(generate(),
                        mimetype='multipart/x-mixed-replace; boundary=frame')

    # Lanzamos thread interno para actualizar frames
    import threading
    t = threading.Thread(target=frame_updater, daemon=True)
    t.start()

    log.Info("Starting web server on http://0.0.0.0:5000")

    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
