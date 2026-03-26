# main.py
from sensors.pir import PIRSensor
from hardware.alarm import AlarmSystem
from sensors.camera import Camera
from detection.face_recognition import FaceRecognition
from hardware.telegram_bot import TelegramBot
from config.settings import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from core import state

import time
import threading

# =========================
# LOG FUNCTION
# =========================
def add_log(msg):
    print(msg)
    state.logs.append(msg)
    # Limit logs to last 100 entries
    if len(state.logs) > 100:
        state.logs = state.logs[-100:]

# =========================
# TELEGRAM ALERT
# =========================
def send_telegram_async(frame):
    telegram = TelegramBot(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)
    telegram.send_message("🚨 Intruder detected!")
    telegram.send_image(frame, caption="Unknown person detected!")

# =========================
# MAIN SYSTEM LOOP
# =========================
def security_loop():
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

    MOTION_THRESHOLD = 2
    NO_MOTION_THRESHOLD = 100
    FACE_THRESHOLD = 2
    PROCESS_EVERY = 2
    loop_counter = 0

    while True:
        if not state.system_armed:
            time.sleep(0.2)
            continue

        if pir.detect():
            motion_count += 1
            no_motion_count = 0
        else:
            no_motion_count += 1
            motion_count = 0

        if motion_count >= MOTION_THRESHOLD:
            if not motion_active:
                add_log("🚨 Motion confirmed!")
                motion_active = True

            loop_counter += 1
            if loop_counter % PROCESS_EVERY != 0:
                time.sleep(0.05)
                continue

            frame = cam.capture_frame()
            state.latest_frame = frame.copy()

            name = face_rec.recognize(frame)
            state.latest_name = name

            add_log(f"👁 Detected: {name}")

            if name != "Unknown":
                known_count += 1
                unknown_count = 0
            else:
                unknown_count += 1
                known_count = 0

            if known_count >= FACE_THRESHOLD:
                add_log(f"✅ Authorized: {name}")
                alarm.alarm_off()
                state.alarm_status = False
                alert_sent = False
            elif unknown_count >= FACE_THRESHOLD:
                add_log("🚨 Intruder detected!")
                alarm.alarm_on()
                state.alarm_status = True
                if not alert_sent:
                    threading.Thread(target=send_telegram_async, args=(frame,)).start()
                    alert_sent = True

        if motion_active and no_motion_count >= NO_MOTION_THRESHOLD:
            add_log("😴 System reset")
            motion_active = False
            known_count = 0
            unknown_count = 0
            alert_sent = False
            alarm.alarm_off()
            state.alarm_status = False

        time.sleep(0.1)

# =========================
# START SYSTEM IN THREAD
# =========================
def start_system():
    threading.Thread(target=security_loop, daemon=True).start()
