# -*- coding: utf-8 -*-
# frozen_model.pbファイルを読み込む

import tensorflow as tf
import numpy as np
import time
import os
import cv2
import random
import sys
sys.path.append('/home/ubuntu/notebooks/github/SSD-Tensorflow/')

from nets import ssd_vgg_300, np_methods

class ObjectDetection():
    MODEL_DIR="/home/ubuntu/notebooks/github/SSD-Tensorflow/model"
    FROZEN_MODEL_NAME="ssd_roadsign.pb"

    sess = None
    cv_bgr=None

    def __init__(self):
        tf.reset_default_graph()

        # TensorFlow session: grow memory when needed. TF, DO NOT USE ALL MY GPU MEMORY!!!
        gpu_options = tf.GPUOptions(allow_growth=True)
        #gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.333)
        config = tf.ConfigProto(log_device_placement=False, gpu_options=gpu_options)
        graph = self.load_graph(os.path.join(self.MODEL_DIR,self.FROZEN_MODEL_NAME))
        graph_def = graph.as_graph_def()

        # print operations
        self.print_graph_operations(graph)

        # print nodes
        #print_graph_nodes(graph_def)

        ####################
        self.input_x = graph.get_tensor_by_name('prefix/input_x:0')
        # 非常に粗いconv10_2とconv11_2を削ってもよい
        self.predictions= [graph.get_tensor_by_name('prefix/ssd_300_vgg/block4_cls_pred/softmax/Reshape_1:0'),
                      graph.get_tensor_by_name('prefix/ssd_300_vgg/block7_cls_pred/softmax/Reshape_1:0'),
                      graph.get_tensor_by_name('prefix/ssd_300_vgg/block8_cls_pred/softmax/Reshape_1:0'),
                      graph.get_tensor_by_name('prefix/ssd_300_vgg/block9_cls_pred/softmax/Reshape_1:0'),
                      graph.get_tensor_by_name('prefix/ssd_300_vgg/block10_cls_pred/softmax/Reshape_1:0'),
                      graph.get_tensor_by_name('prefix/ssd_300_vgg/block11_cls_pred/softmax/Reshape_1:0')]
        self.localisations= [graph.get_tensor_by_name('prefix/ssd_300_vgg/block4_box/loc_pred:0'),
                        graph.get_tensor_by_name('prefix/ssd_300_vgg/block7_box/loc_pred:0'),
                        graph.get_tensor_by_name('prefix/ssd_300_vgg/block8_box/loc_pred:0'),
                        graph.get_tensor_by_name('prefix/ssd_300_vgg/block9_box/loc_pred:0'),
                        graph.get_tensor_by_name('prefix/ssd_300_vgg/block10_box/loc_pred:0'),
                        graph.get_tensor_by_name('prefix/ssd_300_vgg/block11_box/loc_pred:0')]
        self.bbox_img= graph.get_tensor_by_name('prefix/ssd_preprocessing_train/my_bbox_img/strided_slice:0')


        # SSD default anchor boxes.
        net_shape = (300, 300)
        ssd_net = ssd_vgg_300.SSDNet()
        self.ssd_anchors = ssd_net.anchors(net_shape)

        ########################################
        # ラベル
        ########################################
        self.VOC_LABELS = {
            0: 'none',
            1: 'stop',
            2: 'speed_10',
            3: 'speed_20',
            4: 'speed_30',
        }
        self.colors = [(random.randint(0,255), random.randint(0,255), random.randint(0,255)) for i in range(len(self.VOC_LABELS))]

        self.sess = tf.Session(graph=graph,config=config)


    def __del__(self):
        if self.sess is not None:
            self.sess.close()
        return


    def print_graph_operations(self,graph):
        # print operations
        print("----- operations in graph -----")
        for op in graph.get_operations():
            print("{} {}".format(op.name,op.outputs))
        return


    def print_graph_nodes(self,graph_def):
        # print nodes
        print("----- nodes in graph_def -----")
        for node in graph_def.node:
            print(node)
        return


    def load_graph(self,frozen_graph_filename):
        # We load the protobuf file from the disk and parse it to retrieve the
        # unserialized graph_def
        with tf.gfile.GFile(frozen_graph_filename, "rb") as f:
            graph_def = tf.GraphDef()
            graph_def.ParseFromString(f.read())

        # Then, we can use again a convenient built-in function to import a graph_def into the
        # current default Graph
        with tf.Graph().as_default() as graph:
            tf.import_graph_def(
                graph_def,
                input_map=None,
                return_elements=None,
                name="prefix",
                op_dict=None,
                producer_op_list=None
            )
        return graph

    def write_bboxes(self, classes, scores, bboxes):
        """Visualize bounding boxes. Largely inspired by SSD-MXNET!
        """
        height = self.cv_bgr.shape[0]
        width = self.cv_bgr.shape[1]
        for i in range(classes.shape[0]):
            cls_id = int(classes[i])
            if cls_id >= 0:
                score = scores[i]
                ymin = int(bboxes[i, 0] * height)
                xmin = int(bboxes[i, 1] * width)
                ymax = int(bboxes[i, 2] * height)
                xmax = int(bboxes[i, 3] * width)
                cv2.rectangle(self.cv_bgr, (xmin, ymin), (xmax, ymax),
                              self.colors[cls_id],
                              2)
                class_name = self.VOC_LABELS[cls_id]
                cv2.rectangle(self.cv_bgr, (xmin, ymin-6), (xmin+180, ymin+6),
                              self.colors[cls_id],
                              -1)
                cv2.putText(self.cv_bgr, '{:s} | {:.3f}'.format(class_name, score),
                            (xmin, ymin + 6),
                            cv2.FONT_HERSHEY_PLAIN, 1,
                            (255, 255, 255))
        return


    # Main image processing routine.
    def get_detection(self,select_threshold=0.5, nms_threshold=.45, net_shape=(300, 300)):
        # 予測実行
        # Run SSD network.
        rpredictions, rlocalisations, rbbox_img = self.sess.run([self.predictions, self.localisations, self.bbox_img],
                                                           feed_dict={self.input_x: self.cv_bgr})

        # Get classes and bboxes from the net outputs.
        rclasses, rscores, rbboxes = np_methods.ssd_bboxes_select(
            rpredictions, rlocalisations, self.ssd_anchors,
            select_threshold=select_threshold, img_shape=net_shape, num_classes=5, decode=True)

        rbboxes = np_methods.bboxes_clip(rbbox_img, rbboxes)
        rclasses, rscores, rbboxes = np_methods.bboxes_sort(rclasses, rscores, rbboxes, top_k=400)
        rclasses, rscores, rbboxes = np_methods.bboxes_nms(rclasses, rscores, rbboxes, nms_threshold=nms_threshold)
        # Resize bboxes to original image shape. Note: useless for Resize.WARP!
        rbboxes = np_methods.bboxes_resize(rbbox_img, rbboxes)

        self.write_bboxes(rclasses, rscores, rbboxes)
        return rclasses, rscores, rbboxes



