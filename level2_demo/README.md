<a name='top'>

【タイトル】
# レベル2：ロボットカー走行デモ
<hr>

【目標】
#### ラインを検出してロボットカーを自走させる

【画像】<br>
![](./document/robotcar1.jpg)<br>
![](./document/robotcar2.jpg)<br>
![](./document/robotcar3.jpg)<br>
実行環境の構成
* Fabo TYPE1 ロボットカー

【動画】<br>
level2解析動画：[./document/demo1.mp4](./document/demo1.mp4)<br>
走行デモ動画：[./document/demo2.mp4](./document/demo2.mp4)<br>

<hr>

<a name='0'>

【目次】
* [実行方法](#1)
* [トラブルシューティング](#2)
  * Webcamが起動しない
  * 走行中にハンドルが固まった
  * Raspberry Pi3が起動しない
* [ディレクトリとファイルについて](#3)
<hr>

<a name='1'>

## 実行方法
> `git pull https://github.com/FaBoPlatform/RobotCarAI`<br>
> `cd level2_demo`<br>
> `python start_button.py`<br>

青いボタンを押すと走行開始します。<br>
赤いボタンを押すと走行停止します。<br>

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
頻繁に発生する時は、2口USBバッテリーを使うか、level2_demo_socketを試してみてください。<br>
<hr>

#### Raspberry Pi3が起動しない
バッテリーの出力不足が原因として上げられます。<br>
2A以上のモバイルバッテリーを使ってください。<br>

[<ページTOP>](#top)　[<目次>](#0)
<hr>

<a name='3'>

## ディレクトリとファイルについて
* ディレクトリについて
  * document/ ドキュメント関連
  * fabolib/ Fabo製基板関連
  * lib/ SPI,ライン検出ライブラリ
* ファイルについて
  * README.md このファイル
  * run_car.py 自動走行コード
  * start_button.py 開始ボタンコード

[<ページTOP>](#top)　[<目次>](#0)
<hr>
