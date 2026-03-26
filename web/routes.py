from flask import Blueprint, Response, jsonify, render_template, request
import cv2
import time
import os
import shutil
import threading

from core import state
from config.settings_manager import load_settings, update_settings

web = Blueprint("web", __name__)

# =========================
@web.route("/")
def index():
    people = os.listdir("known_faces")
    return render_template("index.html", known_people=people)

# =========================
def generate_frames():
    while True:
        if state.latest_frame is None:
            time.sleep(0.05)
            continue

        frame = state.latest_frame.copy()

        if state.latest_name:
            cv2.putText(frame, state.latest_name, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        _, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' +
               buffer.tobytes() + b'\r\n')

        time.sleep(0.03)

@web.route("/video")
def video():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# =========================
@web.route("/logs")
def logs():
    return jsonify(state.logs[-50:])

# =========================
@web.route("/status")
def status():
    return jsonify({
        "name": state.latest_name,
        "armed": state.system_armed,
        "alarm": state.alarm_status
    })

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
    return jsonify(load_settings())

@web.route("/update_settings", methods=["POST"])
def save_settings():
    data = request.json
    update_settings(data)
    return jsonify({"status": "saved"})

# =========================
# ADD PERSON
# =========================
@web.route("/add_person", methods=["POST"])
def add_person():
    name = request.form.get("name")

    path = f"known_faces/{name}"
    os.makedirs(path, exist_ok=True)

    def capture():
        start = time.time()
        while time.time() - start < 10:
            if state.latest_frame is None:
                continue
            cv2.imwrite(f"{path}/{int(time.time()*1000)}.jpg",
                        state.latest_frame)
            time.sleep(0.3)

        state.face_rec.load_known_faces()

    threading.Thread(target=capture).start()
    return jsonify({"status": "capturing"})

# =========================
@web.route("/remove_person/<name>")
def remove_person(name):
    path = f"known_faces/{name}"
    if os.path.exists(path):
        shutil.rmtree(path)
        state.face_rec.load_known_faces()
    return jsonify({"status": "removed"})