#!/usr/bin/env python3
# coding: utf-8

################################################################################
# BLE Sensor ex1_scan.py
#
#                                          Copyright (c) 2019-2021 Wataru KUNINO
################################################################################

#【インストール方法】
#   bluepy (Bluetooth LE interface for Python)をインストールしてください
#       sudo pip3 install bluepy
#
#   サンプル・プログラム集をダウンロードして下さい。
#       git clone https://bokunimo.net/git/ble_sensor
#
#【実行方法】
#   実行するときは sudoを付与してください
#       sudo ./ex1_scan.py
#
#【参考文献】
#   本プログラムを作成するにあたり下記を参考にしました
#   https://ianharvey.github.io/bluepy-doc/scanner.html

interval = 1.01                                     # 動作間隔(秒)

from bluepy import btle                             # bluepyからbtleを組み込む
from time import sleep                              # timeからsleepを組み込む
from sys import argv                                # sysから引数取得を組み込む
from getpass import getuser                         # ユーザ取得を組み込む

if getuser() != 'root':                             # 実行したユーザがroot以外
    print('使用方法: sudo', argv[0], '[対象MACアドレス(省略可)]...')
    exit()                                          # プログラムの終了

scanner = btle.Scanner()                            # インスタンスscannerを生成
while True:                                         # 永久ループ
    try:
        devices = scanner.scan(interval)            # BLEアドバタイジング取得
    except Exception as e:                          # エラー発生時
        print('ERROR',e)                            # エラー表示
        print('Rebooting HCI, please wait...')      # HCI再起動中表示
        subprocess.call(['hciconfig','hci0','down'])# HCIの切断
        sleep(5)                                    # 5秒間待機
        subprocess.call(['hciconfig','hci0','up'])  # HCIの再接続
        sleep(interval)                             # 1秒間待機
        continue                                    # 永久ループの先頭に戻る
    for dev in devices:                             # 発見した各デバイスについて
        print('\nDevice',dev.addr, end='')          # MACアドレスを表示
        print(' (' + dev.addrType + ')', end='')    # アドレス種別を表示
        print(', RSSI=' + str(dev.rssi), end='')    # 受信強度RSSIを表示
        if dev.connectable:                         # GATT接続が可能なデバイス
            print(', Connectable', end='')          # 接続可能を表示
        print('\n|type|              description | value')
        for d in dev.getScanData():                 # タプル型変数dに代入
            print('|%4d|%25s' %(d[0],d[1]), end='') # アドバタイズTypeとType名
            print('\t|', d[2])                      # データ値を表示

''' 実行結果の一例
pi@raspberrypi:~ $ cd ~/ble_sensor
pi@raspberrypi:~/ble_sensor $ sudo ./ex1_scan.py

Device 72:3b:xx:xx:xx:xx (random), RSSI=-60
|type|              description | value
|   3|    Complete 16b Services | 0000fd6f-0000-1000-8000-00805f9b34fb
|  22|         16b Service Data | xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

Device 53:2c:xx:xx:xx:xx (random), RSSI=-70, Connectable
|type|              description | value
|   1|                    Flags | 1a
|  10|                 Tx Power | 0c
| 255|             Manufacturer | xxxxxxxxxxxxxxxxxxxx

Device f8:80:xx:xx:xx:xx (random), RSSI=-81
|type|              description | value
|   1|                    Flags | 06
| 255|             Manufacturer | 59008c5d0033bd55
|   9|      Complete Local Name | nRF5x

'''
