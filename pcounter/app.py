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
    resourcedir = u"~/.pcounter.d" if resourcedir is None else resourcedir
    pollingInterval = 50 if pollingInterval is None else pollingInterval

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
    try:
    parse = optparse.OptionParser()
    parse.add_option("-r", "--reset", dest="reset", action="store_true")
    return parse.parse_args(args)

  def main(self, args):
    # コマンドラインオプションをパース
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
    # PCounterオブジェクト作成
    pc = PCounter(hw, plugin, cd)
    GLib.timeout_add(self.pollingInterval, pc.loop)
    # シグナルハンドラ設定
    def signal_handler(signum, stackframe):
      cd.save(datafilepath)
      sys.exit(128)
    signal.signal(signal.SIGTERM, signal_handler)
    # メインループ
    try:
      GLib.MainLoop().run()
    except KeyboardInterrupt:
      pass
    finally:
      cd.save(datafilepath)
    return 0
