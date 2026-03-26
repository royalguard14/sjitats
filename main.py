from sensors.pir import PIRSensor
from hardware.alarm import AlarmSystem
from sensors.camera import Camera
from detection.face_recognition import FaceRecognition

from hardware.telegram_bot import TelegramBot
from config.settings_manager import load_settings

from core import state

import time
import threading

# =========================
def add_log(msg):
    print(msg)
    state.logs.append(msg)

# =========================
def run_system():

    pir = PIRSensor()
    alarm = AlarmSystem()
    cam = Camera()
    face_rec = FaceRecognition()
    state.face_rec = face_rec

    add_log("🚀 AI Security System Running...")

    motion_count = 0
    no_motion_count = 0

    known_count = 0
    unknown_count = 0

    motion_active = False
    alert_sent = False

    loop_counter = 0

    while True:

        settings = load_settings()  # 🔥 dynamic load

        if not state.system_armed:
            time.sleep(0.3)
            continue

        # =========================
        # MOTION
        # =========================
        if settings["ENABLE_MOTION"]:
            if pir.detect():
                motion_count += 1
                no_motion_count = 0
            else:
                no_motion_count += 1
                motion_count = 0
        else:
            motion_count = 2  # always active if disabled

        if motion_count >= 2:

            if not motion_active:
                add_log("🚨 Motion confirmed!")
                motion_active = True

            loop_counter += 1
            if loop_counter % 2 != 0:
                continue

            frame = cam.capture_frame()
            if frame is None:
                continue

            state.latest_frame = frame.copy()

            # =========================
            # FACE RECOGNITION
            # =========================
            if settings["ENABLE_FACE_RECOGNITION"]:
                name = face_rec.recognize(frame)
            else:
                name = "Disabled"

            state.latest_name = name
            add_log(f"👁 Detected: {name}")

            if name != "Unknown" and name != "Disabled":
                known_count += 1
                unknown_count = 0
            else:
                unknown_count += 1
                known_count = 0

            if known_count >= 2:
                add_log(f"✅ Authorized: {name}")
                alarm.alarm_off()
                state.alarm_status = False
                alert_sent = False

            elif unknown_count >= 2:
                add_log("🚨 Intruder detected!")
                alarm.alarm_on()
                state.alarm_status = True

                if settings["ENABLE_NOTIFICATIONS"] and not alert_sent:
                    telegram = TelegramBot(
                        settings["TELEGRAM_TOKEN"],
                        settings["TELEGRAM_CHAT_ID"]
                    )

                    threading.Thread(
                        target=lambda: (
                            telegram.send_message("🚨 Intruder detected!"),
                            telegram.send_image(frame)
                        )
                    ).start()

                    alert_sent = True

        if motion_active and no_motion_count >= 100:
            add_log("😴 System reset")
            motion_active = False
            known_count = 0
            unknown_count = 0
            alert_sent = False

            alarm.alarm_off()
            state.alarm_status = False

        time.sleep(0.1)

# =========================
def start_system():
    threading.Thread(target=run_system, daemon=True).start()