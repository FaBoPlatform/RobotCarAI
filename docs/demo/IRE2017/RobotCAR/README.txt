MLPでモデルを作成しておく。
出来たモデルをfreeze_graph.pyでcar_model.pbファイルに変換し、modelディレクトリに設置する。
./model/car_model.pb
モデルの読み込みは./lib/ai.pyで行っている

【起動方法】
・ボタン起動
python start_button.py
・起動ボタン無しでの起動
python run_car_ai.py


【テスト】
・近接センサ取得確認
python test/kerberos_test.py
python test/kerberoslib_test.py

・サーボ,モーター動作確認
python motor_test.py
python car_test.py


