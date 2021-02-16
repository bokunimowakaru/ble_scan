#!/usr/bin/env python3
# coding: utf-8

################################################################################
# BLE Logger
#
#                                          Copyright (c) 2019-2021 Wataru KUNINO
################################################################################

#【インストール方法】
#   bluepy (Bluetooth LE interface for Python)をインストールしてください
#       sudo pip3 install bluepy
#
#【実行方法】
#   実行するときは sudoを付与してください
#       sudo ./ble_logger_basic.py &
#
#【参考文献】
#   本プログラムを作成するにあたり下記を参考にしました
#   https://ianharvey.github.io/bluepy-doc/scanner.html

interval = 1.01                                 # 動作間隔(秒)

from bluepy import btle                         # bluepyからbtleを組み込む
from time import sleep                          # timeからsleepを組み込む

def payval(num, bytes=1, sign=False):           # 受信データから値を抽出する
    global val                                  # 受信データ用変数valを読み込む
    a = 0                                       # 戻り値用変数aを定義する
    if num < 2 or len(val) < (num - 2 + bytes) * 2:
        print('ERROR: data length',len(val))
        return 0
    for i in range(0, bytes):                   # バイト数分の値を変数aに代入
        a += (256 ** i) * int(val[(num - 2 + i) * 2 : (num - 1 + i) * 2],16)
    if sign:                                    # 符号つきの場合
        if a >= 2 ** (bytes * 8 - 1):           # マイナス値のとき
            a -= 2 ** (bytes * 8)               # マイナス値へ変換
    return a                                    # 得られた値aを応答する

def printval(dict, name, n, unit):              # 受信値を表示する関数
    value = dict.get(name)                      # 変数dict内の項目nameの値を取得
    if value == None:                           # 項目が無かったとき
        return                                  # 戻る
    if type(value) is not str:                  # 値が文字列で無かったとき
        value = round(value,n)                  # 小数点以下第n位で丸める
    print('    ' + name + ' ' * (14 - len(name)) + '=', value, unit)    # 表示

scanner = btle.Scanner()                        # インスタンスscannerを生成
while True:                                     # 永久ループ
    # BLEスキャン
    try:
        devices = scanner.scan(interval)
    except Exception as e:
        print('ERROR',e)
        print('Rebooting HCI, please wait...')
        subprocess.call(['hciconfig', 'hci0', 'down'])
        sleep(5)
        subprocess.call(['hciconfig', 'hci0', 'up'])
        sleep(interval)
        continue
    for dev in devices:                         # 見つかった各デバイスについて
        print("\nDevice %s (%s), RSSI=%d dB, Connectable=%s" % (dev.addr, dev.addrType, dev.rssi, dev.connectable))
        for (adtype, desc, value) in dev.getScanData():
            print("  %3d %s = %s" % (adtype, desc, value))

''' 実行結果の一例
pi@raspberrypi:~ $ cd
pi@raspberrypi:~ $ git clone https://bokunimo.net/git/ble_sensor
pi@raspberrypi:~ $ cd ~/ble_sensor
pi@raspberrypi:~/ble_sensor $ sudo ./ble_logger.py

'''
