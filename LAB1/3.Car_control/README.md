# ラジコンハンドル操作、モーター操作の単体コード

* ## handle.ipynb

ハンドルのニュートラル位置はサーボへのパーツの取り付け角度で変わってきます。
大体300前後になるかと思います。

フロントタイヤの左右最大角は壊れない程度に抑えるために45としておきます。
ソースコードでは真っ直ぐ、左、右だけの操作にてありますが、値を調整することで舵角を小さくすることも可能です。

```python
import MotorShield
r = MotorShield.RobotCar()
r.handle_move(345) # 右に切る
```

* ## motor.ipynb

速度は0-100の範囲で前進、後進、停止に制御できます。
```python
import time
import MotorShield
r = MotorShield.RobotCar()
r.car_forward(100) # 速度100で前進
time.sleep(1)
r.car_back(100) # 速度100で後進
time.sleep(1)
r.car_stop() # 停止
```