from flask import Blueprint, Response, jsonify, render_template
import cv2
import time
import os
import shutil

from core import state

web = Blueprint("web", __name__)

# =========================
# HOME PAGE
# =========================
@web.route("/")
def index():
    return render_template("index.html")


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

        time.sleep(0.03)  # 🔥 prevent CPU overload


@web.route("/video")
def video():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


# =========================
# LOGS
# =========================
@web.route("/logs")
def get_logs():
    return jsonify(state.logs[-10:])


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
    state.logs.append("🟢 System ARMED")
    return jsonify({"status": "armed"})


@web.route("/disarm")
def disarm():
    state.system_armed = False
    state.logs.append("🔴 System DISARMED")
    return jsonify({"status": "disarmed"})


# =========================
# ADD PERSON (NON-BLOCKING FIX)
# =========================
@web.route("/add_person/<name>")
def add_person(name):

    if not name.strip():
        return jsonify({"status": "invalid name"})

    save_path = f"dataset/{name}"
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
            state.face_rec.reload()

    # 🔥 run in background (IMPORTANT FIX)
    import threading
    threading.Thread(target=capture_faces).start()

    return jsonify({"status": "recording started"})


# =========================
# REMOVE PERSON
# =========================
@web.route("/remove_person/<name>")
def remove_person(name):

    path = f"dataset/{name}"

    if os.path.exists(path):
        shutil.rmtree(path)
        state.logs.append(f"❌ Removed {name}")

        if state.face_rec:
            state.face_rec.reload()

        return jsonify({"status": "removed"})

    return jsonify({"status": "not found"})
