# coding: utf-8

import time
from motor import Motor
from servo import Servo

print("start")

motor = Motor()
handle = Servo()

try:
    for i in range(1,101):
        motor.forward(i)
        time.sleep(0.1)
        motor.stop()

    for i in range(1,101):
        motor.back(i)
        time.sleep(0.1)
        motor.stop()

    motor.brake()

    handle.set_angle(90)
    time.sleep(1)
    handle.set_angle(45)
    time.sleep(1)
    handle.set_angle(90)
    time.sleep(1)
    handle.set_angle(135)
    time.sleep(1)
    handle.set_angle(90)
except:
    import traceback
    traceback.print_exc()
finally:
    motor.stop()
    handle.set_angle(90)

print("end")
