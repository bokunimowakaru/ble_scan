#!/usr/bin/env python3
# coding: utf-8

################################################################################
# BLE Sensor ex5_line.py
# 1分間に発見したBLEビーコン数をLINEアプリに送信します。
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
#       sudo ./ex5_line.py
#
#【参考文献】
#   本プログラムを作成するにあたり下記を参考にしました
#   https://ianharvey.github.io/bluepy-doc/scanner.html

'''
 ※LINE アカウントと LINE Notify 用のトークンが必要です。
    1. https://notify-bot.line.me/ へアクセス
    2. 右上のアカウントメニューから「マイページ」を選択
    3. アクセストークンの発行で「トークンを発行する」を選択
    4. トークン名「raspi」（任意）を入力
    5. 送信先のトークルームを選択する(「1:1でLINE Notifyから通知を受け取る」等)
    6. [発行する]ボタンでトークンが発行される
    7. [コピー]ボタンでクリップボードへコピー
    8. 下記のline_tokenに貼り付け
'''

line_token='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
                                            # ↑ここにLINEで取得したTOKENを入力

interval = 1.01                                     # 動作間隔(秒)
target_rssi = -999                                  # 最低受信強度
counter = None                                      # BLEビーコン発見数
alart_n = 3                                         # LINE送信閾値

from bluepy import btle                             # bluepyからbtleを組み込む
from sys import argv                                # sysから引数取得を組み込む
from getpass import getuser                         # ユーザ取得を組み込む
from time import time                               # 時間取得を組み込む
import urllib.request                               # HTTP通信を組み込む
import json                                         # JSON変換を組み込む

url_s = 'https://notify-api.line.me/api/notify'     # アクセス先
head = {'Authorization':'Bearer ' + line_token,
             'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8'};

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
        print(counter, 'Counts/minute')             # カウンタ値を表示
        MAC = list()                                # アドレスを廃棄
        time_prev = time()                          # 現在の時間を変数に保持
        if counter >= alart_n:                      # カウンタ値が5以上のとき
            body = 'message=密集度は ' + str(counter) + ' です。'
            print(body)                             # メッセージを表示
            post = urllib.request.Request(url_s, body.encode(), head)
            try:                                    # 例外処理の監視を開始
                urllib.request.urlopen(post)        # HTTPアクセスを実行
            except Exception as e:                  # 例外処理発生時
                print(e,url_s)                      # エラー内容と変数url_s表示

''' 実行結果の一例
pi@raspberrypi:~ $ cd ~/ble_scan
pi@raspberrypi:~/ble_scan $ sudo ./ex5_line.py
1 Devices found
2 Devices found
3 Devices found
3 Counts/minute
message=密集度は 3 です。
1 Devices found
2 Devices found
2 Counts/minute
1 Devices found
2 Devices found
3 Devices found
4 Devices found
4 Counts/minute
message=密集度は 4 です。
'''
