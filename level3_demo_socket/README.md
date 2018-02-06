<a name='top'>

【タイトル】
# レベル3：ロボットカー走行デモ TCP通信版
<hr>

【目標】
#### 映像をサーバに送り、level2,level3によるサーバからの走行指示でロボットカーを自走させる

実行環境の構成
* Fabo TYPE1 ロボットカー

<a name='0'>

【目次】
* [実行方法](#1)
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

#### [Jetson TX2/PC] サーバ起動
> `cd level3_demo_socket/pc_server`<br>
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
<hr>

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
