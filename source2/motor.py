#!/usr/bin/python
# coding: utf-8 
import smbus
import sys

## DRV8830 Default I2C slave address
MOTOR1_ADDRESS  = 0x64
''' DRV8830 Register Addresses '''
## sample rate driver
CONTROL = 0x00
## Value motor.
FORWARD = 0x02
BACK = 0x01
STOP = 0x00

print("start")

## smbus
bus = smbus.SMBus(1)

def map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min
    
speed = 10
s = map(speed, 1, 100, 1, 58)
sval = FORWARD | ((s+5)<<2) #スピードを設定して送信するデータを1Byte作成
bus.write_i2c_block_data(MOTOR1_ADDRESS,CONTROL,[sval]) #生成したデータを送信
print(sval)

print("end")
