Pachinko Counter
================

Pachinko Counter は、パチンコ台の外部情報出力端子から出力される信号を、USB-IO経由で受け取り、現在の回転数や確率などを出力するいわゆるカウンターです。

注意事項:**このソフトウエアは私が作成した webcamstudio ( https://github.com/yukkeorg/simplebroadcast4linux/blob/master/tool/webcamcomposer )内の子プロセスとして動作することを前提として作成されているため、見やすいGUIが表示されたりしませんので、ご注意下さい。**

必要なハードウエア
-----------------
- USB-IO 2.0
  - http://km2net.com/usb-io2.0/index.shtml
  - http://akizukidenshi.com/catalog/g/gM-05131/


必要なソフトウエア
-----------------
- Python 2.7 or later (not 3.0)
- PyUSB
- PyUSBIO
  - https://github.com/yukkeorg/pyusbio


使い方
------
  $ ./pcounter.py -t xfiles


オプション
----------
-t
: 対象のパチンコ台を指定します。このオプションは必ず指定してください。

-n
: カウンタをリセットした状態で起動します。


ライセンス
----------
2-clause BSD Licence.  
詳しくは、LICENSE.txtを参照してください。
