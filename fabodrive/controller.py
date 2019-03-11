# coding: utf-8
# python controller.py (with Picamera)
# python controller.py --use-usb (with USB Webcam)
import argparse
import base64
#import cStringIO as io
import io
import os
import tornado
import tornado.httpserver
import tornado.web
import tornado.websocket
import tornado.ioloop
import webbrowser
from fabolib.motor import Motor
from fabolib.servo import Servo
from fabolib.config import CarConfig
import socket

parser = argparse.ArgumentParser(description="Starts a webserver that "
                                 "connects to a webcam.")
parser.add_argument("--port", type=int, default=8080, help="The "
                    "port on which to serve the website.")
parser.add_argument("--resolution", type=str, default="low", help="The "
                    "video resolution. Can be high, medium, or low.")
parser.add_argument("--use-usb", action="store_true", help="Use a USB "
                    "webcam instead of the standard Pi camera.")
parser.add_argument("--usb-id", type=int, default=0, help="The "
                    "usb camera number to display")
parser.add_argument("--type", type=str, default="fabo", help="Robot type")
args = parser.parse_args()

HANDLE_NEUTRAL = CarConfig.HANDLE_NEUTRAL
HANDLE_ANGLE = CarConfig.HANDLE_ANGLE
BUSNUM = 1

if args.type == "fabo":
    motor = Motor(busnum=BUSNUM)
    servo = Servo(busnum=BUSNUM)
    motor.stop()
    servo.set_angle(HANDLE_NEUTRAL)
elif args.type == "1/6":
    print("1/6")

if args.use_usb:
    import cv2
    from PIL import Image
    camera = cv2.VideoCapture(args.usb_id)
else:
    import picamera
    camera = picamera.PiCamera()
    camera.start_preview()
    print("picamera enable", camera)

resolutions = {"high": (1280, 720), "medium": (640, 480), "low": (320, 240)}
if args.resolution in resolutions:
    if args.use_usb:
        w, h = resolutions[args.resolution]
        camera.set(3, w)
        camera.set(4, h)
    else:
        camera.resolution = resolutions[args.resolution]
        print("picamera resolution", camera.resolution)
else:
    raise Exception("%s not in resolution options." % args.resolution)

class IndexHandler(tornado.web.RequestHandler):

    def get(self):
        # GETメソッドで最初のHTTPアクセスを受け付け、WebSocket接続を行うスクリプトが入ったindex.htmlを返す。
        # index.html内にある変数名PORT,ANGLE_NEUTRALに値を入れて返す。
        self.render("index.html",
                    PORT = args.port)

class DriveHandler(tornado.web.RequestHandler):

    def get(self):
        # GETメソッドで車両制御アクセスを受付、処理を行う。何も返さない。
        self.drive()
        return

    def post(self):
        # POSTメソッドで車両制御アクセスを受付、処理を行う。何も返さない。
        self.drive()
        return

    def drive(self):
        # 車両制御処理を行う。何も返さない。
        angle = int(float(self.get_argument('angle')))
        speed = int(float(self.get_argument('speed')))
        if args.type == "fabo":
            """
            ステアリング角を制限する
            servo.pyのサーボ制御は0-180度まで動作する。
            しかし、ラジコンのステアリングは90度を基準に45度程度にしか曲げることが出来ないため、
            サーボを壊さないようにここで制限する必要がある。
            """
            if angle < -45:
                angle = 45
            elif angle > 45:
                angle = 45
            servo.set_angle(HANDLE_NEUTRAL - angle)

            """
            速度を制限する
            motor.pyで100を超える場合は無視するようにしているので、制限は必要ないけれども、
            ステアリング処理に合わせて制限を入れておく。
            """
            if speed == 0:
                motor.stop()
            elif speed > 0:
                if speed > 100:
                    speed = 100
                motor.forward(speed)
            elif speed < 0:
                if speed < -100:
                    speed = -100
                speed = -1 * speed
                motor.back(speed)
            return
        elif args.type == "1/6":
            return

class WSHandler(tornado.websocket.WebSocketHandler):
    def initialize(self):
        # サブクラスを初期化をフックします。リクエスト毎に呼び出されます。
        return

    def on_message(self, message):
        # Start loop when this called
        if message == "read_camera":
            self.camera_loop = tornado.ioloop.PeriodicCallback(self.loop, 10)
            self.camera_loop.start()
        else:
            print("Unsupported function: {}".format(message))

    def loop(self):
        """
        Sends camera images in an infinite loop.
        """
        #sio = io.StringIO()
        sio = io.BytesIO()
        if args.use_usb:
            _, frame = camera.read()
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            img.save(sio, "JPEG")
        else:
            camera.capture(sio, "jpeg", use_video_port=True)
        try:
            self.write_message(base64.b64encode(sio.getvalue()))
        except tornado.websocket.WebSocketClosedError:
            self.camera_loop.stop()

def main():
    print("complete initialization")
    import ipget
    a = ipget.ipget()
    print(a.ipaddr("wlan0")) # 172.xx.xx.xx/24 など

    handlers = [(r"/", IndexHandler), # GETメソッドで最初のアクセスを受ける
            (r"/control", WSHandler), # WebSocket接続を待ち受けるハンドラ
            (r"/drive", DriveHandler), # POSTメソッドで車両制御アクセスを受ける
    ]
    app = tornado.web.Application(handlers,
                                  template_path  = os.path.join(os.getcwd(),  "templates"),
                                  static_path    = os.path.join(os.getcwd(),  "static") # JavaScriptファイルへのアクセス
    )
    app.listen(args.port)
    webbrowser.open("http://localhost:%d/" % args.port, new=2)
    ip_address = socket.gethostbyname(socket.gethostname())
    print(ip_address)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
