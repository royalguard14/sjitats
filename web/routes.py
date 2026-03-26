from flask import Blueprint, Response, jsonify, render_template, request
import cv2
import os
import shutil
import time
import threading

from core import state

web = Blueprint("web", __name__)

# =========================
# HOME PAGE
# =========================
@web.route("/")
def index():
    # List all known people
    known_people = os.listdir("known_faces")
    return render_template("index.html", known_people=known_people)


# =========================
# VIDEO STREAM
# =========================
def generate_frames():
    while True:
        if state.latest_frame is None:
            time.sleep(0.05)
            continue

        frame = state.latest_frame.copy()
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

        time.sleep(0.03)  # prevent CPU overload


@web.route("/video")
def video():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


# =========================
# LOGS
# =========================
@web.route("/logs")
def get_logs():
    return jsonify(state.logs[-50:])  # last 50 logs


# =========================
# ADD PERSON
# =========================
@web.route("/add_person", methods=["POST"])
def add_person():
    name = request.form.get("name", "").strip()

    if not name:
        return jsonify({"status": "invalid name"})

    save_path = os.path.join("known_faces", name)
    os.makedirs(save_path, exist_ok=True)

    def capture_faces():
        count = 0
        start_time = time.time()
        while time.time() - start_time < 10:
            if state.latest_frame is None:
                time.sleep(0.1)
                continue
            frame = state.latest_frame.copy()
            filename = f"{save_path}/{int(time.time()*1000)}.jpg"
            cv2.imwrite(filename, frame)
            count += 1
            time.sleep(0.3)

        state.logs.append(f"✅ Added {count} images for {name}")
        if state.face_rec:
            state.face_rec.load_known_faces("known_faces")

    threading.Thread(target=capture_faces).start()
    return jsonify({"status": "recording started"})


# =========================
# REMOVE PERSON
# =========================
@web.route("/remove_person/<name>")
def remove_person(name):
    path = os.path.join("known_faces", name)
    if os.path.exists(path):
        shutil.rmtree(path)
        state.logs.append(f"❌ Removed {name}")
        if state.face_rec:
            state.face_rec.load_known_faces("known_faces")
        return jsonify({"status": "removed"})
    return jsonify({"status": "not found"})
