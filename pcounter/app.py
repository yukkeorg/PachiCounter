# coding: utf-8
# vim: ts=2 sts=2 sw=2 et

import os
import sys
import signal
import errno
import optparse
import logging

from gi.repository import GLib

from pcounter.core import PCounter, CountData
from pcounter.hwr import hwReceiverFactory, HwReceiverError
from pcounter.plugin import PluginLoader

logger = logging.getLogger("PCounter")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


def makedir(target):
  """ リソースディレクトリを作成する """
  try:
    os.makedirs(target)
  except OSError as e:
    if e.errno == errno.EEXIST:
      pass
    else:
      raise


class App(object):
  def __init__(self, basedir, pollingInterval=None, resourcedir=None):
    pollingInterval = pollingInterval or 50  # msec
    resourcedir = resourcedir or u"~/.pcounter.d" 

    self.basedir = basedir
    self.pollingInterval = pollingInterval
    self.resourcedir = os.path.expanduser(resourcedir)


  def main(self, args=None):
    # コマンドラインオプションをパース
    if args is None:
      args = sys.argv[1:]

    parser = optparse.OptionParser()
    parser.add_option("-r", "--reset", dest="reset", action="store_true")
    opt, args = parser.parse_args(args)

    if len(args) == 0:
      logger.critical("カウント対象機種を指定されていません。")
      return 1

    machine = args[0]

    # 設定ファイル保存ディレクトリとファイルのパスを生成
    makedir(self.resourcedir)
    datafilepath = os.path.join(self.resourcedir, machine)
    # ハードウエアレシーバオブジェクト作成
    try:
      hw = hwReceiverFactory("usbio")
    except HwReceiverError as e:
      logger.critical(e)
      return 1

    loader = PluginLoader(self.basedir, "machines")
    plugin = loader.get(machine)()
    cd = plugin.createCountData()
    if not opt.reset == True:
      cd.load(datafilepath)

    loop = GLib.MainLoop()

    # PCounterオブジェクト作成
    pc = PCounter(hw, plugin, cd)
    GLib.timeout_add(self.pollingInterval, pc.loop)

    # シグナルハンドラ設定
    if sys.platform != "win32":
      def signal_handler(user_data):
        loop.quit()
      GLib.unix_signal_add(GLib.PRIORITY_DEFAULT,
                           signal.SIGTERM,
                           signal_handler,
                           None)

    # メインループ
    try:
      loop.run()
    except KeyboardInterrupt:
      pass
    finally:
      cd.save(datafilepath)
      logger.info("Counter data is saved to {}".format(datafilepath))

    return 0
