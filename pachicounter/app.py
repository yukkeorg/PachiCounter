# coding: utf-8
# vim: ts=4 sts=4 sw=4 et

"""\
Pachi Counter
Copyright (c) 2011-2020, Yusuke Ohshima All rights reserved.
License: MIT.
For details, please see LICENSE file.
"""

import os
import sys
import signal
import argparse

import gevent

from pachicounter.core import PCounter
from pachicounter.hardware import hwReceiverFactory, HwReceiverError
from pachicounter.plugin import PluginLoader

import logging
logger = logging.getLogger("PCounter")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())




class App:
    def __init__(self, basedir, pollingInterval=None, resourcedir=None):
        if pollingInterval is None:
            pollingInterval = 50  # msec

        if resourcedir is None:
            resourcedir = "~/.pcounter.d"

        self.basedir = basedir
        self.pollingInterval = pollingInterval / 1000
        self.resourcedir = os.path.expanduser(resourcedir)

    def main(self, args=None):
        parser = argparse.ArgumentParser()
        parser.add_argument("-r", "--reset", dest="reset", action="store_true")
        parser.add_argument("machine")
        args = parser.parse_args(args)

        machine = args.machine

        # 設定ファイル保存ディレクトリとファイルのパスを生成
        os.makedirs(self.resourcedir, exist_ok=True)
        datafilepath = os.path.join(self.resourcedir, machine)

        # ハードウエアレシーバオブジェクト作成
        try:
            hw = hwReceiverFactory("usbio")
        except HwReceiverError as e:
            logger.critical(e)
            return 1

        # 引数で指定され機種に対応したモジュールをインポートする
        loader = PluginLoader()
        plugin = loader.getInstance(machine)

        counter_data = plugin.createCountData()
        if not args.reset:
            counter_data.load(datafilepath)

        # PCounterオブジェクト作成
        pc = PCounter(hw, plugin, counter_data)

        # メインループオブジェクト作成
        def loop():
            while True:
                gevent.sleep(self.pollingInterval)
                pc.loop()

        greenlet = gevent.spawn(loop)

        # シグナルハンドラ設定
        if sys.platform != "win32":
            gevent.signal_handler(signal.SIGTERM, lambda: greenlet.kill())

        # メインループ
        try:
            greenlet.join()
        except KeyboardInterrupt:
            pass
        finally:
            counter_data.save(datafilepath)
            logger.info("Counter data saved to {}".format(datafilepath))

        return 0
