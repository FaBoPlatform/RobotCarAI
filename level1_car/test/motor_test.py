# coding: utf-8
import os
_FILE_DIR=os.path.abspath(os.path.dirname(__file__))

import time
import sys
sys.path.append(_FILE_DIR+'/..')
from fabolib.motor import Motor
from fabolib.servo import Servo

print("start")

motor = Motor(busnum=1)

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

except:
    import traceback
    traceback.print_exc()
finally:
    motor.stop()

print("end")
