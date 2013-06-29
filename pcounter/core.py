# coding: utf-8
# vim: ts=2 sts=2 sw=2 et

import sys
import time
import logging
try:
  import ujson as json
except ImportError:
  try:
    import simplejson as json
  except ImportError:
    import json

from hwr import HwReceiver
from plugin import ICounter
from pctypes import enum

logger = logging.getLogger("PCounter")

USBIO_BIT = enum('COUNT', 'BONUS', 'CHANCE', 'SBONUS', 'LAST')
N_BITS = USBIO_BIT.LAST
BITMASK = (1 << USBIO_BIT.LAST) - 1

class PCounterError(Exception): pass

class CountData(object):
  def __init__(self, colnames):
    self.counts = dict((k, 0) for k in colnames)
    self.history = []

  def __getitem__(self, key):
    return self.counts[key]

  def __setitem__(self, key, val):
    self.counts[key] = val

  def resetCounter(self):
    for k in self.counts:
      self.counts[k] = 0

  def resetHistory(self):
    del self.history[:]

  def save(self, filename):
    with open(filename, 'wb') as fp:
      json.dump(self.__dict__, fp)

  def load(self, filename):
    with open(filename, 'rb') as fp:
      try:
        data = json.load(fp)
      except:
        return
    if 'counts' in data:
      self.counts.update(data['counts'])
    if 'history' in data:
      self.resetHistory()
      self.history.extend(data['history'])


class PCounter(object):
  def __init__(self, hr, cif, countdata, eol=None, output=None):
    if not isinstance(hr, HwReceiver):
      raise TypeError(u"hr は HwReceiver のインスタンスではありません。")
    if not isinstance(cif, ICounter):
      raise TypeError(u"cif は ICounter のインスタンスではありません。")

    self.hr = hr
    self.cif = cif
    self.eol = '\0' if eol is None else eol
    self.output = output or sys.stdout
    self.countdata = countdata
    self.__switch = 0
    self.__prevcountstr = ""
    self.__prevportval = -1

  def countup(self, portval):
    for bit in (USBIO_BIT.COUNT, USBIO_BIT.BONUS, 
                USBIO_BIT.CHANCE, USBIO_BIT.SBONUS):
      checkbit = 1 << bit
      edgeup = bool(portval & checkbit)
      state = bool(self.__switch & checkbit)
      if edgeup == True and state == False:
        # 調査中ビットの状態が0->1になるとき
        self.__switch |= checkbit
        self.cif.on(bit, portval, self.countdata)
      elif edgeup == False and state == True:
        # 調査中ビットの状態が1->0になるとき
        self.__switch &= (~checkbit)
        self.cif.off(bit, portval, self.countdata)

  def display(self):
    countstr = self.cif.build(self.countdata)
    if countstr != self.__prevcountstr:
        self.__prevcountstr = countstr
        self.output.write(countstr)
        self.output.write(self.eol)
        self.output.flush()

  def loop(self):
    portval = self.hr.get_port_value()
    if portval != self.__prevportval:
      self.__prevportval = portval
      self.countup(portval)
      self.display()
    return True

