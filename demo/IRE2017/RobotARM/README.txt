CNNでモデルを作成しておく。
出来たモデルをfreeze_graph.pyでcnn_model.pbファイルに変換し、modelディレクトリに設置する。
./model/cnn_model.pb

【起動方法】
・ボタン起動
python start_button.py


【テスト】
・AI分類確認
python test/run_ai_test.py

・モデル評価
python test/model_test.py

・アーム動作確認
python run_arm_test.py

・ボタン動作確認
python run_button_test.py

・LED動作確認
python run_led_test.py

・サーボ動作確認
python run_servo_test.py

