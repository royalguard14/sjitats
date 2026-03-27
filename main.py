from sensors.pir import PIRSensor
from hardware.alarm import AlarmSystem
from sensors.camera import Camera
from detection.face_recognition import FaceRecognition
from utils.confusion_matrix_logger import log_result

from hardware.telegram_bot import TelegramBot
from config.settings_manager import load_settings

from core import state

import time
import threading

# =========================
# LOG FUNCTION
# =========================
def add_log(msg):
    print(msg)
    state.logs.append(msg)

# =========================
# MAIN SYSTEM
# =========================
def run_system():

    pir = PIRSensor()
    alarm = AlarmSystem()
    cam = Camera()
    face_rec = FaceRecognition()

    state.face_rec = face_rec

    # ✅ Load settings ONCE
    settings = load_settings()

    # ✅ Create telegram ONCE
    telegram = None
    if settings["ENABLE_NOTIFICATIONS"]:
        telegram = TelegramBot(
            settings["TELEGRAM_TOKEN"],
            settings["TELEGRAM_CHAT_ID"]
        )

    add_log("🚀 AI Security System Running...")

    motion_count = 0
    no_motion_count = 0

    known_count = 0
    unknown_count = 0

    motion_active = False
    alert_sent = False

    loop_counter = 0
    PROCESS_EVERY = 2  # controls speed

    while True:

        # =========================
        # Reload settings occasionally
        # =========================
        if loop_counter % 10 == 0:
            settings = load_settings()

        if not state.system_armed:
            time.sleep(0.3)
            continue

        # =========================
        # MOTION DETECTION
        # =========================
        if settings["ENABLE_MOTION"]:

            if pir.detect():
                motion_count += 1
                no_motion_count = 0
            else:
                no_motion_count += 1
                motion_count = 0
        else:
            motion_count = 2  # force active

        # =========================
        # MOTION CONFIRMED
        # =========================
        if motion_count >= 2:

            if not motion_active:
                add_log("🚨 Motion confirmed!")
                motion_active = True

            loop_counter += 1

            if loop_counter % PROCESS_EVERY != 0:
                time.sleep(0.05)
                continue

            frame = cam.capture_frame()

            if frame is None:
                continue

            state.latest_frame = frame.copy()

            # =========================
            # FACE RECOGNITION
            # =========================
            if settings["ENABLE_FACE_RECOGNITION"]:
                name, confidence = face_rec.recognize(frame)
            else:
                name, confidence = "Disabled", 0.0

            state.latest_name = f"{name} ({confidence*100:.2f}%)"

            add_log(f"👁 Detected: {name} ({confidence*100:.2f}%)")


            # =========================
            # CONFUSION MATRIX LOGGING
            # =========================
            if settings.get("TEST_MODE", False):
                actual = settings.get("EXPECTED_NAME", "Unknown")
            else:
                actual = "Unknown"

            log_result(name, actual)

            # =========================
            # CLASSIFICATION
            # =========================
            if name != "Unknown" and name != "Disabled":
                known_count += 1
                unknown_count = 0
            else:
                unknown_count += 1
                known_count = 0

            # =========================
            # AUTHORIZED
            # =========================
            if known_count >= 2:
                add_log(f"✅ Authorized: {name}")

                alarm.alarm_off()
                state.alarm_status = False
                alert_sent = False

            # =========================
            # INTRUDER
            # =========================
            elif unknown_count >= 2:
                add_log("🚨 Intruder detected!")

                alarm.alarm_on()
                state.alarm_status = True

                # =========================
                # TELEGRAM (NO SPAM)
                # =========================
                if settings["ENABLE_NOTIFICATIONS"] and not alert_sent and telegram:

                    def send_alert():
                        telegram.send_message("🚨 Intruder detected!")
                        telegram.send_image(frame)

                    threading.Thread(target=send_alert).start()

                    alert_sent = True

        # =========================
        # RESET SYSTEM
        # =========================
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
