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
- Python 2.7 or later (not 3.0)
- PyUSB
- PyUSBIO
  - https://github.com/yukkeorg/pyusbio

オプション
----------
-t <machine>
: 対象の機種を指定します。このオプションは必ず指定する必要があります。

-n
: カウンタをリセットした状態で起動します。

例
--
  $ ./pcounter.py -t xfiles

ライセンス
----------
2-clause BSD Licence.  
詳しくは、LICENSE.txtを参照してください。
