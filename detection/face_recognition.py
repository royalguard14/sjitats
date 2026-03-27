import face_recognition
import cv2
import os
import numpy as np

from config.settings_manager import load_settings

# =========================
# KNN IMPORT (SAFE)
# =========================
try:
    from sklearn.neighbors import KNeighborsClassifier
    KNN_AVAILABLE = True
except ImportError:
    print("⚠️ scikit-learn not installed. KNN disabled.")
    KNN_AVAILABLE = False


class FaceRecognition:

    def __init__(self, known_faces_path="known_faces"):
        self.known_faces_path = known_faces_path

        self.known_encodings = []
        self.known_names = []

        self.model = None

        self.load_known_faces()

    # =========================
    # LOAD FACES
    # =========================
    def load_known_faces(self):
        print("🔄 Loading known faces...")

        self.known_encodings = []
        self.known_names = []

        for person_name in os.listdir(self.known_faces_path):
            person_path = os.path.join(self.known_faces_path, person_name)

            if not os.path.isdir(person_path):
                continue

            for file in os.listdir(person_path):
                if file.lower().endswith((".jpg", ".png")):
                    image_path = os.path.join(person_path, file)

                    image = face_recognition.load_image_file(image_path)
                    encodings = face_recognition.face_encodings(image)

                    if len(encodings) > 0:
                        self.known_encodings.append(encodings[0])
                        self.known_names.append(person_name)

        print(f"✅ Loaded {len(self.known_names)} faces")

        self.train_knn()

    # =========================
    # TRAIN KNN
    # =========================
    def train_knn(self):
        settings = load_settings()

        if not settings.get("USE_KNN", False):
            self.model = None
            return

        if not KNN_AVAILABLE:
            print("⚠️ KNN not available (scikit-learn missing)")
            return

        if len(self.known_encodings) == 0:
            print("⚠️ No data for KNN")
            return

        print("🧠 Training KNN...")

        self.model = KNeighborsClassifier(
            n_neighbors=settings.get("KNN_NEIGHBORS", 3)
        )

        self.model.fit(self.known_encodings, self.known_names)

        print("✅ KNN trained")

    # =========================
    # RECOGNIZE FACE
    # =========================
    def recognize(self, frame):

        settings = load_settings()

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        if len(face_encodings) == 0:
            return "Unknown", 0.0

        encoding = face_encodings[0]

        # =========================
        # KNN MODE
        # =========================
        if settings.get("USE_KNN", False) and self.model is not None:

            distances, _ = self.model.kneighbors([encoding], n_neighbors=1)

            distance = distances[0][0]

            # confidence (0–1)
            confidence = max(0.0, min(1.0, 1 / (1 + distance)))

            prediction = self.model.predict([encoding])[0]

            # optional threshold
            threshold = settings.get("FACE_CONFIDENCE_THRESHOLD", 0.6)
            if confidence < threshold:
                return "Unknown", confidence

            return prediction, confidence

        # =========================
        # REGULAR MODE
        # =========================
        matches = face_recognition.compare_faces(self.known_encodings, encoding)
        face_distances = face_recognition.face_distance(self.known_encodings, encoding)

        if len(self.known_encodings) > 0 and True in matches:
            best_match_index = np.argmin(face_distances)

            confidence = max(0.0, min(1.0, 1 - face_distances[best_match_index]))

            # optional threshold
            threshold = settings.get("FACE_CONFIDENCE_THRESHOLD", 0.6)
            if confidence < threshold:
                return "Unknown", confidence

            return self.known_names[best_match_index], confidence

        return "Unknown", 0.0
