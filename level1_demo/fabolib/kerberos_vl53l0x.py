# coding: utf-8
# Fabo #902 Kerberos基盤を用いたVL53L0Xの自動アドレス変更
import FaBoGPIO_PCAL6408
import time
import VL53L0X

''' definition
class Vl53l0xAccuracyMode:
    GOOD = 0        # 33 ms timing budget 1.2m range
    BETTER = 1      # 66 ms timing budget 1.2m range
    BEST = 2        # 200 ms 1.2m range
    LONG_RANGE = 3  # 33 ms timing budget 2m range
    HIGH_SPEED = 4  # 20 ms timing budget 1.2m range
'''

class KerberosVL53L0X():

    def __init__(self,busnum=1):
        pcal6408 = FaBoGPIO_PCAL6408.PCAL6408(busnum=busnum)
        mode = VL53L0X.Vl53l0xAccuracyMode.BEST
        ########################################
        # Sensor1のアドレスを変更する 0x29 -> 0x52
        ########################################
        pcal6408.setDigital(1<<0, 1) # 0番目のSensorの電源を入れる

        time.sleep(0.1)
        sensor1 = VL53L0X.VL53L0X(i2c_bus=busnum,i2c_address=0x29)
        sensor1.change_address(0x52)
        sensor1.open()
        sensor1.start_ranging(mode)
        timing = sensor1.get_timing()
        if timing < 20000:
            timing = 20000

        ########################################
        # Sensor2のアドレスを変更する 0x29 -> 0x54
        ########################################
        pcal6408.setDigital(1<<1, 1) # 1番目のSensorの電源を入れる
        time.sleep(0.1)
        sensor2 = VL53L0X.VL53L0X(i2c_bus=busnum,i2c_address=0x29)
        sensor2.change_address(0x54)
        sensor2.open()
        sensor2.start_ranging(mode)

        ########################################
        # Sensor3のアドレスを変更する 0x29 -> 0x56
        ########################################
        pcal6408.setDigital(1<<2, 1) # 3番目のSensorの電源を入れる
        time.sleep(0.1)
        sensor3 = VL53L0X.VL53L0X(i2c_bus=busnum,i2c_address=0x29)
        sensor3.change_address(0x56)
        sensor3.open()
        sensor3.start_ranging(mode)

        self.pcal6408 = pcal6408
        self.sensor1 = sensor1
        self.sensor2 = sensor2
        self.sensor3 = sensor3
        self.timing = timing
        return

    def __del__(self):
        self.sensor1.stop_ranging()
        self.sensor1.close()
        self.sensor2.stop_ranging()
        self.sensor2.close()
        self.sensor3.stop_ranging()
        self.sensor3.close()
        self.pcal6408.setAllClear() # すべてのSensorの電源を落とす

    def get_distance(self):
        ########################################
        # 全てのSensorの値を取得する
        ########################################
        while True:
            distance1 = self.sensor1.get_distance()
            distance2 = self.sensor2.get_distance()
            distance3 = self.sensor3.get_distance()

            if distance1 > 0 and distance2 > 0 and distance3 > 0:
                return int(distance1/10),int(distance2/10),int(distance3/10)
            time.sleep(self.timing/1000000.00)
