from picamera2 import Picamera2

class Camera:
    def __init__(self):
        self.picam2 = Picamera2()
        self.picam2.configure(self.picam2.create_preview_configuration())
        self.picam2.start()

    def capture_frame(self):
        frame = self.picam2.capture_array()
        return frame

    def release(self):
        self.picam2.stop()
