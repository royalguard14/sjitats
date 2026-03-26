import RPi.GPIO as GPIO

class PIRSensor:
    def __init__(self, pin=4):
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN)

    def detect(self):
        return GPIO.input(self.pin) == 1
