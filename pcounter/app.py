# coding: utf-8

import os
import sys
import errno
import optparse
import logging

from gi.repository import GLib

from core import PCounter, CountData
from hwr import hwreceiverFactory
from plugin import CounterPluginLoader

logger = logging.getLogger("PCounter")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

def make_resourcedir(d):
  try:
    os.makedirs(d)
  except OSError as e:
    if e.errno == errno.EEXIST:
      pass
    else:
      raise

class App(object):
  def __init__(self, basedir, pollingInterval=None, resourcedir=None):
    resourcedir = u"~/.pcounter.d" if resourcedir is None else resourcedir
    pollingInterval = 50 if pollingInterval is None else pollingInterval

    self.basedir = basedir
    self.pollingInterval = pollingInterval
    self.resourcedir = os.path.expanduser(resourcedir)

  def parse_commandline(self, args):
    parse = optparse.OptionParser()
    parse.add_option("-r", "--reset", dest="reset", action="store_true")
    parse.add_option("-i", "--invert", dest="invert", action="store_true")
    return parse.parse_args(args)

  def main(self, args):
    # コマンドラインオプションをパース
    opt, args = self.parse_commandline(args)
    if len(args) == 0:
      logger.error("カウント対象機種を指定されていません。")
      return 1
    machine = args[0]
    # ハードウエアレシーバオブジェクト作成
    hw = hwreceiverFactory("dummy")
    # 設定ファイル保存ディレクトリとファイルのパスを生成
    make_resourcedir(self.resourcedir)
    datafile = os.path.join(self.resourcedir, machine)
    # 機種ごとのカウンタインタフェースをロード
    loader = CounterPluginLoader(self.basedir, 'machines')
    mod = loader.get(machine)
    cif, cd = mod.init()
    if opt.reset == False:
      cd.load(datafile)
    # PCounterオブジェクト作成
    pc = PCounter(hw, cif, cd)
    GLib.timeout_add(self.pollingInterval, pc.loop)
    # メインループ
    try:
      GLib.MainLoop().run()
    except KeyboardInterrupt:
      pass
    finally:
      cd.save(datafile)
    return 0
