# coding: utf-8
# Fabo #902 Kerberos基盤を用いたLidarLiteV3の自動アドレス変更
import FaBoGPIO_PCAL6408
import time
import sys
import LidarLiteV3

pcal6408 = FaBoGPIO_PCAL6408.PCAL6408()

try:
    ########################################
    # Lidar1のアドレスを変更する 0x62 -> 0x52
    ########################################
    pcal6408.setDigital(1<<0, 1) # 0番目のLidarの電源を入れる
    time.sleep(0.1)
    lidar1 = LidarLiteV3.Connect(0x62)
    lidar1.changeAddress(0x52)
    for i in range(300):
        distance1 = lidar1.getDistance()
        sys.stdout.write("Distance to target = "+str(distance1)+"   \r")
        sys.stdout.flush()
        time.sleep(0.022)
    print("")
    sys.stdout.flush()
    print("end")


    ########################################
    # Lidar2のアドレスを変更する 0x62 -> 0x54
    ########################################
    pcal6408.setDigital(1<<1, 1) # 1番目のLidarの電源を入れる
    time.sleep(0.1)
    lidar2 = LidarLiteV3.Connect(0x62)
    lidar2.changeAddress(0x54)

    for i in range(300):
        distance2 = lidar2.getDistance()
        sys.stdout.write("Distance to target = "+str(distance2)+"   \r")
        sys.stdout.flush()
        time.sleep(0.022)
    print("")
    sys.stdout.flush()
    print("end")


    ########################################
    # Lidar3のアドレスを変更する 0x62 -> 0x56
    ########################################
    pcal6408.setDigital(1<<2, 1) # 3番目のLidarの電源を入れる
    time.sleep(0.1)
    lidar3 = LidarLiteV3.Connect(0x62)
    lidar3.changeAddress(0x56)

    for i in range(300):
        distance3 = lidar3.getDistance()
        sys.stdout.write("Distance to target = "+str(distance3)+"   \r")
        sys.stdout.flush()
        time.sleep(0.022)
    print("")
    sys.stdout.flush()
    print("end")


    ########################################10
    # 全てのLidarの値を取得する
    ########################################
    for i in range(300):
        distance1 = lidar1.getDistance()
        distance2 = lidar2.getDistance()
        distance3 = lidar3.getDistance()
        sys.stdout.write("Distance to target = "+str(distance1)+", "+str(distance2)+", "+str(distance3)+"         \r")
        sys.stdout.flush()
        time.sleep(0.022)
    print("")
    sys.stdout.flush()
    print("end")


except:
    import traceback
    traceback.print_exc()
finally:
    pcal6408.setAllClear() # すべてのLidarの電源を落とす
    sys.exit()
