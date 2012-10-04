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

from pcounter import pcounter, usbioreceiver, pluginloader

INTERVAL = 0.1    # sec
RC_DIR = os.path.expanduser("~/.pcounter.d")


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
  hwr = usbioreceiver.UsbIoReceiver()
  hwr.init()

  # 機種ごとのカウンタインタフェースをロード
  loader = pluginloader.CounterInterfacePluginLoader('machines')
  cif = loader.get(opt.type)
  if cif is None:
    logger.error("--type または -t オプションが指定されていないか、間違っています。")
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
