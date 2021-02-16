#!/usr/bin/env python3
# coding: utf-8

################################################################################
# BLE Sensor ex2_counter.py
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
#       sudo ./ex2_counter.py
#
#【参考文献】
#   本プログラムを作成するにあたり下記を参考にしました
#   https://ianharvey.github.io/bluepy-doc/scanner.html

interval = 1.01                                     # 動作間隔(秒)
target_rssi = -80                                   # 最低受信強度

from bluepy import btle                             # bluepyからbtleを組み込む
from time import sleep                              # timeからsleepを組み込む
from sys import argv                                # sysから引数取得を組み込む
from getpass import getuser                         # ユーザ取得を組み込む

if getuser() != 'root':                             # 実行したユーザがroot以外
    print('使用方法: sudo', argv[0], '[対象MACアドレス(省略可)]...')
    exit()                                          # プログラムの終了

MAC = list()                                        # アドレス保存用の配列変数
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
        if dev.rssi < target_rssi:                  # 受信強度が-80より小さい時
            continue                                # forループの先頭に戻る
        if dev.addr not in MAC:                     # アドレスが配列内に無い時
            MAC.append(dev.addr)                    # 配列変数にアドレスを追加
        print(len(MAC), 'Devices found,', end=' ')  # 発見済みデバイス数を表示
        print(dev.addr, end=' ')                    # MACアドレスを表示
        print('RSSI=' + str(dev.rssi))              # 受信強度RSSIを表示

''' 実行結果の一例
pi@raspberrypi:~ $ cd ~/ble_sensor
pi@raspberrypi:~/ble_sensor $ sudo ./ex2_counter.py
1 Devices found, 6a:f9:xx:xx:xx:xx RSSI=-62
2 Devices found, 5e:27:xx:xx:xx:xx RSSI=-56
2 Devices found, 5e:27:xx:xx:xx:xx RSSI=-57
3 Devices found, f8:80:xx:xx:xx:xx RSSI=-80
