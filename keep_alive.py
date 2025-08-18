from flask import Flask, jsonify
from threading import Thread
import psutil
import os
from waitress import serve  # production server

app = Flask(__name__)

@app.route("/")
def home():
    return "Sharan is running!"

@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "cpu_percent": psutil.cpu_percent(interval=None),  # ✅ non-blocking
        "memory_percent": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage("/").percent,
        "threads": psutil.cpu_count(),
    })


def run():
    port = int(os.environ.get("PORT", 8080))  # Render sets PORT automatically
    serve(app, host="0.0.0.0", port=port)

def keep_alive():
    thread = Thread(target=run, daemon=True)
    thread.start()
