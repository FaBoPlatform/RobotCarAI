#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ClientからOpenCV画像データを受け取り、ライン検出して制御命令を送る
# Server: Jetson TX2
# Client: Jetson TX2/Raspberry Pi3 Docker
# 1. FFMPEG UDP StreamingをClientで実行する。Jetson TX2向け30FPS
# 2. Serverを起動する
# 3. Clientを起動する
# コード修正
# lib/camera.py: vid = cv2.VideoCapture()を環境に合わせて修正する必要がある
'''
Python 3.6
    送信するmessageは.encode('ascii')や.encode('utf-8')等でエンコードする必要がる
    ここではClientから送られてくるOpenCV BGR画像データが'ascii'に変換されているので'ascii'で統一している
'''
print("wait. launching...")
import socket, select
import os
import logging
import threading
import numpy as np
from lib.mpfps import FPS
from lib.functions import *
from lib.lane_detection import lane_detection

import numpy as np
from tf_utils import visualization_utils_cv2 as vis_util
from lib.webcam import WebcamVideoStream
from lib.session_worker import SessionWorker
from lib.load_graph import LoadFrozenGraph
from lib.load_label_map import LoadLabelMap
from lib.mpvariable import MPVariable
from lib.functions import draw_text
import time
import sys
import cv2
import tensorflow as tf
import yaml



# ログ設定
logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] time:%(created).8f pid:%(process)d pn:%(processName)-10s tid:%(thread)d tn:%(threadName)-10s fn:%(funcName)-10s %(message)s',
)

# 解析、送信スレッド動作フラグ
is_analyze_running = False

sock = None


def load_config():
    """
    LOAD CONFIG FILE
    Convert config.yml to DICT.
    """
    cfg = None
    if (os.path.isfile('config.yml')):
        with open("config.yml", 'r') as ymlfile:
            cfg = yaml.load(ymlfile)
    else:
        raise FileNotFoundError(("File not found: config.yml"))
    return cfg

def without_visualization(category_index, boxes, scores, classes, cur_frame, det_interval, det_th):
    # Exit after max frames if no visualization
    for box, score, _class in zip(np.squeeze(boxes), np.squeeze(scores), np.squeeze(classes)):
        if cur_frame%det_interval==0 and score > det_th:
            label = category_index[_class]['name']
            print("label: {}\nscore: {}\nbox: {}".format(label, score, box))

def min_class(category_index, scores, classes):
    # check minimum detected class number
    min_class = 100000
    for score, _class in zip(np.squeeze(scores), np.squeeze(classes)):
        if score > 0.5:
            if _class < min_class:
                min_class = _class
    if min_class == 100000:
        return 0
    else:
        return int(min_class)

def visualization(category_index, image, boxes, scores, classes, debug_mode, vis_text, fps_interval):
    # Visualization of the results of a detection.
    vis_util.visualize_boxes_and_labels_on_image_array(
        image,
        np.squeeze(boxes),
        np.squeeze(classes).astype(np.int32),
        np.squeeze(scores),
        category_index,
        use_normalized_coordinates=True,
        line_thickness=8)
    return image

def detection_loop():
    global is_analyze_running
    global sock

    """
    LOAD SETUP VARIABLES
    """
    cfg = load_config()

    """
    START FPS, FPS PRINT
    """
    fps = FPS(cfg)
    fps_counter_proc = fps.start_counter()
    fps_console_proc = fps.start_console()

    """ """ """ """ """ """ """ """ """ """ """
    GET CONFIG
    """ """ """ """ """ """ """ """ """ """ """
    VIDEO_INPUT          = cfg['video_input']
    FORCE_GPU_COMPATIBLE = cfg['force_gpu_compatible']
    VISUALIZE            = cfg['visualize']
    VIS_TEXT             = cfg['vis_text']
    MAX_FRAMES           = cfg['max_frames']
    WIDTH                = cfg['width']
    HEIGHT               = cfg['height']
    FPS_INTERVAL         = cfg['fps_interval']
    DET_INTERVAL         = cfg['det_interval']
    DET_TH               = cfg['det_th']
    SPLIT_MODEL          = cfg['split_model']
    LOG_DEVICE           = cfg['log_device']
    ALLOW_MEMORY_GROWTH  = cfg['allow_memory_growth']
    SSD_SHAPE            = cfg['ssd_shape']
    DEBUG_MODE           = cfg['debug_mode']
    LABEL_PATH           = cfg['label_path']
    NUM_CLASSES          = cfg['num_classes']
    X_METER              = cfg['x_meter']
    Y_METER              = cfg['y_meter']
    cur_frame = 0
    """ """

    """ """ """ """ """ """ """ """ """ """ """
    LOAD FROZEN_GRAPH
    """ """ """ """ """ """ """ """ """ """ """
    load_frozen_graph = LoadFrozenGraph(cfg)
    graph = load_frozen_graph.load_graph()
    """ """

    """ """ """ """ """ """ """ """ """ """ """
    LOAD LABEL MAP
    """ """ """ """ """ """ """ """ """ """ """
    llm = LoadLabelMap()
    category_index = llm.load_label_map(cfg)
    """ """

    """ """ """ """ """ """ """ """ """ """ """
    PREPARE TF CONFIG OPTION
    """ """ """ """ """ """ """ """ """ """ """
    # Session Config: allow seperate GPU/CPU adressing and limit memory allocation
    config = tf.ConfigProto(allow_soft_placement=True, log_device_placement=LOG_DEVICE)
    config.gpu_options.allow_growth = ALLOW_MEMORY_GROWTH
    config.gpu_options.force_gpu_compatible = FORCE_GPU_COMPATIBLE
    #config.gpu_options.per_process_gpu_memory_fraction = 0.01 # 80MB memory is enough to run on TX2
    """ """

    """ """ """ """ """ """ """ """ """ """ """
    PREPARE GRAPH I/O TO VARIABLE
    """ """ """ """ """ """ """ """ """ """ """
    # Define Input and Ouput tensors
    image_tensor = graph.get_tensor_by_name('image_tensor:0')
    detection_boxes = graph.get_tensor_by_name('detection_boxes:0')
    detection_scores = graph.get_tensor_by_name('detection_scores:0')
    detection_classes = graph.get_tensor_by_name('detection_classes:0')
    num_detections = graph.get_tensor_by_name('num_detections:0')

    if SPLIT_MODEL:
        score_out = graph.get_tensor_by_name('Postprocessor/convert_scores:0')
        expand_out = graph.get_tensor_by_name('Postprocessor/ExpandDims_1:0')
        score_in = graph.get_tensor_by_name('Postprocessor/convert_scores_1:0')
        expand_in = graph.get_tensor_by_name('Postprocessor/ExpandDims_1_1:0')
    """ """

    """ """ """ """ """ """ """ """ """ """ """
    START WORKER THREAD
    """ """ """ """ """ """ """ """ """ """ """
    # gpu_worker uses in split_model and non-split_model
    gpu_tag = 'GPU'
    cpu_tag = 'CPU'
    gpu_worker = SessionWorker(gpu_tag, graph, config)
    if SPLIT_MODEL:
        gpu_opts = [score_out, expand_out]
        cpu_worker = SessionWorker(cpu_tag, graph, config)
        cpu_opts = [detection_boxes, detection_scores, detection_classes, num_detections]
    else:
        gpu_opts = [detection_boxes, detection_scores, detection_classes, num_detections]
    """ """

    """ """ """ """ """ """ """ """ """ """ """
    WAIT UNTIL THE FIRST DUMMY IMAGE DONE
    """ """ """ """ """ """ """ """ """ """ """
    print('Loading...')
    loss = 0
    sleep_interval = 0.1
    """
    PUT DUMMY DATA INTO GPU WORKER
    """
    is_dummy_gpu = True
    gpu_feeds = {image_tensor:  [np.zeros((300, 300, 3))]}
    gpu_extras = {}
    gpu_worker.put_sess_queue(gpu_opts, gpu_feeds, gpu_extras)
    if SPLIT_MODEL:
        """
        PUT DUMMY DATA INTO CPU WORKER
        """
        is_dummy_cpu = True
        if SSD_SHAPE == 600:
            shape = 7326
        else:
            shape = 1917

        score = np.zeros((1, shape, NUM_CLASSES))
        expand = np.zeros((1, shape, 1, 4))
        cpu_feeds = {score_in: score, expand_in: expand}
        cpu_extras = {}
        cpu_worker.put_sess_queue(cpu_opts, cpu_feeds, cpu_extras)
    """
    WAIT UNTIL JIT-COMPILE DONE
    """
    while True:
        g = gpu_worker.get_result_queue()
        if g is None:
            time.sleep(sleep_interval)
        else:
            break
    if SPLIT_MODEL:
        while True:
            c = cpu_worker.get_result_queue()
            if c is None:
                time.sleep(sleep_interval)
            else:
                break
    """ """



    """ """ """ """ """ """ """ """ """ """ """
    START CAMERA
    """ """ """ """ """ """ """ """ """ """ """
    video_stream = WebcamVideoStream(VIDEO_INPUT, WIDTH, HEIGHT).start()
    """ """


    """ """ """ """ """ """ """ """ """ """ """
    PREPARE LANE DETECTION
    """ """ """ """ """ """ """ """ """ """ """
    cols = video_stream.cols
    rows = video_stream.rows

    """ """ """ """ """ """ """ """ """ """ """
    CAR PARAMETER
    """ """ """ """ """ """ """ """ """ """ """
    MAX_HANDLE_ANGLE = 42
    max_speed = 40
    str_control = None
    speed = 40
    lane_image = None

    """ """ """ """ """ """ """ """ """ """ """
    DETECTION LOOP
    """ """ """ """ """ """ """ """ """ """ """
    print('Starting Detection')
    sleep_interval = 0.005

    try:
        while video_stream.running and is_analyze_running:
            top_in_time = time.time()
            """
            SPRIT/NON-SPLIT MODEL CAMERA TO WORKER
            """
            if gpu_worker.is_sess_empty(): # must need for speed
                cap_in_time = time.time()
                frame = video_stream.read()
                image_expanded = np.expand_dims(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), axis=0) # np.expand_dims is faster than []
                #image_expanded = np.expand_dims(frame, axis=0) # BGR image for input. Of couse, bad accuracy in RGB trained model, but speed up.
                cap_out_time = time.time()
                # put new queue
                gpu_feeds = {image_tensor: image_expanded}
                if VISUALIZE:
                    gpu_extras = {'image':frame, 'top_in_time':top_in_time, 'cap_in_time':cap_in_time, 'cap_out_time':cap_out_time} # for visualization frame
                else:
                    gpu_extras = {'top_in_time':top_in_time, 'cap_in_time':cap_in_time, 'cap_out_time':cap_out_time}
                gpu_worker.put_sess_queue(gpu_opts, gpu_feeds, gpu_extras)

            g = gpu_worker.get_result_queue()
            if SPLIT_MODEL:
                # if g is None: gpu thread has no output queue. ok skip, let's check cpu thread.
                if g:
                    # gpu thread has output queue.
                    score, expand, extras = g['results'][0], g['results'][1], g['extras']

                    if cpu_worker.is_sess_empty():
                        # When cpu thread has no next queue, put new queue.
                        # else, drop gpu queue.
                        cpu_feeds = {score_in: score, expand_in: expand}
                        cpu_extras = extras
                        cpu_worker.put_sess_queue(cpu_opts, cpu_feeds, cpu_extras)
                    # else: cpu thread is busy. don't put new queue. let's check cpu result queue.
                # check cpu thread.
                q = cpu_worker.get_result_queue()
            else:
                """
                NON-SPLIT MODEL
                """
                q = g
            if q is None:
                """
                SPLIT/NON-SPLIT MODEL
                """
                # detection is not complete yet. ok nothing to do.
                time.sleep(sleep_interval)
                continue

            """
            VISUALIZATION
            """
            vis_in_time = time.time()
            boxes, scores, classes, num, extras = q['results'][0], q['results'][1], q['results'][2], q['results'][3], q['extras']

            image = extras['image']
            str_control = None

            """
            DETECTION RESULT
            """
            detected_min_class = min_class(category_index, scores, classes)
            if detected_min_class == 1:
                # stop
                is_need_header_receive = True
                str_control='0,0,'
                sock.sendall(("CONTROL,"+ str_control).encode('ascii'))
            elif detected_min_class == 2:
                # 10
                max_speed = 40
            elif detected_min_class == 3:
                # 20
                max_speed = 70
            elif detected_min_class == 4:
                # 30
                max_speed = 100


            if VISUALIZE:
                # Visualization of the results of a detection.
                detected_image = visualization(category_index, image, boxes, scores, classes, DEBUG_MODE, VIS_TEXT, FPS_INTERVAL)
            else:
                """
                NO VISUALIZE
                """
                without_visualization(category_index, boxes, scores, classes, cur_frame, DET_INTERVAL, DET_TH)


            """
            LANE DETECTION
            """
            handle_angle = 0
            is_pass = False
            try:
                # detect lane
                is_pass, lane_image, tilt1_deg,tilt2_deg,angle1_deg,angle2_deg,curve1_r,curve2_r, \
                meters_from_center = lane_detection(image, detected_image, X_METER, Y_METER, cols, rows)
                ########################################
                # speed control
                ########################################
                if np.abs(tilt2_deg) > np.abs(tilt1_deg) and np.abs(tilt2_deg) >= 15.0:
                    speed += -1
                else:
                    speed += 1
                if speed > max_speed:
                    speed = max_speed
                elif speed < max_speed - 30:
                    speed = max_speed - 30
                if speed < 40:
                    speed = 40

            except:
                #import traceback
                #traceback.print_exc()
                pass
            if not is_pass and str_control is None:
                # Lane detection failed.
                is_need_header_receive = True
                str_control='0,0,'
                sock.sendall(("CONTROL,"+ str_control).encode('ascii'))

            if VIS_TEXT:
                strings = ["fps: {:.1f}".format(MPVariable.fps.value)]
                colors = [(77, 255, 9)]
                if DEBUG_MODE:
                    """ FOR PERFORMANCE DEBUG """
                    strings += ["fps: {:.1f} 0.2sec".format(MPVariable.fps_snapshot.value)]
                    colors += [(77, 255, 9)]
                if lane_image is not None:
                    draw_text(lane_image, strings, colors)
                else:
                    draw_text(detected_image, strings, colors)

            """
            SHOW
            """
            if lane_image is not None:
                cv2.imshow("Object Detection", lane_image)
                # Press q to quit
                if cv2.waitKey(1) & 0xFF == 113: #ord('q'):
                    MPVariable.running.value = False
                    break
            else:
                cv2.imshow("Object Detection", detected_image)
                # Press q to quit
                if cv2.waitKey(1) & 0xFF == 113: #ord('q'):
                    MPVariable.running.value = False
                    break

            vis_out_time = time.time()

            if str_control is None:
                '''
                左右について
                tilt_deg: -が右、+が左
                angle_deg: +が右、-が左
                meters_from_center: -が右にいる、+が左にいる
                handle_angle: +が右、-が左
                '''
                ########################################
                # ハンドル角調整を行う
                ########################################
                handle_angle = -1*tilt1_deg
                if meters_from_center >= 0:
                    # 左にいる
                    if np.abs(meters_from_center)*100 > 20:
                        # とても離れて左にいる：
                        if tilt2_deg > 0:
                            # 先は左に曲がる：少し左に曲がる
                            handle_angle = -1*MAX_HANDLE_ANGLE/2
                        else:
                            # 先は右に曲がる：右に全開で曲がる
                            handle_angle = 1*MAX_HANDLE_ANGLE
                    elif np.abs(meters_from_center)*100 > 10:
                        if tilt2_deg > 0 :
                            # 離れて左いる、奥は左カーブ：右に少し曲がる
                            handle_angle=MAX_HANDLE_ANGLE/2
                        else:
                            # 離れて左いる、奥は右カーブ：右に全開で曲がる
                            handle_angle=MAX_HANDLE_ANGLE
                else:
                    # 右にいる
                    if np.abs(meters_from_center)*100 > 20:
                        # とても離れて右にいる
                        if tilt2_deg < 0:
                            # 先は右に曲がる：少し右に曲がる
                            handle_angle = 1*MAX_HANDLE_ANGLE/2
                        else:
                            # 先は左に曲がる：左に全開で曲がる
                            handle_angle = -1*MAX_HANDLE_ANGLE
                    elif np.abs(meters_from_center)*100 > 10:
                        if tilt2_deg < 0 :
                            # 離れて右いる、奥は右カーブ：左に少し曲がる
                            handle_angle=-1*MAX_HANDLE_ANGLE/2
                        else:
                            # 離れて右いる、奥は左カーブ、左に全開で曲がる
                            handle_angle=-1*MAX_HANDLE_ANGLE

                # 動作可能な角度内に調整する
                if handle_angle > MAX_HANDLE_ANGLE:
                    handle_angle = MAX_HANDLE_ANGLE
                if handle_angle < -1*MAX_HANDLE_ANGLE:
                    handle_angle = -1*MAX_HANDLE_ANGLE

                # 車両制御送信
                str_control=str(speed)+','+str(handle_angle)+','
                #print("speed={},handle_angle={},CONTROL,{}".format(speed,handle_angle,str_control))
                sock.sendall(("CONTROL,"+ str_control).encode('ascii'))


            """
            PROCESSING TIME
            """
            top_in_time = extras['top_in_time']
            cap_proc_time = extras['cap_out_time'] - extras['cap_in_time']
            gpu_proc_time = extras[gpu_tag+'_out_time'] - extras[gpu_tag+'_in_time']
            if SPLIT_MODEL:
                cpu_proc_time = extras[cpu_tag+'_out_time'] - extras[cpu_tag+'_in_time']
            else:
                cpu_proc_time = 0
            vis_proc_time = vis_out_time - vis_in_time
            lost_proc_time = vis_out_time - top_in_time - cap_proc_time - gpu_proc_time - cpu_proc_time - vis_proc_time
            total_proc_time = vis_out_time - top_in_time
            MPVariable.cap_proc_time.value += cap_proc_time
            MPVariable.gpu_proc_time.value += gpu_proc_time
            MPVariable.cpu_proc_time.value += cpu_proc_time
            MPVariable.vis_proc_time.value += vis_proc_time
            MPVariable.lost_proc_time.value += lost_proc_time
            MPVariable.total_proc_time.value += total_proc_time

            if DEBUG_MODE:
                if SPLIT_MODEL:
                    sys.stdout.write('snapshot FPS:{: ^5.1f} total:{: ^10.5f} cap:{: ^10.5f} gpu:{: ^10.5f} cpu:{: ^10.5f} vis:{: ^10.5f} lost:{: ^10.5f}\n'.format(
                        MPVariable.fps.value, total_proc_time, cap_proc_time, gpu_proc_time, cpu_proc_time, vis_proc_time, lost_proc_time))
                else:
                    sys.stdout.write('snapshot FPS:{: ^5.1f} total:{: ^10.5f} cap:{: ^10.5f} gpu:{: ^10.5f}  vis:{: ^10.5f} lost:{: ^10.5f}\n'.format(
                        MPVariable.fps.value, total_proc_time, cap_proc_time, gpu_proc_time, vis_proc_time, lost_proc_time))
            """ """

            """
            EXIT WITHOUT GUI
            """
            if not VISUALIZE:
                if cur_frame >= MAX_FRAMES:
                    MPVariable.running.value = False
                    break
                cur_frame += 1
            """
            CHANGE SLEEP INTERVAL
            """
            if MPVariable.frame_counter.value == 0 and MPVariable.fps.value > 0:
                sleep_interval = 1.0 / MPVariable.fps.value / 10.0
                MPVariable.sleep_interval.value = sleep_interval

            MPVariable.frame_counter.value += 1
        """
        END while
        """
    except:
        import traceback
        traceback.print_exc()

    finally:
        """ """ """ """ """ """ """ """ """ """ """
        CLOSE
        """ """ """ """ """ """ """ """ """ """ """
        MPVariable.running.value = False
        gpu_worker.stop()
        if SPLIT_MODEL:
            cpu_worker.stop()
        video_stream.stop()

        if VISUALIZE:
            cv2.destroyAllWindows()

        fps_counter_proc.join()
        fps_console_proc.join()
        """ """

    return



def main():
    global is_analyze_running
    global sock
    global out

    # 通信設定
    HOST = '192.168.0.76' # Server IP Address
    PORT = 6666 # Server TCP Port
    #HOST = 'a32158c3da9f' # AWS Docker
    #PORT = 8091 # AWS TCP Port
    #HOST = '2204f9b0e871' # PC Docker
    #PORT = 8091 # PC TCP Port

    ########################################
    # 通信準備
    ########################################
    connected_clients_sockets = []
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(10)
    connected_clients_sockets.append(server_socket)
    # Headerの受信が必要かどうか。Headerを受信したら、encode('ascii')を通さずに受信データを解析する
    is_need_header_receive = True

    print("Server start")
    try:

        while True:
            ########################################
            # 受信待ち
            ########################################
            read_sockets, write_sockets, error_sockets = select.select(connected_clients_sockets, [], [])

            for sock in read_sockets:
                if sock == server_socket:
                    sockfd, client_address = server_socket.accept()
                    connected_clients_sockets.append(sockfd)
                else:
                    # ClientがServerにHeaderを送る時は4096 Byte以下にすること
                    packet = sock.recv(4096)
                    #print(type(packet))
                    # 
                    if is_need_header_receive:
                        print('header')
                        packet = packet.decode('ascii')
                        txt = str(packet)
                        if packet:
                            print('packet True')
                            if packet == 'START':
                                is_analyze_running = True
                                t = threading.Thread(target=detection_loop)
                                t.setDaemon(True)
                                t.start()
                            elif packet.startswith('BYE'):
                                print('got BYE')
                                is_need_header_receive = True
                                is_analyze_running = False
                                sock.shutdown(socket.SHUT_RDWR)
                                sock.close()
                                connected_clients_sockets.remove(sock)
                        else:
                            print('client disconnect')
                            is_need_header_receive = True
                            is_analyze_running = False
                            sock.shutdown(socket.SHUT_RDWR)
                            sock.close()
                            connected_clients_sockets.remove(sock)
                    if not is_need_header_receive:
                        # ここには来ない
                        print('body')
                        if packet:
                            print('packet True')
                            is_need_header_receive = True
                        else:
                            print('data finished')
                            is_need_header_receive = True
                            is_analyze_running = False
                            sock.shutdown(socket.SHUT_RDWR)
                            sock.close()
                            connected_clients_sockets.remove(sock)

    except:
        import traceback
        traceback.print_exc()
    finally:
        is_need_header_receive = True
        is_analyze_running = False
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()
        connected_clients_sockets.remove(sock)
        server_socket.close()

if __name__ == '__main__':
    main()
    print("end server")
