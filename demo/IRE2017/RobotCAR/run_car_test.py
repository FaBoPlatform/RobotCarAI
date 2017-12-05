# coding: utf-8

import time
from car import Car

print("start")

car = Car()

try:
    for i in range(1,101):
        car.forward(i)
        time.sleep(0.1)
        car.stop()

    for i in range(1,101):
        car.back(i)
        time.sleep(0.1)
        car.stop()

    car.brake()

    car.set_angle(90)
    time.sleep(1)
    car.set_angle(55)
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
