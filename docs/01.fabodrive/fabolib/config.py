# coding: utf-8

class ServoConfig():
    # サーボの限界軸角度
    SERVO_MIN_PULSE = 650   # サーボの軸角度が0度になるHIGH時間のμ秒。サーボ毎に特性が異なる。
    SERVO_MAX_PULSE = 2350  # サーボの軸角度が180度になるHIGH時間のμ秒。サーボ毎に特性が異なる。
    # サーボの中央位置
    SERVO_CENTER_PULSE = (SERVO_MIN_PULSE + SERVO_MAX_PULSE)/2
    # サーボの動作遅延
    SERVO_SPEED = 0

class MotorConfig():
    SPEED_RATIO = 1.0 # モーター出力制御係数。速すぎる場合は0.5にダウンする

class CarConfig():
    HANDLE_NEUTRAL = 95 # ステアリングニュートラル位置
    HANDLE_ANGLE = 42 # 左右最大アングル
    N_BACK_FOWARD = 5 # バック時、障害物との距離を取るためにとりあえず真っ直ぐバックする回数
    MAX_LOG_LENGTH = 20 # ハンドル操作ログの保持数 MAX_LOG_LENGTH > N_BACK_FOWARD
