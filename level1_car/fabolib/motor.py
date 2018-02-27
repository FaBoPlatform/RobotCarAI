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

class Motor():
    '''
    通電し続けている限り、DRV8830に書き込んだ値のパルスを送信し続けるため、
    値を一度書き込んだら値に変更があるまで放置でよい（無限ループで書き込み続ける必要はない）
    '''
    ## DRV8830 Default I2C address
    MOTOR_ADDR_L = 0x64
    MOTOR_ADDR_R = 0x65

    # DRV8830 Register Addresses
    COMMAND0 = 0x00

    ## Value motor.
    FORWARD = 0x01
    BACK = 0x02
    STOP = 0x00
    BRAKE = 0x03

    # I2C Clock High Time (FAST MODE)
    CLOCK_HIGH = 1.0/0.6e-6 # 0.6 microsecond
    CLOCK_LOW = 1.0/1.3e-6 # 1.3 microsecond

    def __init__(self, busnum=1, motor_address=None):
        if motor_address is None:
            motor_address = self.MOTOR_ADDR_L
        self.bus = smbus.SMBus(busnum)
        self.MOTOR_ADDRESS = motor_address

    def map(self, x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

    def back(self, speed):
        '''
        後進する値は2bitで
        xxxx xx01 となる。(FORWARD = 0x01)
        前進する値は2bitで
        xxxx xx10 となる。(BACK = 0x02)
        停止する値は2bitで
        xxxx xx00 となる。(STOP = 0x00)
        ブレーキする値は2bitで
        xxxx xx11 となる。(BRAKE = 0x03)
        
        速度として使える値は1111 11 == 0011 1111 == 63まで。
        speed : 0-100
        '''
        if speed <= 0:
            print("value is under 0,  must define 1-100 as speed.")
            return
        elif speed > 100:
            print("value is over 100,  must define 1-100 as speed.")
            return
        direction = self.FORWARD
        s = self.map(speed, 1, 100, 1, 63)
        value = (s<<2) + direction # スピード値を2ビット左シフトして下位2bitに前進ビットを設定した1Byteの送信データを作成
        print("forward:{} {}".format(speed,value))
        self.bus.write_byte_data(self.MOTOR_ADDRESS,self.COMMAND0,value) #生成したデータを送信

    def stop(self):
        self.bus.write_byte_data(self.MOTOR_ADDRESS,self.COMMAND0,self.STOP) #モータへの電力の供給を停止(惰性で動き続ける)

    def forward(self, speed):
        if speed <= 0:
            print("value is under 0,  must define 1-100 as speed.")
            return
        elif speed > 100:
            print("value is over 100,  must define 1-100 as speed.")
            return
        direction = self.BACK
        s = self.map(speed, 1, 100, 1, 63)
        value = (s<<2) + direction # スピード値を2ビット左シフトして下位2bitに後進ビットを設定した1Byteの送信データを作成
        print("forward:{} {}".format(speed,value))
        self.bus.write_byte_data(self.MOTOR_ADDRESS,self.COMMAND0,value) #生成したデータを送信

    def brake(self):
        self.bus.write_byte_data(self.MOTOR_ADDRESS,self.COMMAND0,0x03) #モータをブレーキさせる
