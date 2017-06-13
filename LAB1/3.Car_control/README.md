# ラジコンハンドル操作、モーター操作の単体コード

* ## handle.ipynb:ハンドル操作

ハンドルのニュートラル位置はサーボへのパーツの取り付け角度で変わってきます。
大体300前後になるかと思います。

フロントタイヤの左右最大角は壊れない程度に抑えるために45としておきます。
ソースコードでは真っ直ぐ、左、右だけの操作にてありますが、値を調整することで舵角を小さくすることも可能です。

```python
import MotorShield
car = MotorShield.RobotCar()
car.handle_angle(330) # 値指定で右に切る
car.handle_angle(280) # 値指定で左に切る
car.handle_angle(300) # 値指定で真っ直ぐに戻す
car.handle_right() # 右に切る
car.handle_left() # 左に切る
car.handle_forward() # 真っ直ぐに戻す
car.handle_forward(310) # 真っ直ぐの値を310に設定して真っ直ぐに戻す
```

* ## motor.ipynb:モーター操作

速度は0-100の範囲で前進、後進、停止に制御できます。
```python
import time
import MotorShield
car = MotorShield.RobotCar()
car.motor_forward(100) # 速度100で前進
time.sleep(1)
car.motor_back(100) # 速度100で後進
time.sleep(1)
car.motor_stop() # 停止
```