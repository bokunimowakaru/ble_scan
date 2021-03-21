#!/usr/bin/env python3
# coding: utf-8

################################################################################
# BLE Sensor ex3_server.py
# 1分間に発見したBLEビーコン数をHTTPサーバでLAN内に配信します。
#
#                                               Copyright (c) 2021 Wataru KUNINO
################################################################################

#【インストール方法】
#   bluepy (Bluetooth LE interface for Python)をインストールしてください
#       sudo pip3 install bluepy
#
#   サンプル・プログラム集をダウンロードして下さい。
#       git clone https://bokunimo.net/git/ble_scan
#
#【実行方法】
#   実行するときは sudoを付与してください
#       sudo ./ex3_server.py
#
#【参考文献】
#   本プログラムを作成するにあたり下記を参考にしました
#   https://ianharvey.github.io/bluepy-doc/scanner.html

interval = 1.01                                     # 動作間隔(秒)
target_rssi = -80                                   # 最低受信強度
counter = None                                      # BLEビーコン発見数

from wsgiref.simple_server import make_server       # WSGIサーバ
from bluepy import btle                             # bluepyからbtleを組み込む
from sys import argv                                # sysから引数取得を組み込む
from getpass import getuser                         # ユーザ取得を組み込む
from time import time                               # 時間取得を組み込む
import threading                                    # スレッド管理を組み込む

def wsgi_app(environ, start_response):              # HTTPアクセス受信時の処理
    res = 'counter = ' + str(counter) + '\r\n'      # 応答文を作成
    print(res, end='')                              # 応答文を表示
    res = res.encode('utf-8')                       # バイト列へ変換
    start_response('200 OK', [('Content-type', 'text/plain; charset=utf-8')])
    return [res]                                    # 応答メッセージを返却

def httpd(port = 80):
    htserv = make_server('', port, wsgi_app)        # HTTPサーバ実体化
    print('HTTP port', port)                        # ポート番号を表示
    htserv.serve_forever()                          # HTTPサーバを起動

if getuser() != 'root':                             # 実行したユーザがroot以外
    print('使用方法: sudo', argv[0])                # 使用方法の表示
    exit()                                          # プログラムの終了

time_prev = time()                                  # 現在の時間を変数に保持
MAC = list()                                        # アドレス保存用の配列変数
scanner = btle.Scanner()                            # インスタンスscannerを生成
thread = threading.Thread(target=httpd, daemon=True)# スレッドhttpdの実体化
thread.start()                                      # スレッドhttpdの起動
while thread.is_alive:                              # 永久ループ(httpd動作中)
    devices = scanner.scan(interval)                # BLEアドバタイジング取得
    for dev in devices:                             # 発見した各デバイスについて
        if dev.rssi < target_rssi:                  # 受信強度が-80より小さい時
            continue                                # forループの先頭に戻る
        if dev.addr not in MAC:                     # アドレスが配列内に無い時
            MAC.append(dev.addr)                    # 配列変数にアドレスを追加
            print(len(MAC), 'Devices found')        # 発見済みデバイス数を表示
    if time_prev + 30 < time():                     # 30秒以上経過した時
        counter = len(MAC)                          # 発見機器数を保持
        print(counter, 'Counts/30seconds')          # カウンタ値(30秒あたり)表示
        MAC = list()                                # アドレスを廃棄
        time_prev = time()                          # 現在の時間を変数に保持

''' 実行結果の一例
pi@raspberrypi:~ $ cd ~/ble_scan
pi@raspberrypi:~/ble_scan $ sudo ./ex3_server.py
HTTP port 80
1 Devices found
2 Devices found
3 Devices found
3 Counts/30seconds
1 Devices found
192.168.1.5 - - [17/Feb/2021 22:26:12] "GET / HTTP/1.1" 200 14
counter = 3
2 Devices found
--------------------------------------------------------------------------------
pi@raspberrypi:~ $ hostname -I
192.168.1.5 XXXX:XXXX:XXXX:XXXX:XXXX:XXXX:XXXX:XXXX
pi@raspberrypi:~ $ curl 192.168.1.5
counter = 3
pi@raspberrypi:~ $
'''
