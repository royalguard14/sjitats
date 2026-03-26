import face_recognition
import cv2
import os

class FaceRecognition:
    def __init__(self, known_faces_path="known_faces"):
        self.known_faces_path = known_faces_path
        self.known_encodings = []
        self.known_names = []
        self.load_known_faces(self.known_faces_path)

    def load_known_faces(self, path):
        print("🔄 Loading known faces...")
        self.known_encodings.clear()
        self.known_names.clear()

        for person_name in os.listdir(path):
            person_path = os.path.join(path, person_name)
            if not os.path.isdir(person_path):
                continue

            for file in os.listdir(person_path):
                if file.endswith(".jpg") or file.endswith(".png"):
                    image_path = os.path.join(person_path, file)
                    image = face_recognition.load_image_file(image_path)
                    encodings = face_recognition.face_encodings(image)
                    if len(encodings) > 0:
                        self.known_encodings.append(encodings[0])
                        self.known_names.append(person_name)

        print(f"✅ Loaded {len(self.known_names)} face samples")

    def recognize(self, frame):
        if frame is None:
            return "Unknown"

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(self.known_encodings, face_encoding)
            if True in matches:
                index = matches.index(True)
                return self.known_names[index]
        return "Unknown"

    def reload(self):
        self.load_known_faces(self.known_faces_path)
