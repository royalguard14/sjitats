import RPi.GPIO as GPIO
import time

class AlarmSystem:
    def __init__(self, led_pinG=18, buzzer_pin=26, led_pinR=12):
        self.led_pinG = led_pinG
        self.led_pinR = led_pinR
        self.buzzer_pin = buzzer_pin

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.led_pinG, GPIO.OUT)
        GPIO.setup(self.led_pinR, GPIO.OUT)
        GPIO.setup(self.buzzer_pin, GPIO.OUT)

    def alarm_on(self, duration=10):
        end_time = time.time() + duration

        while time.time() < end_time:
            # Green ON, Red OFF
            GPIO.output(self.led_pinG, GPIO.HIGH)
            GPIO.output(self.led_pinR, GPIO.LOW)

            # Buzzer ON
            GPIO.output(self.buzzer_pin, GPIO.HIGH)
            time.sleep(0.3)

            # Green OFF, Red ON
            GPIO.output(self.led_pinG, GPIO.LOW)
            GPIO.output(self.led_pinR, GPIO.HIGH)

            # Buzzer OFF (creates beeping effect)
            GPIO.output(self.buzzer_pin, GPIO.LOW)
            time.sleep(0.3)

    def alarm_off(self):
        GPIO.output(self.led_pinG, GPIO.LOW)
        GPIO.output(self.led_pinR, GPIO.LOW)
        GPIO.output(self.buzzer_pin, GPIO.LOW)

    def cleanup(self):
        GPIO.cleanup()

