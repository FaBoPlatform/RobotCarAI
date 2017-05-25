# -*- coding: utf-8 -*-
# MultiPerceptron
# queueを使った学習

import os
import time
import pandas as pd
import tensorflow as tf
import tensorflow.contrib.slim as slim
import threading
from sklearn.utils import shuffle

tf.reset_default_graph()

MODEL_DIR = "../model_car_lidar_queue"
if not os.path.exists(MODEL_DIR):
    os.makedirs(MODEL_DIR)

n_nodes_hl1 = 500
n_nodes_hl2 = 500
n_nodes_hl3 = 500

data_cols = 3 # センサーの数。left45,front,right45
n_classes = 4 # 予測結果の数。stop,left,forward,right
batch_size = 100 # バッチサイズは10〜100前後に
chunk_size = 100 # FIFOQueueのcapacity

TRAIN_NUM=100000 # 学習データの行数
TRAIN_START_INDEX=0
TRAIN_END_INDEX=batch_size
TRAIN_INDEX_I=0
# 学習データを読み込み pandasで読み込みnumpy.ndarrayに変換する
csv_file="../train_data/car_sensor_train_data.csv"
train_dataset = pd.io.parsers.read_csv(csv_file, header = 0, float_precision = "high").values
def next_train_data(batch_size):
    global TRAIN_START_INDEX
    global TRAIN_END_INDEX
    global TRAIN_NUM
    global TRAIN_INDEX_I
    global train_dataset

    if len(train_dataset) < TRAIN_NUM:
        TRAIN_NUM = len(train_dataset)

    TRAIN_START_INDEX=TRAIN_INDEX_I*batch_size
    TRAIN_END_INDEX=TRAIN_START_INDEX + batch_size
    if TRAIN_NUM < TRAIN_START_INDEX:
        TRAIN_START_INDEX=0
        TRAIN_END_INDEX=TRAIN_START_INDEX + batch_size
        TRAIN_INDEX_I=0
    if TRAIN_NUM < TRAIN_END_INDEX:
        TRAIN_END_INDEX=TRAIN_NUM

    TRAIN_INDEX_I+=1

    if TRAIN_START_INDEX==0:
        # 先頭に戻った時は学習データをシャッフルする
        train_dataset = shuffle(train_dataset, random_state=42) # shuffle train data

    batch_data = train_dataset[TRAIN_START_INDEX:TRAIN_END_INDEX,0:data_cols]
    batch_target = train_dataset[TRAIN_START_INDEX:TRAIN_END_INDEX,data_cols:]
    return batch_data, batch_target


TEST_NUM=820000 # テストデータの行数
TEST_START_INDEX=0
TEST_END_INDEX=batch_size
TEST_INDEX_I=0
# csv読み込み pandasで読み込みnumpy.ndarrayに変換する
csv_file="../train_data/car_sensor_test_data.csv"
test_dataset = pd.io.parsers.read_csv(csv_file, header = 0, float_precision = "high").values
def next_test_data(batch_size):
    global TEST_START_INDEX
    global TEST_END_INDEX
    global TEST_NUM
    global TEST_INDEX_I
    global test_dataset

    if len(test_dataset) < TEST_NUM:
        TEST_NUM = len(test_dataset)

    TEST_START_INDEX=TEST_INDEX_I*batch_size
    TEST_END_INDEX=TEST_START_INDEX + batch_size
    if TEST_NUM < TEST_START_INDEX:
        TEST_START_INDEX=0
        TEST_END_INDEX=TEST_START_INDEX + batch_size
        TEST_INDEX_I=0
    if TEST_NUM < TEST_END_INDEX:
        TEST_END_INDEX=TEST_NUM

    TEST_INDEX_I+=1

    # テストデータは精度検証用なのでシャッフルは不要
    batch_data = test_dataset[TEST_START_INDEX:TEST_END_INDEX,0:data_cols]
    batch_target = test_dataset[TEST_START_INDEX:TEST_END_INDEX,data_cols:]
    return batch_data, batch_target


def load_and_enqueue(sess):
    while True:
        try:
            batch_data, batch_target = next_train_data(batch_size)
            sess.run(enqueue_op, feed_dict={placeholder_input_data:batch_data, placeholder_input_target:batch_target})
        except tf.errors.CancelledError as e:
            break
    print("finished enqueueing")

with tf.variable_scope("input"):
    placeholder_input_data = tf.placeholder('float', [None, data_cols], name='input_data') # for load_and_enqueue. use dequeue_data_op for prediction
    placeholder_input_target = tf.placeholder('float', name='input_target') # for load_and_enqueue. use dequeue_target_op for prediction
    placeholder_batch_size = tf.placeholder(tf.int32, name='batch_size') # need feed_dict in training sess.run(). don't need for prediction.

with tf.variable_scope("queue"):
    queue = tf.FIFOQueue(
        capacity=chunk_size, # enqueue size
        dtypes=['float', 'float'],
        shapes=[[data_cols], [n_classes]],
        name='FIFOQueue'
    )

    # Enqueue and dequeue operations
    enqueue_op = queue.enqueue_many([placeholder_input_data, placeholder_input_target], name='enqueue_op')
    dequeue_data_op, dequeue_target_op = queue.dequeue_many(placeholder_batch_size, name='dequeue_op') # instead of data/target placeholder


with tf.variable_scope('neural_network_model'):
    hidden_1_layer = {'weights':tf.Variable(tf.random_normal([data_cols, n_nodes_hl1])),
                      'biases':tf.Variable(tf.random_normal([n_nodes_hl1]))}

    hidden_2_layer = {'weights':tf.Variable(tf.random_normal([n_nodes_hl1, n_nodes_hl2])),
                      'biases':tf.Variable(tf.random_normal([n_nodes_hl2]))}

    hidden_3_layer = {'weights':tf.Variable(tf.random_normal([n_nodes_hl2, n_nodes_hl3])),
                      'biases':tf.Variable(tf.random_normal([n_nodes_hl3]))}

    output_layer = {'weights':tf.Variable(tf.random_normal([n_nodes_hl3, n_classes])),
                    'biases':tf.Variable(tf.random_normal([n_classes])),}


    l1 = tf.add(tf.matmul(dequeue_data_op,hidden_1_layer['weights']), hidden_1_layer['biases'])
    l1 = tf.nn.relu(l1)

    l2 = tf.add(tf.matmul(l1,hidden_2_layer['weights']), hidden_2_layer['biases'])
    l2 = tf.nn.relu(l2)

    l3 = tf.add(tf.matmul(l2,hidden_3_layer['weights']), hidden_3_layer['biases'])
    l3 = tf.nn.relu(l3)

    # 予測結果
    prediction = tf.add(tf.matmul(l3,output_layer['weights']), output_layer['biases'], name='output_y')

with tf.variable_scope('loss'):
    losses = tf.nn.softmax_cross_entropy_with_logits(logits=prediction, labels=dequeue_target_op)
    loss_op = tf.reduce_mean(losses, name='cost')

with tf.variable_scope('accuracy'):
    correct = tf.equal(tf.argmax(prediction, 1), tf.argmax(dequeue_target_op, 1))
    accuracy = tf.reduce_mean(tf.cast(correct, 'float'), name='accuracy')
    accuracy = tf.Print(accuracy, data=[accuracy], message="accuracy:")


train_op = tf.train.AdamOptimizer(0.0001).minimize(loss_op, name='train_op')
max_step = 10
num_batchs = int(TRAIN_NUM/batch_size)

saver = tf.train.Saver()
test_data, test_target =next_test_data(820000)
with tf.Session() as sess:
    ckpt = tf.train.get_checkpoint_state(MODEL_DIR)
    if ckpt:
        # checkpointファイルから最後に保存したモデルへのパスを取得する
        last_model = ckpt.model_checkpoint_path
        print(("load {0}".format(last_model)))
        # 学習済みモデルを読み込む
        saver.restore(sess, last_model)
        LOAD_MODEL = True
    else:
        print("initialization")
        # 初期化処理
        init_op = tf.global_variables_initializer()
        sess.run(init_op)

    start_time, start_clock = time.time(), time.clock()

    # Start a thread to enqueue data asynchronously, and hide I/O latency.
    coord = tf.train.Coordinator()
    enqueue_thread = threading.Thread(target=load_and_enqueue, args=[sess])
    enqueue_thread.isDaemon()
    enqueue_thread.start()
    threads = tf.train.start_queue_runners(coord=coord, sess=sess)
    try:
        # check the accuracy before training (without feed_dict!)
        print sess.run(accuracy, feed_dict={placeholder_batch_size:chunk_size}) # check batch_size's data
        for step in range(max_step):
            batch_loss=0
            for batch_step in range(num_batchs): # 分割したミニバッチを全て実行する
                _, loss = sess.run([train_op, loss_op],
                                   feed_dict={placeholder_batch_size:batch_size})
                batch_loss += loss
            ac = sess.run(accuracy, feed_dict={placeholder_batch_size:chunk_size}) # check batch_size's data

            # 全テストデータでの精度を確認する
            full_test_accuracy = accuracy.eval({'queue/dequeue_op:0':test_data,
                                                'queue/dequeue_op:1':test_target})
            print("Step:%d batch_step:%d accuracy:%.8f full_accuracy:%.8f loss:%.8f time:%.8f clock:%.14f" % (step,batch_step,ac,full_test_accuracy,batch_loss,time.time()-start_time,time.clock()-start_clock))

        sess.run(queue.close(cancel_pending_enqueues=True))
    except Exception, e:
        # Report exceptions to the coodinator.
        print(e)
        coord.request_stop(e)
    finally:
        coord.request_stop()
        coord.join(threads)

    saver.save(sess, MODEL_DIR + '/model.ckpt')


    # 全学習データでの精度を確認する
    test_data, test_target =next_train_data(TRAIN_NUM)
    print('Accuracy:',accuracy.eval({dequeue_data_op:test_data,
                                     dequeue_target_op:test_target}))



print("end")
