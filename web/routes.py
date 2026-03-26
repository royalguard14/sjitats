from flask import Blueprint, Response, render_template, jsonify
import cv2

from core import state

web = Blueprint('web', __name__)

# =========================
# VIDEO STREAM
# =========================
def generate():
    while True:
        if state.latest_frame is None:
            continue

        _, buffer = cv2.imencode('.jpg', state.latest_frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# =========================
# ROUTES
# =========================
@web.route("/")
def index():
    return render_template(
        "index.html",
        name=state.latest_name,
        logs=state.logs[-10:]
    )

@web.route("/video")
def video():
    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@web.route("/logs")
def get_logs():
    return jsonify(state.logs[-10:])


@web.route("/status")
def status():
    return jsonify({
        "name": state.latest_name,
        "armed": state.system_armed,
        "alarm": state.alarm_status
    })