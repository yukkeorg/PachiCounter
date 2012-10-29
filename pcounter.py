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
import logging


BASEDIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, BASEDIR)

logger = logging.getLogger("PCounter")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

from pcounter import pcounter, usbioreceiver, pluginloader


INTERVAL = 0.1    # sec
RC_DIR = os.path.expanduser("~/.pcounter.d")


def parse_commandline():
  parse = optparse.OptionParser()
  parse.add_option("-r", "--reset", dest="reset", action="store_true")
  parse.add_option("-i", "--invert", dest="invert", action="store_true")
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
  # コマンドラインオプションをパース
  opt, args = parse_commandline()
  if len(args) == 0:
    logger.error("カウント対象機種を指定されていません。")
    return 1

  machine = args[0]

  # 機種ごとのカウンタインタフェースをロード
  loader= pluginloader.CounterInterfacePluginLoader(BASEDIR, 'machines')
  cif = loader.get(machine)
  if cif is None:
    logger.error("カウント対象機種の指定が間違っています。")
    return 1

  # ハードウエアレシーバオブジェクト作成
  hwr = usbioreceiver.UsbIoReceiver()
  hwr.init()

  # 設定ファイル保存ディレクトリとファイルのパスを生成
  make_userconfigdir(RC_DIR)# Ctrl+C 受信
  rc_file = os.path.join(RC_DIR, machine)

  # PCounterオブジェクト作成
  pc = pcounter.PCounter(hwr, cif, rc_file)
  pc.loadrc(opt.reset)
  pc.setinvert(opt.invert)

  # シグナルハンドラ設定
  def signal_handler(signum, stackframe):
    if signum == signal.SIGTERM: # Ctrl+C 受信
      pc.saverc()
      sys.exit(1)
  signal.signal(signal.SIGTERM, signal_handler)

  try:
    pc.loop(INTERVAL)
  except KeyboardInterrupt:
    pass
  finally:
    pc.saverc()

  return 0


if __name__ == '__main__':
  sys.exit(main())
