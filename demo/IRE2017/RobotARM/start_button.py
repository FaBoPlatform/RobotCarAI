# coding: utf-8
# pip3 install spidev
# AI開始ボタン

import spidev
import time
import sys
import os
import subprocess
from subprocess import Popen
from led import LED
from spi import SPI

# 開始ボタンのSPI接続コネクタ番号
A1 = 1
A2 = 2
START_BUTTON_SPI_PIN = A1
TEST_BUTTON_SPI_PIN = A2

spi = SPI()
led = LED()

proc = None
try:
    led.start('lightline')
    cmd = "python "+os.path.abspath(os.path.dirname(__file__))+"/run_arm_ai.py"
    cmd_test = "python "+os.path.abspath(os.path.dirname(__file__))+"/run_ai_test.py"
    while True:
        data = spi.readadc(START_BUTTON_SPI_PIN) # data: 0-1023
        if data >= 1000:
            led.stop()
            led.start('light 7')
            print("start ai")
            proc = Popen(cmd,shell=True)
            proc.wait()
            led.stop()
            led.start('lightline')

        data = spi.readadc(TEST_BUTTON_SPI_PIN) # data: 0-1023
        if data >= 1000:
            led.stop()
            led.start('light 7')
            print("start ai")
            proc = Popen(cmd_test,shell=True)
            proc.wait()
            led.stop()
            led.start('lightline')

        time.sleep(0.1)
except:
    import traceback
    traceback.print_exc()
finally:
    led.stop()
    proc.terminate()
    sys.exit(0)
