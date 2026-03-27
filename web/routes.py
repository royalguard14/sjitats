from flask import Blueprint, Response, jsonify, render_template, request
import cv2
import time
import os
import shutil
import threading

from core import state
from config.settings_manager import load_settings, update_settings

web = Blueprint("web", __name__)

KNOWN_FACES_DIR = "known_faces"

# =========================
# HOME
# =========================
@web.route("/")
def index():
    if not os.path.exists(KNOWN_FACES_DIR):
        os.makedirs(KNOWN_FACES_DIR)

    people = sorted([
        d for d in os.listdir(KNOWN_FACES_DIR)
        if os.path.isdir(os.path.join(KNOWN_FACES_DIR, d))
    ])

    return render_template("index.html", known_people=people)

# =========================
# VIDEO STREAM
# =========================
def generate_frames():
    while True:
        if state.latest_frame is None:
            time.sleep(0.05)
            continue

        frame = state.latest_frame.copy()

        if state.latest_name:
            cv2.putText(
                frame,
                state.latest_name,
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

        _, buffer = cv2.imencode('.jpg', frame)

        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' +
               buffer.tobytes() + b'\r\n')

        time.sleep(0.03)

@web.route("/video")
def video():
    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

# =========================
# LOGS
# =========================
@web.route("/logs")
def logs():
    return jsonify(state.logs[-50:])

# =========================
# STATUS
# =========================
@web.route("/status")
def status():
    return jsonify({
        "name": state.latest_name,
        "armed": state.system_armed,
        "alarm": state.alarm_status
    })

# =========================
# ARM / DISARM
# =========================
@web.route("/arm")
def arm():
    state.system_armed = True
    return jsonify({"status": "armed"})

@web.route("/disarm")
def disarm():
    state.system_armed = False
    return jsonify({"status": "disarmed"})

# =========================
# SETTINGS
# =========================
@web.route("/settings")
def get_settings():
    try:
        return jsonify(load_settings())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@web.route("/update_settings", methods=["POST"])
def save_settings():
    data = request.json

    if not data:
        return jsonify({"error": "Invalid data"}), 400

    update_settings(data)

    return jsonify({"status": "saved"})

# =========================
# ADD PERSON
# =========================
@web.route("/add_person", methods=["POST"])
def add_person():
    name = request.form.get("name", "").strip()

    if not name:
        return jsonify({"error": "Invalid name"}), 400

    path = os.path.join(KNOWN_FACES_DIR, name)
    os.makedirs(path, exist_ok=True)

    def capture():
        start = time.time()

        while time.time() - start < 10:
            if state.latest_frame is None:
                continue

            filename = f"{int(time.time()*1000)}.jpg"
            filepath = os.path.join(path, filename)

            cv2.imwrite(filepath, state.latest_frame)
            time.sleep(0.3)

        # reload in background
        threading.Thread(target=state.face_rec.load_known_faces).start()

    threading.Thread(target=capture, daemon=True).start()

    return jsonify({"status": "capturing"})

# =========================
# REMOVE PERSON
# =========================
@web.route("/remove_person/<name>")
def remove_person(name):
    path = os.path.join(KNOWN_FACES_DIR, name)

    if os.path.exists(path):
        shutil.rmtree(path)

        # FORCE FULL RELOAD
        state.face_rec = FaceRecognition()

        return jsonify({"status": "removed"})

    return jsonify({"error": "Not found"}), 404
