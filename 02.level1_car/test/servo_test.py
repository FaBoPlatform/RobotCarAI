# coding: utf-8
import os
_FILE_DIR=os.path.abspath(os.path.dirname(__file__))

import time
import sys
sys.path.append(_FILE_DIR+'/..')
from fabolib import Servo

print("start")

handle = Servo(busnum=1)

try:
    for i in range(0,2):    
        handle.set_angle(90)
        time.sleep(1)
        handle.set_angle(45)
        time.sleep(1)
        handle.set_angle(90)
        time.sleep(1)
        handle.set_angle(135)
        time.sleep(1)
        handle.set_angle(90)
        time.sleep(1)
except:
    import traceback
    traceback.print_exc()
finally:
    handle.set_angle(90)

print("end")
