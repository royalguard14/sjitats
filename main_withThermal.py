from sensors.pir import PIRSensor
from sensors.thermal import ThermalSensor
from hardware.alarm import AlarmSystem
from sensors.camera import Camera
from detection.face_recognition import FaceRecognition
import time

pir = PIRSensor()
thermal = ThermalSensor()
alarm = AlarmSystem()
cam = Camera()
face_rec = FaceRecognition()

print("🚀 AI Security System Running...")

# Motion stability
motion_count = 0
no_motion_count = 0
MOTION_THRESHOLD = 2
NO_MOTION_THRESHOLD = 15

# Face stability
known_count = 0
unknown_count = 0
FACE_THRESHOLD = 5

motion_active = False
thermal_checked = False  # 🔥 important

try:
    while True:

        # =========================
        # 📡 PIR DETECTION
        # =========================
        if pir.detect():
            motion_count += 1
            no_motion_count = 0
        else:
            no_motion_count += 1
            motion_count = 0

        # =========================
        # 🚨 MOTION CONFIRMED
        # =========================
        if motion_count >= MOTION_THRESHOLD:

            if not motion_active:
                print("🚨 Motion confirmed!")
                motion_active = True
                thermal_checked = False  # reset thermal check

            # =========================
            # 🔥 THERMAL CHECK (ONLY ONCE)
            # =========================
            if not thermal_checked:
                print("🔥 Checking thermal...")
                time.sleep(1)  # give sensor time to stabilize

                heat = thermal.detect_heat()
                print(f"🔥 Thermal result: {heat}")

                thermal_checked = True

                # ❌ No heat → ignore
                if not heat:
                    continue

                print("🔥 Human heat confirmed")

            # =========================
            # 📷 FACE RECOGNITION
            # =========================
            frame = cam.capture_frame()
            name = face_rec.recognize(frame)

            if name != "Unknown":
                known_count += 1
                unknown_count = 0
            else:
                unknown_count += 1
                known_count = 0

            # =========================
            # 🎯 FINAL DECISION
            # =========================
            if known_count >= FACE_THRESHOLD:
                print(f"✅ AUTHORIZED: {name}")
                alarm.alarm_off()

            elif unknown_count >= FACE_THRESHOLD:
                print("🚨 INTRUDER DETECTED")
                alarm.alarm_on()

        # =========================
        # 😴 RESET
        # =========================
        elif no_motion_count >= NO_MOTION_THRESHOLD:

            if motion_active:
                print("😴 System reset")

                motion_active = False
                thermal_checked = False
                known_count = 0
                unknown_count = 0

                alarm.alarm_off()

        # 🔥 slower loop = more stable system
        time.sleep(0.5)

except KeyboardInterrupt:
    print("\n🛑 Stopping system...")
    alarm.cleanup()
    cam.release()