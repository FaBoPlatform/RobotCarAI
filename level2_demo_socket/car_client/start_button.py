# coding: utf-8
# pip3 install spidev
# AI開始ボタン

import spidev
import time
import sys
import os
import subprocess
from subprocess import Popen
from lib import SPI

# 開始ボタンのSPI接続コネクタ番号
A1 = 1
START_BUTTON_SPI_PIN = A1

spi = SPI()

proc = None
try:
    cmd = "python "+os.path.abspath(os.path.dirname(__file__))+"/run_car_client.py"
    while True:
        data = spi.readadc(START_BUTTON_SPI_PIN) # data: 0-1023
        if data >= 1000:
            print("start car")
            proc = Popen(cmd,shell=True)
            proc.wait()

        time.sleep(0.1)
except:
    import traceback
    traceback.print_exc()
finally:
    proc.terminate()
    sys.exit(0)
