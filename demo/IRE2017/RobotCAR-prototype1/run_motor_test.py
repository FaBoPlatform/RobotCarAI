# coding: utf-8

import pkg_resources
SMBUS='smbus'
for dist in pkg_resources.working_set:
    #print(dist.project_name, dist.version)
    if dist.project_name == 'smbus':
        break
    if dist.project_name == 'smbus2':
        SMBUS='smbus2'
        break
if SMBUS == 'smbus':
    import smbus
elif SMBUS == 'smbus2':
    import smbus2 as smbus

import time
from servo import Servo

class Motor():
    ## DRV8830 Default I2C address
    MOTOR_ADDR_L = 0x64
    MOTOR_ADDR_R = 0x65

    # DRV8830 Register Addresses
    COMMAND0 = 0x00

    ## Value motor.
    FORWARD = 0x01
    BACK = 0x02
    STOP = 0x00

    def __init__(self, bus, motor_address=MOTOR_ADDR_L):
        self.bus = bus
        self.MOTOR_ADDRESS = motor_address


    def map(self, x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

    def forward(self, speed):
        if speed < 0:
            print("value is under 0,  must define 1-100 as speed.")
            return
        elif speed > 100:
            print("value is over 100,  must define 1-100 as speed.")
            return
        self.direction = self.FORWARD
        s = self.map(speed, 1, 100, 1, 58)
        sval = self.FORWARD | ((s+5)<<2) #スピードを設定して送信するデータを1Byte作成
        self.bus.write_i2c_block_data(self.MOTOR_ADDRESS,self.COMMAND0,[sval]) #生成したデータを送信

    def stop(self):
        self.bus.write_i2c_block_data(self.MOTOR_ADDRESS,self.COMMAND0,[self.STOP]) #モータへの電力の供給を停止(惰性で動き続ける)

    def back(self, speed):
        if speed < 0:
            print("value is under 0,  must define 1-100 as speed.")
            return
        elif speed > 100:
            print("value is over 100,  must define 1-100 as speed.")
            return
        self.direction = self.BACK
        s= self.map(speed, 1, 100, 1, 58)
        sval = self.BACK | ((s+5)<<2) #スピードを設定して送信するデータを1Byte作成
        self.bus.write_i2c_block_data(self.MOTOR_ADDRESS,self.COMMAND0,[sval]) #生成したデータを送信

    def brake(self):
        self.bus.write_i2c_block_data(self.MOTOR_ADDRESS,self.COMMAND0,[0x03]) #モータをブレーキさせる

class RobotCar():

    def __init__(self):
        self.bus = smbus.SMBus(1)
        self.motor = Motor(self.bus)
        #self.PCA9685 = Fabo_PCA9685.PCA9685(self.bus)
        # self.PCA9685.set_freq(50) default: 50 Hz
        #channel = 0
        #self.handle = Handle(self.PCA9685,channel)

    def motor_forward(self, speed):
        self.motor.forward(speed)

    def motor_stop(self):
        self.motor.stop()

    def motor_back(self, speed):
        self.motor.back(speed)

    def motor_brake(self):
        self.motor.brake()

    def handle_right(self):
        self.handle.right()

    def handle_left(self):
        self.handle.left()

    def handle_forward(self,value=None):
        self.handle.forward(value)

    def handle_angle(self, value):
        self.handle.angle(value)

    def get_handle_angle(self):
        return self.handle.get_angle()

print("start")

car = RobotCar()
handle = Servo()
car.motor_forward(100)
time.sleep(1)
car.motor_back(100)
time.sleep(1)
car.motor_forward(100)
time.sleep(1)
car.motor_stop()

handle.set_angle(91)
time.sleep(1)
handle.set_angle(70)
time.sleep(1)
handle.set_angle(110)
time.sleep(1)
handle.set_angle(91)

print("end")
