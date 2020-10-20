# vim: ts=4 sts=4 sw=4 et
#####################################################################
# Pachi Counter
# Copyright (c) 2011-2020, Yusuke Ohshima All rights reserved.
#
# License: MIT.
# For details, please see LICENSE file.
#####################################################################

import os
import sys
import signal
import argparse

import gevent

from pachicounter.core import PCounter
from pachicounter.hardware import hwReceiverFactory, HwReceiverError
from pachicounter.plugin import PluginLoader


BASEDIR = os.path.dirname(os.path.realpath(os.path.join(__file__)))


def _setup_logger():
    import logging
    logger = logging.getLogger("PCounter")
    loglevel = os.environ.get("PACHICOUNTER_LOGLEVEL")
    if loglevel is not None:
        logger.setLevel(loglevel)

    message_format = logging.Formatter("%(asctime)s [%(levelname)-6s] %(message)s")
    handler = logging.StreamHandler()
    handler.setFormatter(message_format)
    logger.addHandler(handler)

    return logger


logger = _setup_logger()


class App:
    def __init__(self, basedir, pollingInterval=None, resourcedir=None):
        if pollingInterval is None:
            pollingInterval = 50  # msec

        if resourcedir is None:
            resourcedir = "~/.config/pcounter.d"

        self.basedir = basedir
        self.pollingInterval = pollingInterval / 1000
        self.resourcedir = os.path.expanduser(resourcedir)

    def main(self, args=None):
        logger.info("Pachi Counter")

        parser = argparse.ArgumentParser()
        parser.add_argument("-r", "--reset", dest="reset", action="store_true")
        parser.add_argument("machine")
        args = parser.parse_args(args)

        machine = args.machine

        # 設定ファイル保存ディレクトリとファイルのパスを生成
        os.makedirs(self.resourcedir, exist_ok=True)
        datafilepath = os.path.join(self.resourcedir, machine)
        logger.info("Datafile: " + datafilepath)

        # ハードウエアレシーバオブジェクト作成
        try:
            hardware = hwReceiverFactory("usbio")
        except HwReceiverError as e:
            logger.critical(e)
            return 1
        logger.info("Hardware: " + hardware.receiver_name)

        # 引数で指定され機種に対応したモジュールをインポートする
        loader = PluginLoader()
        machine_plugin = loader.getInstance(machine)

        counter_data = machine_plugin.createCountData()
        if not args.reset:
            counter_data.load(datafilepath)

        # PCounterオブジェクト作成
        pc = PCounter(hardware, machine_plugin, counter_data)

        # メインループオブジェクト作成
        def mainloop():
            while True:
                gevent.sleep(self.pollingInterval)
                pc.loop()

        greenlet = gevent.spawn(mainloop)

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


def main():
    App(BASEDIR).main()


if __name__ == "__main__":
    main()
