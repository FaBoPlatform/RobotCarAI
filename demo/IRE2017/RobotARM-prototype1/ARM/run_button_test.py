# coding: utf-8
# pip3 install spidev

import spidev
import time
import sys

spi = spidev.SpiDev()
# open: Connects the object to the specified SPI device. open(X,Y) will open /dev/spidev-X.Y
import platform
bus = None
if platform.machine() == 'aarch64':
    bus = 3 # WebCam Jetson TX2 /dev/spidev-3.0
else: # armv7l
    bus = 0 # WebCam Raspberry Pi3 /dev/spidev0.0
device=0
spi.open(bus,device)

# SPI Settings
# max_speed_hz: Property that gets / sets the maximum bus speed in Hz.
# mode: Property that gets /sets the SPI mode as two bit pattern of Clock Polarity and Phase [CPOL|CPHA]. Range:0b00..0b11 (0..3)
spi.max_speed_hz = 5000
spi.mode=0b01

# A0コネクタに機器を接続
A0 = 0
SPI_PIN = A0

#read SPI from the ADC(MCP3008 chip), 8 possible chanels
def readadc(channel):
    """
    Analog Data Converterの値を読み込む
    @channel チャンネル番号
    """    
    #Writes a list of values to SPI device.
    #bits_per_word: Property that gets / sets the bits per word.
    #xfer2(list of values[, speed_hz, delay_usec, bits_per_word])
    speed_hz = 1
    delay_usec = (8+channel)<<4
    bits_per_word = 0
    to_send = [speed_hz,delay_usec,bits_per_word]
    adc = spi.xfer2(to_send)

    data = ((adc[1]&3) << 8) + adc[2]
    return data

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
        data = readadc(SPI_PIN)
        value = map(data, 0, 1023, 0, 100)
        print("adc : {:8} ".format(data))
        
        time.sleep( 0.1 )
except:
    import traceback
    traceback.print_exc()
finally:
    # close: Disconnects the object from the interface
    spi.close()
    sys.exit(0)
