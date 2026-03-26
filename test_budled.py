from hardware.alarm import AlarmSystem
import time

alarm = AlarmSystem()


try:
    alarm.alarm_on(10)  # run alarm for 10 seconds
finally:
    alarm.alarm_off()
    alarm.cleanup()
