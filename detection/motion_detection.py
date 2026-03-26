import cv2

class MotionDetector:
    def __init__(self, threshold=25, min_area=500):
        self.threshold = threshold
        self.min_area = min_area
        self.previous_frame = None

        # Stability settings
        self.motion_frames = 0
        self.no_motion_frames = 0

        self.motion_threshold_frames = 8     # higher = more stable ON
        self.no_motion_threshold_frames = 15 # higher = more stable OFF

        self.last_state = False

    def detect(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        if self.previous_frame is None:
            self.previous_frame = gray
            return False, frame

        frame_delta = cv2.absdiff(self.previous_frame, gray)
        thresh = cv2.threshold(frame_delta, self.threshold, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)

        contours, _ = cv2.findContours(
            thresh.copy(),
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        motion_detected = False

        for contour in contours:
            area = cv2.contourArea(contour)

            if area < self.min_area:
                continue

            motion_detected = True

            (x, y, w, h) = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # 🔥 Stability logic
        if motion_detected:
            self.motion_frames += 1
            self.no_motion_frames = 0
        else:
            self.no_motion_frames += 1
            self.motion_frames = 0

        # 🔥 Hysteresis (prevents flickering)
        if self.motion_frames >= self.motion_threshold_frames:
            final_motion = True
        elif self.no_motion_frames >= self.no_motion_threshold_frames:
            final_motion = False
        else:
            final_motion = self.last_state  # hold previous state

        self.last_state = final_motion
        self.previous_frame = gray.copy()

        return final_motion, frame
