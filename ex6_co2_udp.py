#!/usr/bin/env python3
# coding: utf-8

################################################################################
# BLE Sensor ex6_co2_udp.py [棒グラフ機能付き][UDP送信機能付き]
# ex3_server.py に CO2センサ(SENSIRION SGP30)を追加します。
#
#                                               Copyright (c) 2021 Wataru KUNINO
################################################################################

#【ハードウェア】
# CO2センサ SENSIRION SGP30 のI2Cインタフェースを Raspberry Piに接続します。
#   Raspberry Piの3番ピンにSDAを、5番ピンにSCLを接続してください。
#   注意：SGP30の電源VDD,VDDH、信号電圧は1.8Vです。
#       　1.8Vの電源を供給し、Raspberry PiのI2C信号を3.3V→1.8に変換する
#       　必要があります。

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
sgp30 = 0x58                                        # センサSGP30のI2Cアドレス
counter = 0                                         # BLEビーコン発見数
temp_offset = 0                                     # 温度補正値
temp = 0                                            # 温度値
co2 = 0                                             # 推定CO2濃度
tvoc = 0                                            # TVOC濃度
udp_to = '255.255.255.255'                          # UDPブロードキャスト
udp_port = 1024                                     # UDP送信ポート番号を1024に
device_s = 'e_co2_3'                                # デバイス識別名

from wsgiref.simple_server import make_server       # WSGIサーバ
from bluepy import btle                             # bluepyからbtleを組み込む
from sys import argv                                # sysから引数取得を組み込む
from getpass import getuser                         # ユーザ取得を組み込む
from time import time                               # 時間取得を組み込む
from time import sleep                              # スリープ機能を組み込む
import threading                                    # スレッド管理を組み込む
import smbus                                        # SMBus(I2C)管理を組み込む
import sys
import socket

class TempSensor:                                       # クラスTempSensorの定義
    _filename = '/sys/class/thermal/thermal_zone0/temp' # デバイスのファイル名
    try:                                                # 例外処理の監視を開始
        fp = open(_filename)                            # ファイルを開く
    except Exception as e:                              # 例外処理発生時
        raise Exception('SensorDeviceNotFound')         # 例外を応答
    def __init__(self):                                 # コンストラクタ作成
        self.offset = float(30.0)                       # 温度センサ補正用
        self.value = float()                            # 測定結果の保持用
    def get(self):                                      # 温度値取得用メソッド
        self.fp.seek(0)                                 # 温度ファイルの先頭へ
        val = float(self.fp.read()) / 1000              # 温度センサから取得
        val -= self.offset                              # 温度を補正
        val = round(val,1)                              # 丸め演算
        self.value = val                                # 測定結果を保持
        return val                                      # 測定結果を応答
    def __del__(self):                                  # インスタンスの削除
        self.fp.close()                                 # ファイルを閉じる

def barChartHtml(name, val, max, color='green'):    # 棒グラフHTMLを作成する関数
    html = '<tr><td>' + name + '</td>\n'            # 棒グラフ名を表示
    html += '<td align="right">'+str(val)+'</td>\n' # 変数valの値を表示
    i= round(200 * val / max)                       # 棒グラフの長さを計算
    if val >= max * 0.75:                           # 75％以上のとき
        color = 'red'                               # 棒グラフの色を赤に
        if val > max:                               # 最大値(100％)を超えた時
            i = 200                                 # グラフ長を200ポイントに
    html += '<td><div style="background-color: ' + color
    html += '; width: ' + str(i) + 'px">&nbsp;</div></td>\n'
    return html                                     # HTMLデータを返却

def wsgi_app(environ, start_response):              # HTTPアクセス受信時の処理
    path  = environ.get('PATH_INFO')                # リクエスト先のパスを代入
    if path != '/':                                 # パスがルート以外のとき
        start_response('404 Not Found',[])          # 404エラー設定
        return ['404 Not Found'.encode()]           # 応答メッセージ(404)を返却
    html = '<html>\n<head>\n'                       # HTMLコンテンツを作成
    html += '<meta http-equiv="refresh" content="10;">\n'   # 自動再読み込み
    html += '</head>\n<body>\n'                     # 以下は本文
    html += '<table border=1>\n'                    # 作表を開始
    html += '<tr><th>項目</th><th width=50>値</th>' # 「項目」「値」を表示
    html += '<th width=200>グラフ</th>\n'           # 「グラフ」を表示
    html += barChartHtml('Temperature', temp, 40)   # カウント値を棒グラフ化
    html += barChartHtml('Counter', counter, 10)    # カウント値を棒グラフ化
    html += barChartHtml('CO2', co2, 1000)          # 推定CO2濃度を棒グラフ化
    html += barChartHtml('TVOC', tvoc, 100)         # TVOC濃度を棒グラフ化
    html += '</tr>\n</table>\n</body>\n</html>\n'   # 作表とhtmlの終了
    start_response('200 OK', [('Content-type', 'text/html; charset=utf-8')])
    return [html.encode('utf-8')]                   # 応答メッセージを返却

def httpd(port = 80):
    htserv = make_server('', port, wsgi_app)        # HTTPサーバ実体化
    print('HTTP port', port)                        # ポート番号を表示
    htserv.serve_forever()                          # HTTPサーバを起動

def word2uint(d1,d2):                               # 2バイトデータを結合します
    i = d1                                          # 1バイト目を変数iに代入
    i <<= 8                                         # 8ビット左シフト(上位)
    i += d2                                         # 2バイト目を変数iに加算
    return i                                        # 変数iの値を返却

def getCo2():                                       # SGP30からCO2とTVOCを取得
    i2c.write_byte_data(sgp30, 0x20, 0x08)          # I2C通信で取得コマンド送信
    sleep(0.014)                                    # 14msの待ち時間処理
    data=i2c.read_i2c_block_data(sgp30,0x00,6)      # I2C通信で受信
    if len(data) >= 5:                              # 5バイト以上を受信した時
        co2 = word2uint(data[0],data[1])            # 推定CO2を変数co2に代入
        tvoc= word2uint(data[3],data[4])            # TVOC濃度を変数tvocに代入
    return (co2,tvoc)                               # それぞれを戻り値として返却

if getuser() != 'root':                             # 実行したユーザがroot以外
    print('使用方法: sudo', argv[0])                # 使用方法の表示
    exit()                                          # プログラムの終了
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # ソケットを作成
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,1)
except Exception as e:                              # 例外処理発生時
    print(e)                                        # エラー内容を表示
    exit()                                          # プログラムの終了
try:                                                # 例外処理の監視を開始
    tempSensor = TempSensor()                       # 温度センサの実体化
except Exception as e:                              # 例外処理発生時
    print(e)                                        # エラー内容の表示
    exit()                                          # プログラムの終了
tempSensor.offset += temp_offset                    # 温度補正値を加算する

i2c = smbus.SMBus(1)                                # I2Cバス1を実体化
i2c.write_byte_data(sgp30, 0x20, 0x03)              # SGP30の初期設定を実行
sleep(1.012)                                        # 1.012秒間の待ち時間処理

time_prev = time()                                  # 現在の時間を変数に保持
MAC = list()                                        # アドレス保存用の配列変数
scanner = btle.Scanner()                            # インスタンスscannerを生成
thread = threading.Thread(target=httpd, daemon=True)# スレッドhttpdの実体化
thread.start()                                      # スレッドhttpdの起動

while thread.is_alive:                              # 永久ループ(httpd動作中)
    devices = scanner.scan(interval)                # BLEアドバタイジング取得
    (co2, tvoc) = getCo2()                          # SGP30からCO2とTVOCを取得
    temp = round(tempSensor.get())                  # Raspberry Piの温度値を取得
    for dev in devices:                             # 発見した各デバイスについて
        if dev.rssi < target_rssi:                  # 受信強度が-80より小さい時
            continue                                # forループの先頭に戻る
        if dev.addr not in MAC:                     # アドレスが配列内に無い時
            MAC.append(dev.addr)                    # 配列変数にアドレスを追加
            print(len(MAC), 'Devices found')        # 発見済みデバイス数を表示
    if time_prev + 30 < time():                     # 30秒以上経過した時
        counter = len(MAC)                          # 発見済みデバイス数を保持
        print(counter, 'Counts/minute', end = ', ') # カウンタ値を表示
        print('Temp = %d ℃' % temp, end = ', ')    # tempを表示
        print('CO2 = %d ppm' % co2, end = ', ')     # co2を表示
        print("TVOC= %d ppb" % tvoc)                # tvodを表示
        MAC = list()                                # アドレスを廃棄
        time_prev = time()                          # 現在の時間を変数に保持
        udp_s = device_s + ', ' + str(temp) + ', 0, 0, '
        udp_s += str(co2) + ', ' + str(tvoc) + ', ' + str(counter)
        print('send :', udp_s)                      # 受信データを出力
        udp_bytes = (udp_s + '\n').encode()         # バイト列に変換
        try:                                        # 作成部
            sock.sendto(udp_bytes,(udp_to,udp_port)) # UDPブロードキャスト送信
        except Exception as e:                      # 例外処理発生時
            print(e)                                # エラー内容を表示
sock.close()                                        # ソケットの切断
