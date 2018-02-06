#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ClientからOpenCV画像データを受け取り、ライン検出して制御命令を送る
# Server: Jetson TX2
# Client: Jetson TX2/Raspberry Pi3 Docker
# 先にServerを起動する

'''
Python 3.6
    送信するmessageは.encode('ascii')や.encode('utf-8')等でエンコードする必要がる
    ここではClientから送られてくるOpenCV BGR画像データが'ascii'に変換されているので'ascii'で統一している
'''
print("wait. launching...")
import socket, select
import time
import cv2
import numpy as np
import time
import os
import sys
import logging
import threading
import numpy as np
#from lib import *

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3
if PY2:
    import Queue
elif PY3:
    import queue as Queue
# ログ設定
logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] time:%(created).8f pid:%(process)d pn:%(processName)-10s tid:%(thread)d tn:%(threadName)-10s fn:%(funcName)-10s %(message)s',
)

# 解析、送信スレッド動作フラグ
is_analyze_running = False

sock = None
out = None

def do_analyze():
    global is_analyze_running
    global sock

    while is_analyze_running:
        # 車両制御送信
        sock.sendall(("CONTROL,0,0,").encode('ascii'))
        time.sleep(0.1)


def main():
    global is_analyze_running
    global sock
    global out

    # 通信設定
    HOST = '192.168.0.77' # Server IP Address
    PORT = 6666 # Server TCP Port
    #HOST = 'a32158c3da9f' # AWS
    #PORT = 8091 # AWS
    HOST = '2204f9b0e871' # PC
    PORT = 8091 # PC TCP Port

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
                    print(type(packet))
                    # 1Frameずつデータサイズが異なるので、毎回sizeを送ること
                    if is_need_header_receive:
                        print('header')
                        packet = packet.decode('ascii')
                        txt = str(packet)
                        if packet:
                            print('packet True')
                            if packet == 'START':
                                is_analyze_running = True
                                t = threading.Thread(target=do_analyze)
                                t.start()
                            elif packet.startswith('BYE'):
                                print('got BYE')
                                is_need_header_receive = True
                                is_analyze_running = False
                                sock.shutdown(socket.SHUT_RDWR)
                                sock.close()
                                connected_clients_sockets.remove(sock)
                                if out is not None:
                                    out.release()
                        else:
                            print('client disconnect')
                            is_need_header_receive = True
                            is_analyze_running = False
                            sock.shutdown(socket.SHUT_RDWR)
                            sock.close()
                            connected_clients_sockets.remove(sock)
                            if out is not None:
                                out.release()
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
                            if out is not None:
                                out.release()

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
        if out is not None:
            out.release()

if __name__ == '__main__':
    main()
    print("end server")
