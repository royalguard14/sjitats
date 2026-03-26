import face_recognition
import os
import cv2

class FaceRecognition:

    def __init__(self):
        self.known_encodings = []
        self.known_names = []
        self.load_faces()

    def load_faces(self):
        print("🔄 Loading known faces...")

        dataset_path = "dataset"

        if not os.path.exists(dataset_path):
            print("⚠️ No dataset folder found")
            return

        for name in os.listdir(dataset_path):
            person_path = os.path.join(dataset_path, name)

            if not os.path.isdir(person_path):
                continue

            for file in os.listdir(person_path):
                img_path = os.path.join(person_path, file)

                try:
                    image = face_recognition.load_image_file(img_path)
                    encodings = face_recognition.face_encodings(image)

                    if len(encodings) > 0:
                        self.known_encodings.append(encodings[0])
                        self.known_names.append(name)

                except Exception as e:
                    print("Error loading image:", e)

        print(f"✅ Loaded {len(self.known_names)} face samples")

    def reload(self):
        print("🔄 Reloading known faces...")
        self.known_encodings = []
        self.known_names = []
        self.load_faces()

    def recognize(self, frame):

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_frame)
        encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for encoding in encodings:
            matches = face_recognition.compare_faces(self.known_encodings, encoding)
            face_distances = face_recognition.face_distance(self.known_encodings, encoding)

            if len(face_distances) > 0:
                best_match_index = face_distances.argmin()

                if matches[best_match_index]:
                    return self.known_names[best_match_index]

        return "Unknown"
