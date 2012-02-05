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

WAIT_TIME = 0.1    # sec
RC_FILE = os.path.expanduser("~/.pcounterrc")


def create_counterif_table():
  counterif_table = {}
  modname_list = []
  for fname in os.listdir(os.path.join(BASEDIR, "machines")):
    if fname.endswith(".py") and not fname.startswith("__init__"):
      modname = fname[:-3]
      try:
        mods = __import__("machines."+modname, globals(), locals(), [], -1)
        if callable(mods.__dict__[modname].init):
          ic = mods.__dict__[modname].init()
          if isinstance(ic, pcounter.ICounter):
            counterif_table[ic.name] = ic
      except ImportError:
        pass
  return counterif_table


def commandline_parse():
  parse = optparse.OptionParser()
  parse.add_option("-r", "--reset", dest="reset", action="store_true")
  parse.add_option("-t", "--type", dest="type")
  return parse.parse_args()


def main():
  opt, args = commandline_parse()

  icounter_table = create_counterif_table()
  print(icounter_table)
  counterif = icounter_table.get(opt.type, None)
  if counterif is None:
    logger.error(u"--type オプションが指定されていません.")
    return

  hwr = hwreciever.HwReciever()
  hwr.init()
  pc = pcounter.PCounter(counterif=counterif, 
                         rcfile=RC_FILE,
                         isreset=opt.reset)

  # シグナルハンドラ
  def signal_handler(signum, stackframe):
    if signum == signal.SIGTERM:
      pc.save()
      sys.exit(2)
  signal.signal(signal.SIGTERM, signal_handler)

  try:
    while True:
      port = hwr.get_port_value()
      pc.do(port)
      time.sleep(WAIT_TIME)
  except KeyboardInterrupt:
    pass

  pc.save()
  sys.exit(0)

if __name__ == '__main__':
  main()
