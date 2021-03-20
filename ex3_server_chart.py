#!/usr/bin/env python3
# coding: utf-8

################################################################################
# BLE Sensor ex3_server_chart.py [棒グラフ機能付き]
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
counter = 0                                         # BLEビーコン発見数

from wsgiref.simple_server import make_server       # WSGIサーバ
from bluepy import btle                             # bluepyからbtleを組み込む
from sys import argv                                # sysから引数取得を組み込む
from getpass import getuser                         # ユーザ取得を組み込む
from time import time                               # 時間取得を組み込む
import threading                                    # スレッド管理を組み込む

def barChartHtml(name, val, max, color='green'):    # 棒グラフHTMLを作成する関数
    html = '<tr><td>' + name + '</td>\n'            # 棒グラフ名を表示
    html += '<td align="right">'+str(val)+'</td>\n' # 変数valの値を表示
    i= round(200 * val / max)                       # 棒グラフの長さを計算
    if val >= max * 0.75:                           # 75％以上のとき
        color = 'red'                               # 棒グラフの色を赤に
        if val > max:                               # 最大値(100％)を超えた時
            i = 200                                 # グラフ長を200ポイントに
    html += '<td><div style="background-color:' + color
    html += '; width:' + str(i) + 'px">&nbsp;</div></td>\n'
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
    html += barChartHtml('Counter', counter, 10)    # カウント値を棒グラフ化
    html += '</tr>\n</table>\n</body>\n</html>\n'   # 作表とhtmlの終了
    start_response('200 OK', [('Content-type', 'text/html; charset=utf-8')])
    return [html.encode('utf-8')]                   # 応答メッセージを返却

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
        counter = len(MAC) * 2                      # 分あたりの発見機器数を保持
        print(counter, 'Counts/minute')             # カウンタ値(分あたり)を表示
        MAC = list()                                # アドレスを廃棄
        time_prev = time()                          # 現在の時間を変数に保持
