import FaBoGPIO_PCAL6408
import time
import sys

pcal6408 = FaBoGPIO_PCAL6408.PCAL6408()

try:
    while True:
        for i in range(8):
            pcal6408.setDigital(1<<i, 1)
            time.sleep(1)

        pcal6408.setAllClear()
        time.sleep(1)
        if i == 7:
            break

except:
    pass
finally:
    pcal6408.setAllClear()
sys.exit()
