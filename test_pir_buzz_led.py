from sensors.pir import PIRSensor
from hardware.alarm import AlarmSystem
import time

pir = PIRSensor()
alarm = AlarmSystem()

print("Testing PIR with Buzzer + LEDs...")

motion_active = False

try:
    while True:
        if pir.detect():
            if not motion_active:
                print("🚨 Motion detected!")
                alarm.alarm_on(5)  # run alarm for 5 seconds
                motion_active = True
        else:
            if motion_active:
                print("No motion")
            motion_active = False
            alarm.alarm_off()

        time.sleep(0.5)

except KeyboardInterrupt:
    print("Stopped")
    alarm.cleanup()
