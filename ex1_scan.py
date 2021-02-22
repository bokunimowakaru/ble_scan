#!/usr/bin/env python3
# coding: utf-8

################################################################################
# BLE Sensor ex1_scan.py
# BLEビーコン(アドバタイジング)の情報を表示します。
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
#       sudo ./ex1_scan.py
#
#【参考文献】
#   本プログラムを作成するにあたり下記を参考にしました
#   https://ianharvey.github.io/bluepy-doc/scanner.html

interval = 1.01                                     # 動作間隔(秒)

from bluepy import btle                             # bluepyからbtleを組み込む
from sys import argv                                # sysから引数取得を組み込む
from getpass import getuser                         # ユーザ取得を組み込む

if getuser() != 'root':                             # 実行したユーザがroot以外
    print('使用方法: sudo', argv[0])                # 使用方法の表示
    exit()                                          # プログラムの終了
scanner = btle.Scanner()                            # インスタンスscannerを生成
while True:                                         # 永久ループ
    devices = scanner.scan(interval)                # BLEアドバタイジング取得
    for dev in devices:                             # 発見した各デバイスについて
        print()                                     # 改行
        print('Address =',dev.addr, end=', ')       # アドレスを表示
        print('AddrType =', dev.addrType, end=', ') # アドレス種別を表示
        print('RSSI =', str(dev.rssi))              # 受信強度RSSIを表示
        for d in dev.getScanData():                 # タプル型変数dに代入
            print('\t', d[0], d[1], '=', d[2])      # アドバタイズType番号,名,値

''' 実行結果の一例
pi@raspberrypi:~ $ cd ~/ble_scan
pi@raspberrypi:~/ble_scan $ sudo ./ex1_scan.py

Address = 72:3b:xx:xx:xx:xx, AddrType = random, RSSI = -60
		3 Complete 16b Services = 0000fd6f-0000-1000-8000-00805f9b34fb
		22 16b Service Data = xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

Address = 53:2c:xx:xx:xx:xx, AddrType = random, RSSI = -70
		1 Flags = 1a
		10 Tx Power = 0c
		255 Manufacturer = xxxxxxxxxxxxxxxxxxxx

Address = f8:80:xx:xx:xx:xx, AddrType = random, RSSI=-81
		1 Flags = 06
		255 Manufacturer = 59008c5d0033bd55
		9 Complete Local Name = nRF5x
'''
