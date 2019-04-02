# coding: utf-8
# Fabo #902 Kerberos基盤を用いたLidarLiteV3の自動アドレス変更
import FaBoGPIO_PCAL6408
import time
import LidarLiteV3

class Kerberos():

    def __init__(self):
        pcal6408 = FaBoGPIO_PCAL6408.PCAL6408()

        ########################################
        # Lidar1のアドレスを変更する 0x62 -> 0x52
        ########################################
        pcal6408.setDigital(1<<0, 1) # 0番目のLidarの電源を入れる

        time.sleep(0.1)
        lidar1 = LidarLiteV3.Connect(0x62)
        lidar1.changeAddress(0x52)

        ########################################
        # Lidar2のアドレスを変更する 0x62 -> 0x54
        ########################################
        pcal6408.setDigital(1<<1, 1) # 1番目のLidarの電源を入れる
        time.sleep(0.1)
        lidar2 = LidarLiteV3.Connect(0x62)
        lidar2.changeAddress(0x54)

        ########################################
        # Lidar3のアドレスを変更する 0x62 -> 0x56
        ########################################
        pcal6408.setDigital(1<<2, 1) # 3番目のLidarの電源を入れる
        time.sleep(0.1)
        lidar3 = LidarLiteV3.Connect(0x62)
        lidar3.changeAddress(0x56)

        self.pcal6408 = pcal6408
        self.lidar1 = lidar1
        self.lidar2 = lidar2
        self.lidar3 = lidar3
        return

    def __del__(self):
        self.pcal6408.setAllClear() # すべてのLidarの電源を落とす

    def get_distance(self):
        ########################################10
        # 全てのLidarの値を取得する
        ########################################
        distance1 = self.lidar1.getDistance()
        distance2 = self.lidar2.getDistance()
        distance3 = self.lidar3.getDistance()
        return distance1,distance2,distance3

