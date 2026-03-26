from sensors.camera import Camera
from detection.face_recognition import FaceRecognition
import cv2
import time

# =========================
# SETTINGS
# =========================
THRESHOLD = 5  # number of consecutive frames to confirm detection

known_count = 0
unknown_count = 0

# =========================
# INITIALIZE
# =========================
cam = Camera()
face_rec = FaceRecognition()

print("🔄 Testing face recognition... Press 'q' to quit")

# =========================
# MAIN LOOP
# =========================
while True:
    frame = cam.capture_frame()
    if frame is None:
        time.sleep(0.05)
        continue

    name = face_rec.recognize(frame)

    if name != "Unknown":
        known_count += 1
        unknown_count = 0
    else:
        unknown_count += 1
        known_count = 0

    # CONFIRMED DETECTION
    if known_count >= THRESHOLD:
        print(f"✅ CONFIRMED: {name}")
        known_count = 0  # reset to prevent repeated printing
    elif unknown_count >= THRESHOLD:
        print("🚨 CONFIRMED: Unknown person")
        unknown_count = 0

    # SHOW FRAME
    display_frame = frame.copy()
    cv2.putText(display_frame, name, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow("Face Recognition Test", display_frame)

    # QUIT
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# =========================
# CLEANUP
# =========================
cam.release()
cv2.destroyAllWindows()
