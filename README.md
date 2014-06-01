PC Counter for Pachinko
=======================

Pachinko Counter は、パチンコ台の外部情報出力端子から出力される信号を、USB-IO経由で受け取り、現在の回転数や確率などを出力するいわゆるカウンターです。

必要なハードウエア
-----------------
- USB-IO 2.0
  - http://km2net.com/usb-io2.0/index.shtml
  - http://akizukidenshi.com/catalog/g/gM-05131/


必要なソフトウエア
-----------------
- Python >=2.7 or >=3.3
- PyGObject
- PyUSB and libusb-1.0
- SimpleJSON
- PyUSBIO
  - https://github.com/yukkeorg/pyusbio


クイックスタート
----------------
    $ git clone https://github.com/yukkeorg/PachiCounter.git
    $ cd PachiCounter
    $ python pcounter/app.py [option] [machine_name]


オプション
----------
-r
: カウンタをリセットした状態で起動します。


制限
----
- イベントループにてGLibを利用しているため、GLibがインストールされている環境でのみ動作します。(これは近く改善する予定)


ライセンス
----------
MIT License
