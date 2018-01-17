<a name='top'>

【タイトル】
# レベル1：ロボットカー走行デモ
<hr>

【目標】
#### 3つの距離センサーから値を取得し、Neaural Networksで進行方向を判断してロボットカーを自走させる

【画像】<br>
![](./document/robotcar.jpg)<br>
実行環境の構成
* Fabo TYPE1 ロボットカー

【動画】<br>
走行デモ動画：[./document/demo1.mp4](./document/demo1.mp4)<br>

<hr>

<a name='0'>

【目次】
* [必要なコードとファイル](#1)
* [Python] [level0の自走コードを元に修正する](#2)
  * Neural Networksの判断処理を追加する
  * 開始ボタン
* [ディレクトリとファイルについて](#3)
<hr>

<a name='1'>

## 必要なコードとファイル
走行に必要なコードは以下になります。<br>
* ライブラリ
  * ./fabolib/以下
  * ./lib/以下
* 学習済みモデル
  * ./model/以下
* 実行コード
  * start_button.py 開始ボタンコード
  * run_car_ai.py level0のrun_car_if.pyを元に修正

[<ページTOP>](#top)　[<目次>](#0)
<hr>

<a name='2'>

## [Python] level0の自走コードを元に修正する
#### Neural Networksの判断処理を追加する
AI判断を追加し、ジェネレータの判断は不要なのでコメントアウトしておきます。<br>

車両自走コード：[./run_car_ai.py](./run_car_ai.py)<br>
```python
from lib import AI
#from generator import LabelGenerator
...
    # AI準備
    ai = AI("car_model_100M.pb")
    SCORE = 0.6 # スコア閾値
    # IF準備 (学習ラベル ジェネレータ)
    #generator = LabelGenerator()
...
            ########################################
            # AI予測結果を取得する
            ########################################
            # 今回の予測結果を取得する
            ai_value = ai.get_prediction(sensors,SCORE)

            print("ai_value:{} {}".format(ai_value,sensors))
            # 予測結果のスコアが低い時は何もしない
            if ai_value == ai.get_other_label():
                time.sleep(LIDAR_INTERVAL)
                continue

            ########################################
            # IF結果を取得する
            ########################################
            # 今回の結果を取得する
            #generator_result = generator.get_label(sensors)
            #ai_value = np.argmax(generator_result)
```

開始ボタンコードも修正します。<br>
開始ボタンコード：[./start_button.py](./start_button.py)
```python
    cmd = "python "+os.path.abspath(os.path.dirname(__file__))+"/run_car_ai.py"
```

あとはlevel0同様に開始ボタンコードを実行します。<br>
> `python start_button.py`<br>

[<ページTOP>](#top)　[<目次>](#0)
<hr>

<a name='3'>

## ディレクトリとファイルについて
* ディレクトリについて
  * document/ ドキュメント関連
  * fabolib/ Fabo製基板関連
  * lib/ SPI,AIライブラリ
* ファイルについて
  * README.md このファイル
  * run_ai_ai.py 自動走行コード
  * start_button.py 開始ボタンコード

[<ページTOP>](#top)　[<目次>](#0)
<hr>


