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
from pcounter.hwr import hwreceiverFactory
from pcounter.plugin import PluginLoader

logger = logging.getLogger("PCounter")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


class App(object):
  def __init__(self, basedir, pollingInterval=None, resourcedir=None):
    resourcedir = resourcedir or u"~/.pcounter.d" 
    pollingInterval = pollingInterval or 50

    self.basedir = basedir
    self.pollingInterval = pollingInterval
    self.resourcedir = os.path.expanduser(resourcedir)

  def make_resourcedir(self):
    """ リソースディレクトリを作成する """
    try:
      os.makedirs(self.resourcedir)
    except OSError as e:
      if e.errno == errno.EEXIST:
        pass
      else:
        raise

  def parse_commandline(self, args):
    """ コマンドラインをパースする """
    parse = optparse.OptionParser()
    parse.add_option("-r", "--reset", dest="reset", action="store_true")
    return parse.parse_args(args)

  def main(self, args=None):
    # コマンドラインオプションをパース
    if args is None:
      args = sys.argv[1:]
    opt, args = self.parse_commandline(args)

    if len(args) == 0:
      logger.error("カウント対象機種を指定されていません。")
      return 1

    machine = args[0]

    # 設定ファイル保存ディレクトリとファイルのパスを生成
    self.make_resourcedir()
    datafilepath = os.path.join(self.resourcedir, machine)
    # ハードウエアレシーバオブジェクト作成
    hw = hwreceiverFactory("usbio")
    # 機種ごとのカウンタインタフェースをロード
    loader = PluginLoader(self.basedir, 'machines')
    plugin = loader.get(machine)()
    cd = plugin.createCountData()
    if not opt.reset == True:
      cd.load(datafilepath)

    loop = GLib.MainLoop()
    exit_code = 0

    # PCounterオブジェクト作成
    pc = PCounter(hw, plugin, cd)
    GLib.timeout_add(self.pollingInterval, pc.loop)

    # シグナルハンドラ設定
    if sys.platform != 'win32':
      def signal_handler(user_data):
        loop.quit()
        exit_code = 127
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
      print("""
            Counter data is saved to {}""".format(datafilepath),
            file=sys.stderr)

    return exit_code
