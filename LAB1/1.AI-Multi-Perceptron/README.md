# AI学習、実行の単体コード

3つの距離センサー値から進行方向を判断するための手本となる学習用データ(../TrainData/car_sensor_train_data.csv)を用いて、
1. train_car_lidar_queue.py:
  Multi-PerceptronのNNモデルに学習させます
2. freeze_graph.py:
  学習結果をprotocol buffer形式のファイル(../model_car_lidar/car_lidar_queue_20000.pb)に変換します
3. run_car_lidar.py:
  予測コードで動作確認を行います

train_car_lidar_queue.log: 20000ステップ学習時のログ。

この予測コードでは実際の距離センサーの代わりにnumpyを用いた[0-1000]の範囲のランダムなint値を与えて予測コードの動作確認を行っています。

run_car_lidar.py:
```python
        # ランダム予測
        # sensors = [[LEFT45,FRONT,RIGHT45]] # unsigned int value
        sensors = np.array([np.random.randint(0,1000,3)])
        
        # max_value = [[N]] # N = 0:STOP,1:LEFT,2:FORWARD,3:RIGHT
        _output_y = sess.run(output_y,feed_dict={input_x:sensors})
        max_value = np.argmax(_output_y) # max_value
```

## train_car_lidar_queue.pyのポイント
* 一般的な3層Multi-PerceptronのNNモデルをqueueを用いて分散効率を上げ、学習にかかる時間を短縮。
* ミニバッチに用いるデータ数は10-100程度に抑えて、特徴量を算出しやすくしておく。
* 予測で利用するinput/outputにはわかりやすいように名前を付けておく。
* ここではinputにqueue/dequeue_op、outputにneural_network_model/output_y、精度にaccuracy/accuracyの名前が付くように指定している。

## freeze_graph.pyのポイント
* 予測で利用するinput/outputを指定することで、それを使うために必要な部分だけがpbファイルに保存されるため、予測時には不要な学習のためのグラフを除去した小さいサイズの学習済みモデルのファイルを作ることが出来る。
* 学習時に保存したcheckpointファイルを読み込み、グラフに学習済み値がある状態でpbファイルを作るため、確実に学習済み値がpbファイルに保存される。
* checkpointファイルはどんなNNモデルで作成したものであってもよいため、NNモデルが持つオペレーションの一覧をprint_graph_operations(graph)で表示し、目視確認できるようにしてある。

## ran_car_lidar.pyのポイント
* pbファイルから利用するinput/outputをget_tensor_by_name()でグラフから取得し、sess.run()でセンサー値をinputに与えた時に、どの進行方向に進むといいのかを予測する。
* 実際のセンサー値の代わりにnumpyを用いた[0-1000]の範囲のランダムなint値をinputに与えている。