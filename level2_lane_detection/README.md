<a name='top'>

【タイトル】
# レベル2：OpenCVでラインを検出する
<hr>

【目標】
#### 映像から、ラインを検出する

【画像】<br>
![](./document/result_frame_1.jpg)<br>

【動画】<br>
入力動画：[./demo_lane/input4.mp4](./demo_lane/input4.mp4)<br>
出力動画：[./document/result_input4.mp4](./document/result_input4.mp4)<br>

【参考】<br>
Programmatic lane finding: [https://github.com/BillZito/lane-detection](https://github.com/BillZito/lane-detection)
level4:OpenCVでレーン検出する: [level4_lane_detection](../level4_lane_detection)
<hr>

<a name='0'>

【目次】
* [実行方法](#1)
* [処理について](#2)
* [ディレクトリとファイルについて](#3)

<a name='1'>

## 実行方法
> `git pull https://github.com/FaBoPlatform/RobotCarAI`<br>
> `cd level2_lane_detection`<br>
> `python opencv_lane_detection.py`<br>

./demo_lane/capture.mp4を読み込み、白線で出来たラインを検出して車両に与えるためのハンドル角度を描画します。<br>
検出結果は./output/result_capture.aviに保存されます。

自分のライン動画で検出する場合、視点変更、ラインの色抽出を調整する必要があります。<br>
関心領域の確認<br>
> `python to_region_of_interest.py`<br>

視点の確認<br>
> `python to_inverse_perspective_mapping.py`<br>

白色抽出の確認<br>
> `python to_white.py`<br>

<hr>

<a name='2'>

## 処理について
処理方法はlevel4:OpenCVでレーン検出する: [level4_lane_detection](../level4_lane_detection)と同じ流れになります。<br>
level4を1本線の処理に修正したものになるため、処理についてはlevel4を参考にしてください。<br>

[<ページTOP>](#top)　[<目次>](#0)
<hr>

<a name='3'>
## [ディレクトリとファイルについて]
* ディレクトリについて
  * documment/ ドキュメント関連
  * demo_lane/ デモ用ディレクトリ
  * lib/ 関数ライブラリ
  * test_images/ ROI,IPM,白色フィルタの確認用ディレクトリ
  * output/ 出力用ディレクトリ(実行時に作成)
* ファイルについて
  * README.md このファイル
  * opencv_lane_detection.py ライン検出コード
  * to_region_of_interest.py ROI座標確認コード
  * to_inverse_perspective_mapping.py IPM座標確認コード
  * to_white.py 白色フィルタ確認コード
