<a name='top'>

【タイトル】
# レベル3：ロボットカー走行デモ FFMPEG UDP Streaming/TCP通信版
<hr>

【目標】
#### 映像をサーバに送り、level2,level3によるサーバからの走行指示でロボットカーを自走させる

【動画】<br>
走行しながら止まれを検出して止まる動画：[./document/leve3_aws_demo1.mp4](./document/leve3_aws_demo1.mp4)<br>

実行環境の構成
* Fabo TYPE1 ロボットカー

<a name='0'>

【目次】
* [実行方法](#1)
  * [Raspberry Pi3] ロボットカー FFMPEG UDP Streaming起動
  * [Jetson TX2/PC] サーバ起動
  * [Raspberry Pi3] ロボットカー起動
* [トラブルシューティング](#2)
  * Webcamが起動しない
  * 走行中にハンドルが固まった
  * Raspberry Pi3が起動しない
  * サーバが起動しない
* [ディレクトリとファイルについて](#3)
<hr>

<a name='1'>

## 実行方法
ダウンロード
> `git pull https://github.com/FaBoPlatform/RobotCarAI`<br>

#### [Raspberry Pi3] ロボットカー FFMPEG UDP Streaming起動
FFMPEG起動コマンド
> `ffmpeg -thread_queue_size 1024 -r 10 -video_size 160x120 -input_format yuyv422 -i /dev/video0 -pix_fmt yuv422p -threads 4 -f mpegts udp://192.168.0.77:8090`<br>

Dockerの場合
> `docker run -itd --device=/dev/video0:/dev/video0 ffmpeg /bin/bash -c "ffmpeg -thread_queue_size 1024 -r 10 -video_size 160x120 -input_format yuyv422 -i /dev/video0 -pix_fmt yuv422p -threads 4 -f mpegts udp://192.168.0.77:8090"`

送信先にサーバのIPアドレスとUDPポート番号を指定します。<br>
-r 10でFPSを指定します。物体検出の処理速度が遅いので-r 1でいいかもしれません。<br>
<hr>

#### [Jetson TX2/PC] サーバ起動
> `cd level3_demo_streaming/pc_server`<br>
> `python server.py`<br>

サーバ側が監視する自分のIPアドレスとTCPポート番号をサーバに合わせて修正してください。<br>
> `vi server.py`
>>`    HOST = '192.168.0.77' # Server IP Address`
>>`    PORT = 6666 # Server Port`

TensorFlowでSSD300モデルを読み込むので、起動完了まで少し時間がかかります。<br>
<hr>

#### [Raspberry Pi3] ロボットカー起動
> `cd level2_demo_socket/car_server`<br>
> `python start_button.py`<br>

青いボタンを押すと走行開始します。<br>
赤いボタンを押すと走行停止します。<br>

クライアント側も通信先のサーバのIPアドレスとTCPポート番号をサーバに合わせて修正してください。<br>
> `vi run_car_client.py`
>>`    HOST = '192.168.0.77' # Server IP Address`
>>`    PORT = 6666 # Server Port`

走行開始すると、サーバに開始したことを通知します。<br>
ソースコード：[./car_client/run_car_client.py](./car_client/run_car_client.py)<br>
```python
        ########################################
        # ロボットカー開始をサーバに送る
        ########################################
        message = "START"
        sock.sendall(message.encode('ascii'))
```
ロボットカー開始の通知を受けたサーバは、UDPポートに送られてきている動画を読み込み、解析してTCPポートでロボットカーに送り続けます。<br>
TCP通信のみの時は1フレームずつ確認しながらの通信処理でしたが、UDP Streamingを使った動画解析ではロボットカーからの受信応答を待たずに次のフレーム処理を開始しています。<br>
そのため、クライアント側は受信したパケットの処理方法がlevel3_demo_socketとは異なります。<br>

[<ページTOP>](#top)　[<目次>](#0)
<hr>

<a name='2'>

## トラブルシューティング
#### Webcamが起動しない
>`IOError: Couldn't open video file or webcam. If you're trying to open a webcam, make sure you video_path is an integer!`

OpenCVの映像取得に失敗した場合にこのエラーが発生します。<br>
他にカメラを使っているプロセスがなければ、数秒おいて再実行で解決することが多いです。<br>
それでも解決しない場合は、カメラのUSBケーブルを抜き差ししてください。<br>
これは再実行時によく発生します。<br>
<hr>

#### 走行中にハンドルが固まった
>`VIDIOC_DQBUF: No such device`

ロボットカーの赤いボタンを押して車両を停止してください。<br>
走行中に突然一方方向に進み続けてしまう場合は、Raspberry Pi3からの電力供給が遮断されてカメラが認識不能になったために発生します。<br>
カメラのUSBケーブルを抜き差ししてください。<br>
Faboシールドの電源をRaspberry Pi3から取得している時に、サーボの消費電力量が増えた瞬間に発生します。電力供給はすぐに復旧するので走行は続くのですが、カメラが認識不能になるため、制御不能に陥ります。<br>
<hr>

#### Raspberry Pi3が起動しない
バッテリーの出力不足が原因として上げられます。<br>
2A以上のモバイルバッテリーを使ってください。<br>
<hr>

#### サーバが起動しない
server.pyのHOST,PORTを確認してください。<br>
Dockerを使っている場合は、HOSTはDockerコンテナIDになります。<br>
ファイアーウォールは通常、内部IPに対して設定していないので通信可能ですが、設定している場合はサーバ側でTCPポート番号の通信を許可してください。<br>

[<ページTOP>](#top)　[<目次>](#0)
<hr>

<a name='3'>

## ディレクトリとファイルについて
* ディレクトリについて
  * car_client/ ロボットカー制御関連
  * car_client/fabolib/ Fabo製基板関連
  * car_client/lib/ SPI,カメラライブラリ
  * pc_server/ サーバ解析関連
  * pc_server/lib/ ライン検出関連
* ファイルについて
  * README.md このファイル
  * car_client/run_car_client.py 自動走行コード
  * car_client/start_button.py 開始ボタンコード
  * pc_server/server.py サーバ起動コード

[<ページTOP>](#top)　[<目次>](#0)
<hr>
