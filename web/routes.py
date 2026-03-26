from flask import Blueprint, Response, jsonify
import cv2
import time
import os
import shutil

from core import state

web = Blueprint("web", __name__)

# =========================
# VIDEO STREAM
# =========================
def generate_frames():
    while True:
        if state.latest_frame is None:
            continue

        _, buffer = cv2.imencode('.jpg', state.latest_frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


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
# ADD PERSON
# =========================
@web.route("/add_person/<name>")
def add_person(name):

    if not name:
        return {"status": "invalid name"}

    save_path = f"dataset/{name}"
    os.makedirs(save_path, exist_ok=True)

    count = 0
    start_time = time.time()

    while time.time() - start_time < 10:

        if state.latest_frame is None:
            continue

        frame = state.latest_frame.copy()

        filename = f"{save_path}/{int(time.time()*1000)}.jpg"
        cv2.imwrite(filename, frame)

        count += 1
        time.sleep(0.3)

    state.logs.append(f"✅ Added {count} images for {name}")

    # 🔥 reload model
    if state.face_rec:
        state.face_rec.reload()

    return {"status": "done"}


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

        return {"status": "removed"}

    return {"status": "not found"}
