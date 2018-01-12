# coding: utf-8
# MultiPerceptron
# queueを使った学習
# 学習step数を記録
# 学習データはCSVの代わりにジェネレータを搭載
# 3x11x4のNNモデルに変更
# scoreを追加

import os
_FILE_DIR=os.path.abspath(os.path.dirname(__file__))
import time
import tensorflow as tf
import threading
from sklearn.utils import shuffle
import sys
sys.path.append(_FILE_DIR+'/..')
from generator import LabelGenerator
import numpy as np
import logging

# ログ設定
logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] time:%(created).8f pid:%(process)d pn:%(processName)-10s tid:%(thread)d tn:%(threadName)-10s fn:%(funcName)-10s %(message)s',
)

tf.reset_default_graph()

MODEL_DIR=_FILE_DIR+"/model"
SUMMARY_LOG_DIR=_FILE_DIR+"/log"
if not os.path.exists(MODEL_DIR):
    os.makedirs(MODEL_DIR)

N_NODES_HL1 = 11

DATA_COLS = 3 # センサーの数。left45,front,right45
N_CLASSES = 4 # 予測結果の数。stop,left,forward,right
BATCH_SIZE = 100 # バッチサイズは10〜100前後に
CHUNK_SIZE = BATCH_SIZE*2 # queueで保持するデータ件数

TARGET_STEP = 10000 # ステップ数

TEST_NUM = 10000 # テストデータ件数

generator = LabelGenerator()

def generate_random_train_data(n_rows):
    '''
    ランダムなセンサー値と、それに対応するラベルデータを作成する
    args:
        n_rows: 作成するデータ件数
    return:
        batch_data: センサー値
        batch_target: ラベルデータ
    '''
    csvdata=[]
    # 2m以内のランダムなINT値を作成する
    sensors = np.random.randint(0,200,[n_rows,DATA_COLS])

    for i in range(n_rows):
        generator_result = generator.get_label(sensors[i])
        csvrow = np.hstack((sensors[i],generator_result))
        csvdata.append(csvrow)
    csvdata = np.array(csvdata)

    batch_data = csvdata[0:n_rows,0:DATA_COLS]
    batch_target = csvdata[0:n_rows,DATA_COLS:]
    return batch_data, batch_target

def load_and_enqueue(sess):
    while True:
        try:
            batch_data, batch_target = generate_random_train_data(BATCH_SIZE)
            sess.run(enqueue_op, feed_dict={placeholder_input_data:batch_data, placeholder_input_target:batch_target})
            #logging.debug("running")
        except tf.errors.CancelledError as e:
            break
    print("finished enqueueing")

def weight_variable(shape):
    initial = tf.truncated_normal(shape, stddev=0.1)
    return tf.Variable(initial)

def bias_variable(shape):
    initial = tf.constant(0.1, shape=shape)
    return tf.Variable(initial)

with tf.variable_scope("input"):
    placeholder_input_data = tf.placeholder('float', [None, DATA_COLS], name='input_data') # for load_and_enqueue. use dequeue_op:0 for prediction
    placeholder_input_target = tf.placeholder('float', name='input_target') # for load_and_enqueue. use dequeue_op:1 for prediction
    placeholder_batch_size = tf.placeholder(tf.int32, name='batch_size') # need feed_dict in training sess.run(). don't need for prediction.

with tf.variable_scope("step"):
    placeholder_step = tf.placeholder(tf.int32, name='input_step') # step値入力用
    variable_step = tf.Variable(initial_value=0, name="step") # step記録用
    step_op = variable_step.assign(placeholder_step)

with tf.variable_scope("queue"):
    queue = tf.FIFOQueue(
        capacity=CHUNK_SIZE, # enqueue size
        dtypes=['float', 'float'],
        shapes=[[DATA_COLS], [N_CLASSES]],
        name='FIFOQueue'
    )

    # Enqueue and dequeue operations
    enqueue_op = queue.enqueue_many([placeholder_input_data, placeholder_input_target], name='enqueue_op')
    # dequeue_manyでBATCH_SIZE分のデータを取得する。テストデータや実際に予測時に使う可変個数のデータ件数に対応するためにplaceholderで取得件数を指定する。
    dequeue_input_data, dequeue_input_target = queue.dequeue_many(placeholder_batch_size, name='dequeue_op') # instead of data/target placeholder

with tf.variable_scope('neural_network_model'):
    hidden_1_layer = {'weights':tf.Variable(weight_variable([DATA_COLS, N_NODES_HL1])),
                      'biases':tf.Variable(bias_variable([N_NODES_HL1]))}

    output_layer = {'weights':tf.Variable(weight_variable([N_NODES_HL1, N_CLASSES])),
                    'biases':tf.Variable(bias_variable([N_CLASSES])),}

    l1 = tf.add(tf.matmul(dequeue_input_data,hidden_1_layer['weights']), hidden_1_layer['biases'])
    l1 = tf.nn.relu(l1)

    # 予測結果
    prediction = tf.add(tf.matmul(l1,output_layer['weights']), output_layer['biases'], name='output_y')
    # スコア
    score = tf.nn.softmax(prediction, name='score')

with tf.variable_scope('loss'):
    losses = tf.nn.softmax_cross_entropy_with_logits(logits=prediction, labels=dequeue_input_target)
    loss_op = tf.reduce_mean(losses, name='cost')
    tf.summary.scalar('loss', loss_op)

with tf.variable_scope('accuracy'):
    correct = tf.equal(tf.argmax(prediction, 1), tf.argmax(dequeue_input_target, 1))
    accuracy = tf.reduce_mean(tf.cast(correct, 'float'), name='accuracy')
    tf.summary.scalar('accuracy', accuracy)

summary_op = tf.summary.merge_all()

train_op = tf.train.AdamOptimizer(0.0001).minimize(loss_op, name='train_op')

saver = tf.train.Saver(max_to_keep=100)
test_data, test_target =generate_random_train_data(TEST_NUM)
with tf.Session() as sess:
    ckpt = tf.train.get_checkpoint_state(MODEL_DIR)
    if ckpt:
        # checkpointファイルから最後に保存したモデルへのパスを取得する
        last_model = ckpt.model_checkpoint_path
        print("load {0}".format(last_model))
        # 学習済みモデルを読み込む
        saver.restore(sess, last_model)
    else:
        print("initialization")
        # 初期化処理
        init_op = tf.global_variables_initializer()
        sess.run(init_op)

    writer = tf.summary.FileWriter(SUMMARY_LOG_DIR, sess.graph)
    start_time, start_clock = time.time(), time.clock()

    # 学習データ ジェネレータを用いてミニバッチデータを作成し、enqueue_op実行によりqueueへデータを挿入するスレッドを開始する
    # ミニバッチデータ作成時間より学習時間の方が処理負荷が高いので、データ生成スレッドは1スレッドにする
    for i in range(0,1):
        enqueue_thread = threading.Thread(target=load_and_enqueue, args=[sess])
        enqueue_thread.isDaemon()
        enqueue_thread.start()

    step = 0 # 最後にstep数をモデルに記録するために変数を用意しておく
    try:
        # step取得
        _step = sess.run(variable_step)
        print("learned step:{}".format(_step))
        # 学習開始時点での精度表示
        print(sess.run(accuracy, feed_dict={placeholder_batch_size:BATCH_SIZE}))

        for step in range(_step+1, TARGET_STEP+1):
            batch_loss=0
            w_summary=None
            _, batch_loss, w_summary = sess.run([train_op, loss_op, summary_op],
                                                feed_dict={placeholder_batch_size:BATCH_SIZE})

            if step % 1000 == 0:
                if not w_summary is None:
                    writer.add_summary(w_summary, step)

                ac = sess.run(accuracy, feed_dict={placeholder_batch_size:BATCH_SIZE})

                # テストデータでの精度を確認する
                test_accuracy = accuracy.eval({'queue/dequeue_op:0':test_data,
                                               'queue/dequeue_op:1':test_target})

                if step % 10000 == 0:
                    print("Step:%d accuracy:%.8f test_accuracy:%.8f loss:%.8f time:%.8f clock:%.14f" % (step,ac,test_accuracy,batch_loss,time.time()-start_time,time.clock()-start_clock))

            # 1000000 step毎にsaveする
            if step % 1000000 == 0:
                _step = sess.run(step_op,feed_dict={placeholder_step:step}) # variable_stepにstepを記録する
                saver.save(sess, MODEL_DIR + '/model-'+str(step)+'.ckpt')

        sess.run(queue.close(cancel_pending_enqueues=True))
    except Exception as e:
        # Report exceptions to the coodinator.
        print(e)
    finally:
        pass

    # ステップ学習時、保存する
    if step > _step:
        _step = sess.run(step_op,feed_dict={placeholder_step:step}) # variable_stepにstepを記録する
        saver.save(sess, MODEL_DIR + '/model-'+str(step)+'.ckpt')

    # テストデータを新たに生成し、精度を確認する
    test_data, test_target =generate_random_train_data(TEST_NUM)
    print('Accuracy:',accuracy.eval({dequeue_input_data:test_data,
                                     dequeue_input_target:test_target}))

    # 総step数を表示する
    print('step:{}'.format(sess.run(variable_step)))


print("end")
