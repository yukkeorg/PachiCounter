#!/usr/bin/env python
# coding: utf-8

# Copyright (c) 2011-2012, Yusuke Ohshima
# All rights reserved.
#
# This program is under the 2-clauses BSD License.
# For details, please see LICENSE file.

import os
import sys
import errno
import optparse
import signal
import time
import logging

logger = logging.getLogger("PCounter")
logger.addHandler(logging.StreamHandler())

BASEDIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, BASEDIR)

from pcounter import pcounter, hwreceiver

INTERVAL = 0.1    # sec
RC_DIR = os.path.expanduser("~/.pcounter.d")


class CounterInterfaceLoader(object):
  def __init__(self, location=None):
    self.location = location or "machines"
    self._mmodules = None
    self._load_machine_module()

  def _load_machine_module(self):
    """ machines ディレクトリから、機種別の処理を動的に読み込みます。
    """
    modnames = []
    for fname in os.listdir(os.path.join(BASEDIR, self.location)):
      if fname.endswith(".py") and not fname.startswith("__init__"):
        modnames.append(fname[:-3])
    self._mmodules = __import__(self.location, globals(), locals(), modnames, -1)

  def get(self, modname):
    if modname and not modname.startswith('__'):
      mod = self._mmodules.__dict__.get(modname)
      if mod and callable(mod.init):
        ic = mod.init()
        if isinstance(ic, pcounter.ICounter):
          return ic
    return None


def commandline_parse():
  parse = optparse.OptionParser()
  parse.add_option("-r", "--reset", dest="reset", action="store_true")
  parse.add_option("-i", "--invert", dest="invert", action="store_true")
  parse.add_option("-t", "--type", dest="type")
  return parse.parse_args()


def make_userconfigdir(d):
  try:
    os.makedirs(d)
  except OSError as e:
    if e.errno == errno.EEXIST:
      pass
    else:
      raise
  
def main():
  opt, args = commandline_parse()

  make_userconfigdir(RC_DIR)
  rc_file = os.path.join(RC_DIR, opt.type)
 
  # ハードウエアレシーバオブジェクト作成
  hwr = hwreceiver.HwReceiver()
  hwr.init()

  # 機種ごとのカウンタインタフェースをロード
  loader = CounterInterfaceLoader()
  cif = loader.get(opt.type)
  if cif is None:
    logger.error("--type option is not specified or missing.")
    return

  # PCounterオブジェクト作成
  pc = pcounter.PCounter(hwr, cif, rc_file)
  pc.loadrc(opt.reset)
  pc.setinvert(opt.invert)

  # シグナルハンドラ設定
  def signal_handler(signum, stackframe):
    # Ctrl+C 受信
    if signum == signal.SIGTERM:
      pc.saverc()
      sys.exit(1)
  signal.signal(signal.SIGTERM, signal_handler)

  try:
    pc.loop(INTERVAL)
  except KeyboardInterrupt:
    pass
  finally:
    pc.saverc()

if __name__ == '__main__':
  main()
