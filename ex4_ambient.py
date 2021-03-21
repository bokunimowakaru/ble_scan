#!/usr/bin/env python3
# coding: utf-8

################################################################################
# BLE Sensor ex4_ambient.py
# 1分間に発見したBLEビーコン数をクラウドサービスAmbientに送信します。
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
#       sudo ./ex4_ambient.py
#
#【参考文献】
#   本プログラムを作成するにあたり下記を参考にしました
#   https://ianharvey.github.io/bluepy-doc/scanner.html

ambient_chid='0000'                 # ここにAmbientで取得したチャネルIDを入力
ambient_wkey='0123456789abcdef'     # ここにはライトキーを入力
amdient_tag='d1'                    # データ番号d1～d8のいずれかを入力

interval = 1.01                                     # 動作間隔(秒)
target_rssi = -999                                  # 最低受信強度
counter = None                                      # BLEビーコン発見数

from bluepy import btle                             # bluepyからbtleを組み込む
from sys import argv                                # sysから引数取得を組み込む
from getpass import getuser                         # ユーザ取得を組み込む
from time import time                               # 時間取得を組み込む
import urllib.request                               # HTTP通信を組み込む
import json                                         # JSON変換を組み込む

url_s = 'https://ambidata.io/api/v2/channels/'+ambient_chid+'/data' # アクセス先
head = {'Content-Type':'application/json'}          # ヘッダを辞書型変数headへ
body = {'writeKey':ambient_wkey, amdient_tag:0.0}   # 内容を辞書型変数bodyへ

if getuser() != 'root':                             # 実行したユーザがroot以外
    print('使用方法: sudo', argv[0])                # 使用方法の表示
    exit()                                          # プログラムの終了

time_prev = time()                                  # 現在の時間を変数に保持
MAC = list()                                        # アドレス保存用の配列変数
scanner = btle.Scanner()                            # インスタンスscannerを生成
while True:                                         # 永久ループ
    devices = scanner.scan(interval)                # BLEアドバタイジング取得
    for dev in devices:                             # 発見した各デバイスについて
        if dev.rssi < target_rssi:                  # 受信強度が-80より小さい時
            continue                                # forループの先頭に戻る
        if dev.addr not in MAC:                     # アドレスが配列内に無い時
            MAC.append(dev.addr)                    # 配列変数にアドレスを追加
            print(len(MAC), 'Devices found')        # 発見済みデバイス数を表示
    if time_prev + 30 < time():                     # 30秒以上経過した時
        counter = len(MAC)                          # 発見済みデバイス数を保持
        print(counter, 'Counts/30seconds')          # カウンタ値(30秒あたり)表示
        body[amdient_tag] = counter                 # カウンタ値をbodyへ代入
        print(body)                                 # メッセージを表示
        post = urllib.request.Request(url_s, json.dumps(body).encode(), head)
        try:                                        # 例外処理の監視を開始
            urllib.request.urlopen(post)            # HTTPアクセスを実行
        except Exception as e:                      # 例外処理発生時
            print(e,url_s)                          # エラー内容と変数url_s表示
        MAC = list()                                # アドレスを廃棄
        time_prev = time()                          # 現在の時間を変数に保持

''' 実行結果の一例
pi@raspberrypi:~ $ cd ~/ble_scan
pi@raspberrypi:~/ble_scan $ sudo ./ex4_ambient.py
1 Devices found
2 Devices found
3 Devices found
3 Counts/30seconds
{'writeKey': '0123456789abcdef', 'd1': 3}
1 Devices found
2 Devices found
2 Counts/30seconds
{'writeKey': '0123456789abcdef', 'd1': 2}
'''
