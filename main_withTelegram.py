'''
Meron nang telegram but parang kulang
'''

from sensors.pir import PIRSensor
from hardware.alarm import AlarmSystem
from sensors.camera import Camera
from detection.face_recognition import FaceRecognition

from hardware.telegram_bot import TelegramBot
from config.settings import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

import time
import threading

# =========================
# INIT
# =========================
pir = PIRSensor()
alarm = AlarmSystem()
cam = Camera()
face_rec = FaceRecognition()
telegram = TelegramBot(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)

print("🚀 AI Security System Running...")

# =========================
# SETTINGS
# =========================
motion_count = 0
no_motion_count = 0

MOTION_THRESHOLD = 2
NO_MOTION_THRESHOLD = 50

known_count = 0
unknown_count = 0
FACE_THRESHOLD = 5

motion_active = False

# 🔥 TELEGRAM CONTROL
alert_sent = False   # ← IMPORTANT

# =========================
# LOOP CONTROL
# =========================
loop_counter = 0
PROCESS_EVERY = 2

# =========================
# TELEGRAM THREAD
# =========================
def send_telegram_async(frame):
    telegram.send_message("🚨 Intruder detected!")
    telegram.send_image(frame, caption="Unknown person detected!")

# =========================
# MAIN LOOP
# =========================
try:
    while True:

        # =========================
        # PIR SENSOR
        # =========================
        if pir.detect():
            motion_count += 1
            no_motion_count = 0
        else:
            no_motion_count += 1
            motion_count = 0

        # =========================
        # MOTION CONFIRMED
        # =========================
        if motion_count >= MOTION_THRESHOLD:

            if not motion_active:
                print("🚨 Motion confirmed!")
                motion_active = True

            loop_counter += 1

            if loop_counter % PROCESS_EVERY != 0:
                time.sleep(0.05)
                continue

            frame = cam.capture_frame()
            name = face_rec.recognize(frame)

            print(f"👁 Detected: {name}")

            # =========================
            # FACE FILTER
            # =========================
            if name != "Unknown":
                known_count += 1
                unknown_count = 0

            else:
                unknown_count += 1
                known_count = 0

            # =========================
            # AUTHORIZED
            # =========================
            if known_count >= FACE_THRESHOLD:
                print(f"✅ Authorized: {name}")

                alarm.alarm_off()

                # reset alert
                alert_sent = False

            # =========================
            # INTRUDER
            # =========================
            elif unknown_count >= FACE_THRESHOLD:

                print("🚨 Intruder detected!")

                alarm.alarm_on()

                # 🔥 ONLY SEND ONCE
                if not alert_sent:
                    threading.Thread(
                        target=send_telegram_async,
                        args=(frame,)
                    ).start()

                    alert_sent = True   # 🚫 block spam

        # =========================
        # RESET SYSTEM
        # =========================
        if motion_active and no_motion_count >= NO_MOTION_THRESHOLD:
            print("😴 System reset")

            motion_active = False
            known_count = 0
            unknown_count = 0

            alarm.alarm_off()

            # 🔥 RESET ALERT FLAG
            alert_sent = False

        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n🛑 Stopping system...")
    alarm.cleanup()
    cam.release()