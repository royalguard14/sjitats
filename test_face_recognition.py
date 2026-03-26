from sensors.camera import Camera
from detection.face_recognition import FaceRecognition
import cv2

known_count = 0
unknown_count = 0
THRESHOLD = 5

cam = Camera()
face_rec = FaceRecognition()

print("Testing face recognition... Press 'q' to quit")


while True:
    frame = cam.capture_frame()

    name = face_rec.recognize(frame)

    if name != "Unknown":
        known_count += 1
        unknown_count = 0
    else:
        unknown_count += 1
        known_count = 0

    if known_count >= THRESHOLD:
        print(f"✅ CONFIRMED: {name}")

    elif unknown_count >= THRESHOLD:
        print("🚨 CONFIRMED: Unknown person")

    cv2.imshow("Face Test", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()