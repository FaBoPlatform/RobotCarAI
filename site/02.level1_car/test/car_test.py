# coding: utf-8
import os
_FILE_DIR=os.path.abspath(os.path.dirname(__file__))

import time
import sys
sys.path.append(_FILE_DIR+'/..')
from fabolib.car import Car

print("start")

car = Car()

try:
    for i in range(1,101):
        car.forward(i)
        time.sleep(0.1)
    car.stop()

    #モーターが惰性を含めて回転中は逆回転にすることが出来ないため、sleepを入れておく
    time.sleep(1)

    for i in range(1,101):
        car.back(i)
        time.sleep(0.1)
    car.stop()


    car.set_angle(90)
    time.sleep(1)
    car.set_angle(45)
    time.sleep(1)
    car.set_angle(90)
    time.sleep(1)
    car.set_angle(135)
    time.sleep(1)
    car.set_angle(90)
except:
    import traceback
    traceback.print_exc()
finally:
    car.stop()
    car.set_angle(90)

print("end")
