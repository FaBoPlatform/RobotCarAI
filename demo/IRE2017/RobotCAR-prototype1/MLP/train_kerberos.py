# coding: utf-8
# MultiPerceptron
# queueを使った学習
# 学習step数を記録
# 学習データはCSVの代わりにジェネレータを搭載
# 3x11x4のNNモデルに変更
# scoreを追加

import os
import time
import tensorflow as tf
import threading
from sklearn.utils import shuffle
import sys
sys.path.append('./')
import sensordatagenerator
import numpy as np

tf.reset_default_graph()

MODEL_DIR=os.path.abspath(os.path.dirname(__file__))+"/model"
SUMMARY_LOG_DIR=os.path.abspath(os.path.dirname(__file__))+"/log"
if not os.path.exists(MODEL_DIR):
    os.makedirs(MODEL_DIR)

n_nodes_hl1 = 11

data_cols = 3 # センサーの数。left45,front,right45
n_classes = 4 # 予測結果の数。stop,left,forward,right
batch_size = 100 # バッチサイズは10〜100前後に
chunk_size = 100 # FIFOQueueのcapacity

target_step = 10000000 # ステップ数

TEST_NUM = 10000 # テストデータ件数

sg = sensordatagenerator.SensorGenerator()
def generate_random_train_data(batch_size):
    CSVDATA=[]
    # 全体的に学習させる 100万step
    #sensors = np.random.randint(0,1000,[batch_size,3])
    # 停止付近だけを集中的に学習させる 100万step
    #LEFT45 = np.random.randint(0,1000,batch_size)
    #FRONT = np.random.randint(0,20,batch_size)
    #RIGHT45 = np.random.randint(0,1000,batch_size)
    # 左右判定だけを集中的に学習させる 100万step
    #LEFT45 = np.random.randint(0,100,batch_size)
    #FRONT = np.random.randint(20,200,batch_size)
    #RIGHT45 = np.random.randint(0,100,batch_size)
    # 近距離全体的に学習させる 1000万step
    #LEFT45 = np.random.randint(0,200,batch_size)
    #FRONT = np.random.randint(0,200,batch_size)
    #RIGHT45 = np.random.randint(0,200,batch_size)
    # 近距離だけを集中的に学習させる 100万step
    #LEFT45 = np.random.randint(0,100,batch_size)
    #FRONT = np.random.randint(0,100,batch_size)
    #RIGHT45 = np.random.randint(0,100,batch_size)
    # 全体的に学習させる 200万step
    sensors = np.random.randint(0,200,[batch_size,3])

    #sensors = np.c_[LEFT45,FRONT,RIGHT45]
        
    for i in range(batch_size):
        CONTRES = sg.driving_instruction(sensors[i])
        CSVROW = np.hstack((sensors[i],CONTRES[0:4]))
        CSVDATA.append(CSVROW)
    CSVDATA = np.array(CSVDATA)

    batch_data = CSVDATA[0:batch_size,0:data_cols]
    batch_target = CSVDATA[0:batch_size,data_cols:]
    return batch_data, batch_target    


def load_and_enqueue(sess):
    while True:
        try:
            batch_data, batch_target = generate_random_train_data(batch_size)
            sess.run(enqueue_op, feed_dict={placeholder_input_data:batch_data, placeholder_input_target:batch_target})
        except tf.errors.CancelledError as e:
            break
    print("finished enqueueing")

with tf.variable_scope("input"):
    placeholder_input_data = tf.placeholder('float', [None, data_cols], name='input_data') # for load_and_enqueue. use dequeue_data_op for prediction
    placeholder_input_target = tf.placeholder('float', name='input_target') # for load_and_enqueue. use dequeue_target_op for prediction
    placeholder_batch_size = tf.placeholder(tf.int32, name='batch_size') # need feed_dict in training sess.run(). don't need for prediction.


with tf.variable_scope("step"):
    placeholder_step = tf.placeholder(tf.int32, name='input_step') # step値入力用
    variable_step = tf.Variable(initial_value=0, name="step") # step記録用
    step_op = variable_step.assign(placeholder_step)

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

    output_layer = {'weights':tf.Variable(tf.random_normal([n_nodes_hl1, n_classes])),
                    'biases':tf.Variable(tf.random_normal([n_classes])),}


    l1 = tf.add(tf.matmul(dequeue_data_op,hidden_1_layer['weights']), hidden_1_layer['biases'])
    l1 = tf.nn.relu(l1)

    # 予測結果
    prediction = tf.add(tf.matmul(l1,output_layer['weights']), output_layer['biases'], name='output_y')
    # スコア
    score = tf.nn.softmax(prediction, name='score')

with tf.variable_scope('loss'):
    losses = tf.nn.softmax_cross_entropy_with_logits(logits=prediction, labels=dequeue_target_op)
    loss_op = tf.reduce_mean(losses, name='cost')
    tf.summary.scalar('loss', loss_op)

with tf.variable_scope('accuracy'):
    correct = tf.equal(tf.argmax(prediction, 1), tf.argmax(dequeue_target_op, 1))
    accuracy = tf.reduce_mean(tf.cast(correct, 'float'), name='accuracy')
    tf.summary.scalar('accuracy', accuracy)

summary_op = tf.summary.merge_all()

train_op = tf.train.AdamOptimizer(0.0001).minimize(loss_op, name='train_op')

saver = tf.train.Saver(max_to_keep=1000)
test_data, test_target =generate_random_train_data(TEST_NUM)
with tf.Session() as sess:
    ckpt = tf.train.get_checkpoint_state(MODEL_DIR)
    if ckpt:
        # checkpointファイルから最後に保存したモデルへのパスを取得する
        last_model = ckpt.model_checkpoint_path
        print("load {0}".format(last_model))
        # 学習済みモデルを読み込む
        saver.restore(sess, last_model)
        LOAD_MODEL = True
    else:
        print("initialization")
        # 初期化処理
        init_op = tf.global_variables_initializer()
        sess.run(init_op)

    writer = tf.summary.FileWriter(SUMMARY_LOG_DIR, sess.graph)        
    start_time, start_clock = time.time(), time.clock()

    # Start a thread to enqueue data asynchronously, and hide I/O latency.
    coord = tf.train.Coordinator()
    enqueue_thread = threading.Thread(target=load_and_enqueue, args=[sess])
    enqueue_thread.isDaemon()
    enqueue_thread.start()
    threads = tf.train.start_queue_runners(coord=coord, sess=sess)
    step = 0 # 最後にstep数をモデルに記録するために変数を用意しておく
    try:
        # check the accuracy before training (without feed_dict!)
        print(sess.run(accuracy, feed_dict={placeholder_batch_size:chunk_size})) # check batch_size's data
        # step取得
        _step = sess.run(variable_step)
        print("learned step:{}".format(_step))
        for step in range(_step+1, target_step+1):
            batch_loss=0
            w_summary=None
            _, batch_loss, w_summary = sess.run([train_op, loss_op, summary_op],
                                          feed_dict={placeholder_batch_size:batch_size})

            if step % 1000 == 0:
                if not w_summary is None:
                    writer.add_summary(w_summary, step)

                ac = sess.run(accuracy, feed_dict={placeholder_batch_size:chunk_size}) # check batch_size's data

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
        coord.request_stop(e)
    finally:
        coord.request_stop()
        coord.join(threads)

    _step = sess.run(step_op,feed_dict={placeholder_step:step}) # variable_stepにstepを記録する
    saver.save(sess, MODEL_DIR + '/model-'+str(step)+'.ckpt')


    # テストデータを新たに生成し、精度を確認する
    test_data, test_target =generate_random_train_data(TEST_NUM)
    print('Accuracy:',accuracy.eval({dequeue_data_op:test_data,
                                     dequeue_target_op:test_target}))

    # 総step数を表示する
    print('step:{}'.format(sess.run(variable_step)))


print("end")
