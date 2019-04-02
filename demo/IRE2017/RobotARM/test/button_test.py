# coding: utf-8
import os
_FILE_DIR=os.path.abspath(os.path.dirname(__file__))

import time
import sys
sys.path.append(_FILE_DIR+'/..')
from lib import SPI

A0 = 0
SPI_PIN = A0
button = SPI()

def map(x, in_min, in_max, out_min, out_max):
    """
    map関数
    @x 変換したい値
    @in_min 変換前の最小値
    @in_max 変換前の最大値
    @out_min 変換後の最小
    @out_max 変換後の最大値
    @return 変換された値
    """
    return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

try:
    while True:
        data = button.readadc(SPI_PIN)
        value = map(data, 0, 1023, 0, 100)
        print("adc : {:8} ".format(data))
        
        time.sleep( 0.1 )
except:
    import traceback
    traceback.print_exc()
finally:
    pass
