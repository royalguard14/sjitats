from sensors.pir import PIRSensor
import time

pir = PIRSensor()

print("Testing PIR...")

try:
    while True:
        if pir.detect():
            print("🚨 Motion detected!")
        else:
            print("No motion")

        time.sleep(1)

except KeyboardInterrupt:
    print("Stopped")