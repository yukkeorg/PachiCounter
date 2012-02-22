#!/usr/bin/env python
# coding: utf-8

# Copyright (c) 2011-2012, Yusuke Ohshima
# All rights reserved.
#
# This program is under the 2-clauses BSD License.
# For details, please see LICENSE file.

from __future__ import print_function

import os
import sys
import optparse
import signal
import time
import logging

logger = logging.getLogger("PCounter")
logger.addHandler(logging.StreamHandler())

BASEDIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, BASEDIR)

from pcounter import pcounter, hwreciever

INTERVAL = 0.1    # sec
RC_FILE = os.path.expanduser("~/.pcounterrc")


class CounterIfLoader(object):
  def __init__(self, location=None):
    self.location = location or "machines"
    self._mmodules = None
    self._load()

  def _load(self):
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
  parse.add_option("-t", "--type", dest="type")
  return parse.parse_args()


def main():
  opt, args = commandline_parse()

  loader = CounterIfLoader()
  cif = loader.get(opt.type)
  if cif is None:
    logger.error(u"--type オプションが指定されていないか、"
                 u"指定した内容が間違っています.")
    return

  hwr = hwreciever.HwReciever()
  hwr.init()

  pc = pcounter.PCounter(cif, RC_FILE)
  pc.load_rc(opt.isreset)

  # シグナルハンドラ
  def signal_handler(signum, stackframe):
    if signum == signal.SIGTERM:
      pc.save_rc()
      sys.exit(0)
  signal.signal(signal.SIGTERM, signal_handler)

  try:
    while True:
      port = hwr.get_port_value()
      pc.countup(port)
      pc.display()
      time.sleep(INTERVAL)
  except KeyboardInterrupt:
    pass
  finally:
    pc.save_rc()

if __name__ == '__main__':
  main()
