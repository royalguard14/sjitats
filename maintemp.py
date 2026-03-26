from sensors.pir import PIRSensor
from hardware.alarm import AlarmSystem
from sensors.camera import Camera
from detection.face_recognition import FaceRecognition
import time

pir = PIRSensor()
alarm = AlarmSystem()
cam = Camera()
face_rec = FaceRecognition()

print("🚀 System running...")

# 🔥 Motion stability
motion_count = 0
no_motion_count = 0
MOTION_THRESHOLD = 2
NO_MOTION_THRESHOLD = 15

# 🔥 Face stability
known_count = 0
unknown_count = 0
FACE_THRESHOLD = 5

motion_active = False
motion_timer = 0
MOTION_HOLD_TIME = 5  # 🔥 keep system active for 5 seconds

try:
    while True:

        # =========================
        # 📡 PIR INPUT
        # =========================
        if pir.detect():
            motion_count += 1
            no_motion_count = 0
        else:
            no_motion_count += 1
            motion_count = 0

        # =========================
        # 🚨 MOTION START
        # =========================
        if motion_count >= MOTION_THRESHOLD:

            if not motion_active:
                print("🚨 Motion confirmed!")
                motion_active = True
                motion_timer = time.time()

        # =========================
        # 🔒 HOLD STATE (VERY IMPORTANT)
        # =========================
        if motion_active:

            # Keep system active for few seconds
            if time.time() - motion_timer < MOTION_HOLD_TIME:

                frame = cam.capture_frame()
                name = face_rec.recognize(frame)

                # 🧠 Face stability
                if name != "Unknown":
                    known_count += 1
                    unknown_count = 0
                else:
                    unknown_count += 1
                    known_count = 0

                # 🎯 Decision
                if known_count >= FACE_THRESHOLD:
                    print(f"✅ CONFIRMED: {name} (authorized)")
                    alarm.alarm_off()

                elif unknown_count >= FACE_THRESHOLD:
                    print("🚨 CONFIRMED: Unknown person")
                    alarm.alarm_on()

            else:
                # ⏳ End hold period
                print("😴 Motion window ended")
                motion_active = False
                known_count = 0
                unknown_count = 0
                alarm.alarm_off()

        time.sleep(0.2)

except KeyboardInterrupt:
    print("\n🛑 Stopping system...")
    alarm.cleanup()
    cam.release()