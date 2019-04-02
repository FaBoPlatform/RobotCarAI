#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cv2
import threading
import platform

class WebcamVideoStream:
    stream = None
    out = None
    frame = None
    save = False

    def __init__(self):
        return

    def init_webcam(self):
        # initialize the video camera stream and read the first frame
        if platform.machine() == 'aarch64':
            #self.stream = cv2.VideoCapture(1) # WebCam Jetson TX2 /dev/video1
            self.stream = cv2.VideoCapture('udp://192.168.0.77:8090') # UDP Streaming
        elif platform.machine() == 'armv7l': # armv7l
            self.stream = cv2.VideoCapture(0) # WebCam Raspberry Pi3 /dev/video0
        else: # amd64
            #self.stream = cv2.VideoCapture(0) # WebCam
            #self.stream = cv2.VideoCapture('udp://a32158c3da9f:8090') # GPU docker container id
            self.stream = cv2.VideoCapture('udp://2204f9b0e871:8090') # PC docker

        print(self.stream.isOpened())
        if not self.stream.isOpened():
            # カメラオープン失敗は復旧できないので終了にする
            raise IOError(("Couldn't open video file or webcam. If you're "
                           "trying to open a webcam, make sure you video_path is an integer!"))

        fourcc = None
        fps = None
        cv_version = cv2.__version__.split(".")
        if cv_version[0] == '2':
            # OpenCV 2.4
            cols = self.stream.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
            rows = self.stream.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)
            fps = self.stream.get(cv2.cv.CV_CAP_PROP_FPS,fps)
            fourcc = cv2.cv.CV_FOURCC('m', 'p', '4', 'v')
        else:
            # OpenCV 3.2
            cols = self.stream.get(cv2.CAP_PROP_FRAME_WIDTH)
            rows = self.stream.get(cv2.CAP_PROP_FRAME_HEIGHT)
            fps = self.stream.get(cv2.CAP_PROP_FPS)
            fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
        (self.grabbed, self.frame) = self.stream.read()
        # initialize the variable used to indicate if the thread should
        # check camera stream shape
        print("Start video stream with shape: {},{}".format(cols, rows))
        self.running = True
        return cols,rows,fps,fourcc

    def __del__(self):
        if self.stream.isOpened():
            self.stream.release()
        return

    def start(self):
        # start the thread to read frames from the video stream
        t = threading.Thread(target=self.update, args=())
        t.setDaemon(True)
        t.start()
        return self

    def update(self):
        try:
            # keep looping infinitely until the stream is closed
            while self.running:
                # otherwise, read the next frame from the stream
                (self.grabbed, self.frame) = self.stream.read()
        except:
            import traceback
            traceback.print_exc()
            self.running = False
        finally:
            # if the thread indicator variable is set, stop the thread
            self.stream.release()
        return

    def read(self):
        # return the frame most recently read
        return self.frame

    def stop(self):
        self.running = False
