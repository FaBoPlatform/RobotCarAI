# coding: utf-8

raw_input('Connect 1st Lidar cable and Enter key')

''' 1st Lidar
Lidar Lite v3のケーブルを一本だけ接続します。
Lidarはアドレス0x62で起動します。
このアドレスを0x64に変更してセンサー値を取得できることを確認します。
'''
import sys
import time
import LidarLiteV3
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


raw_input('Connect 2nd Lidar cable and Enter key')

''' 2nd Lidar
Lidar Lite v3の2個目のケーブルを接続します。
Lidarはアドレス0x62で起動します。
このアドレスを0x66に変更してセンサー値を取得できることを確認します。
'''
import sys
import time
import LidarLiteV3
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


raw_input('Connect 3rd Lidar cable and Enter key')

''' 3rd Lidar
Lidar Lite v3の3個目のケーブルを接続します。
Lidarはアドレス0x62で起動します。
このアドレスを0x68に変更してセンサー値を取得できることを確認します。
'''
import sys
import time
import LidarLiteV3
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


raw_input('OK, Let\'s get all Lidar value. Enter key')

''' 3 Lidars
3個のLidar Lite v3がそれぞれ値取得出来ていることを確認します。
'''
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
