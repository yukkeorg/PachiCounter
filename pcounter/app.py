# coding: utf-8

import os
import sys
import errno
import optparse
import signal
import logging

from core import PCounter
from usbioreceiver import UsbIoReceiver
from counterplugin import CounterPluginLoader

logger = logging.getLogger("PCounter")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


class App(object):

  def __init__(self, basedir, commandline,
               pollingInterval=0.05, resourcedir=None):
    if resourcedir is None:
      resourcedir = u"~/.pcounter.d"
    self.commandline = commandline
    self.basedir = basedir
    self.pollingInterval = pollingInterval
    self.resourcedir = os.path.expanduser(resourcedir)

  def parse_commandline(self):
    parse = optparse.OptionParser()
    parse.add_option("-r", "--reset", dest="reset", action="store_true")
    parse.add_option("-i", "--invert", dest="invert", action="store_true")
    return parse.parse_args(self.commandline)

  def make_resourcedir(self):
    try:
      os.makedirs(self.resourcedir)
    except OSError as e:
      if e.errno == errno.EEXIST:
        pass
      else:
        raise

  def main(self):
    # コマンドラインオプションをパース
    opt, args = self.parse_commandline()
    if len(args) == 0:
      logger.error("カウント対象機種を指定されていません。")
      return 1
    machine = args[0]

    # 機種ごとのカウンタインタフェースをロード
    loader = CounterPluginLoader(self.basedir, 'machines')
    cif = loader.get(machine)
    if cif is None:
      logger.error("カウント対象機種の指定が間違っています。")
      return 1

    # ハードウエアレシーバオブジェクト作成
    hwr = UsbIoReceiver()

    # 設定ファイル保存ディレクトリとファイルのパスを生成
    self.make_resourcedir()
    rc_file = os.path.join(self.resourcedir, machine)

    # PCounterオブジェクト作成
    pc = PCounter(hwr, cif, rc_file)
    pc.loadrc(opt.reset)
    pc.setinvert(opt.invert)

    # シグナルハンドラ設定
    def signal_handler(signum, stackframe):
      if signum == signal.SIGTERM: # Ctrl+C 受信
        pc.saverc()
        sys.exit(1)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
      pc.loop(self.pollingInterval)
    except KeyboardInterrupt:
      pass
    finally:
      pc.saverc()

    return 0
