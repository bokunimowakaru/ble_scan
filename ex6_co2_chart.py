#!/usr/bin/env python3
# coding: utf-8

################################################################################
# BLE Sensor ex6_co2_chart.py [棒グラフ機能付き]
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
counter = None                                      # BLEビーコン発見数
co2 = 0                                             # 推定CO2濃度
tvoc = 0                                            # TVOC濃度
Res_Html = [('Content-type', 'text/html; charset=utf-8')]
Res_Text = [('Content-type', 'text/plain; charset=utf-8')]
Res_200 = '200 OK'
Res_404 = '404 Not Found'

from wsgiref.simple_server import make_server       # WSGIサーバ
from bluepy import btle                             # bluepyからbtleを組み込む
from sys import argv                                # sysから引数取得を組み込む
from getpass import getuser                         # ユーザ取得を組み込む
from time import time                               # 時間取得を組み込む
from time import sleep                              # スリープ機能を組み込む
import threading                                    # スレッド管理を組み込む
import smbus                                        # SMBus(I2C)管理を組み込む

def barChartHtml(name, val, max, color='green'):    # 棒グラフHTMLを作成する関数
    html = '<tr><td>' + name + '</td>\n'            # 棒グラフ名を表示
    html += '<td align="right">'+str(val)+'</td>\n' # 変数valの値を表示
    if val is None:                                 # 数値が代入されていないとき
        html += '<td>no data</td>\n'                # no data を追加
        return html                                 # HTMLデータを返却
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
        start_response(Res_404, Res_Text)           # 404エラー設定
        return [Res_404.encode()]                   # 応答メッセージ(404)を返却
    html = '<html>\n<head>\n'                       # HTMLコンテンツを作成
    html += '<meta http-equiv="refresh" content="10;">\n'   # 自動再読み込み
    html += '</head>\n<body>\n'                     # 以下は本文
    html += '<table border=1>\n'                    # 作表を開始
    html += '<tr><th>項目</th><th width=50>値</th>' # 「項目」「値」を表示
    html += '<th width=200>グラフ</th>\n'           # 「グラフ」を表示
    html += barChartHtml('Counter', counter, 10)    # カウント値を棒グラフ化
    html += barChartHtml('CO2',co2, 1000)
    html += barChartHtml('TVOD',tvod, 1000)
    html += '</tr>\n</table>\n</body>\n</html>\n'   # 作表とhtmlの終了
    start_response(Res_200, Res_Html)
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
    for dev in devices:                             # 発見した各デバイスについて
        if dev.rssi < target_rssi:                  # 受信強度が-80より小さい時
            continue                                # forループの先頭に戻る
        if dev.addr not in MAC:                     # アドレスが配列内に無い時
            MAC.append(dev.addr)                    # 配列変数にアドレスを追加
            print(len(MAC), 'Devices found')        # 発見済みデバイス数を表示
    if time_prev + 30 < time():                     # 30秒以上経過した時
        counter = len(MAC)                          # 発見済みデバイス数を保持
        print(counter, 'Counts/minute', end = ', ') # カウンタ値を表示
        print('CO2 = %d ppm' % co2, end = ', ')     # co2を表示
        print("TVOC= %d ppb" % tvoc)                # tvodを表示
        MAC = list()                                # アドレスを廃棄
        time_prev = time()                          # 現在の時間を変数に保持

''' 実行結果の一例
pi@raspberrypi:~ $ cd ~/ble_scan
pi@raspberrypi:~/ble_scan $ sudo ./ex6_co2.py
HTTP port 80
1 Devices found
2 Devices found
3 Devices found
4 Devices found
5 Devices found
5 Counts/minute, CO2 = 402 ppm, TVOC= 1 ppb
1 Devices found
192.168.1.5 - - [07/Mar/2021 18:58:20] "GET / HTTP/1.1" 200 36
counter = 5
co2 = 402
tvoc = 1
2 Devices found
3 Devices found
192.168.1.5 - - [07/Mar/2021 18:58:30] "GET / HTTP/1.1" 200 36
counter = 5
co2 = 464
tvoc = 219

--------------------------------------------------------------------------------
pi@raspberrypi:~ $ hostname -I
192.168.1.5 XXXX:XXXX:XXXX:XXXX:XXXX:XXXX:XXXX:XXXX
pi@raspberrypi:~ $ curl 192.168.1.5
counter = 5
co2 = 402
tvoc = 1
pi@raspberrypi:~ $ curl 192.168.1.5
counter = 5
co2 = 464
tvoc = 219
pi@raspberrypi:~ $
'''
