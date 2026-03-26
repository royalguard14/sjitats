import cv2
import os
import time
import face_recognition

class FaceRecorder:
    def __init__(self, save_path="known_faces", duration=15):
        self.save_path = save_path
        self.duration = duration

    def record(self, name, camera):
        person_path = os.path.join(self.save_path, name)

        # Create folder if not exist
        os.makedirs(person_path, exist_ok=True)

        print(f"🎥 Recording face for '{name}' for {self.duration} seconds...")

        start_time = time.time()
        count = 0

        while time.time() - start_time < self.duration:
            frame = camera.capture_frame()
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            face_locations = face_recognition.face_locations(rgb)

            for (top, right, bottom, left) in face_locations:
                face_image = frame[top:bottom, left:right]

                if face_image.size == 0:
                    continue

                file_path = os.path.join(person_path, f"{count}.jpg")
                cv2.imwrite(file_path, face_image)

                count += 1

                print(f"Saved image {count}")

            cv2.imshow("Recording Face", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cv2.destroyAllWindows()

        print(f"✅ Done recording {count} images for {name}")
