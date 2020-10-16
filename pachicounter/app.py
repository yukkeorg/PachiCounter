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

from gi.repository import GLib

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
        pc = PCounter(hw, plugin, cd)

        # メインループオブジェクト作成
        loop = GLib.MainLoop()

        # シグナルハンドラ設定
        if sys.platform != "win32":
            def signal_handler(user_data):
                loop.quit()
            GLib.unix_signal_add(GLib.PRIORITY_DEFAULT,
                                 signal.SIGTERM,
                                 signal_handler,
                                 None)

        GLib.timeout_add(self.pollingInterval, pc.loop)

        # メインループ
        try:
            loop.run()
        except KeyboardInterrupt:
            pass
        finally:
            cd.save(datafilepath)
            logger.info("Counter data is saved to {}".format(datafilepath))
        return 0
