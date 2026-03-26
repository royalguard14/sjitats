from sensors.camera import Camera
from detection.face_recorder import FaceRecorder

cam = Camera()
recorder = FaceRecorder()

name = input("Input name: ")

recorder.record(name, cam)

cam.release()