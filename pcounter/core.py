# coding: utf-8

import sys
import time
import pickle
import logging

from counterplugin import ICounter
from enum import enum

USBIO_BIT = enum(
    'COUNT', 'BONUS', 'CHANCE', 'SBONUS',
    'RESERVED1', 'RESERVED2', 'LAST',
)
COUNT_INDEX = enum(
    'COUNT', 'BONUS', 'CHANCE', 'SBONUS',
    'TOTALCOUNT', 'CHAIN', 'USER',
     LAST=20
)

N_BITS = USBIO_BIT.LAST
N_COUNTS = COUNT_INDEX.LAST
BITMASK = (1 << USBIO_BIT.LAST) - 1
BITSHIFT = USBIO_BIT.LAST

logger = logging.getLogger("PCounter")

class PCounterError(Exception): pass


class PCounter(object):
  def __init__(self, hwreceiver, counterif, rcfile,
               isaddnull=True, output=None, outputcharset=None):
    self.hwreceiver = hwreceiver
    self.rcfile = rcfile
    if counterif and isinstance(counterif, ICounter):
      self.counterif = counterif
    else:
      raise TypeError("counterif は ICounter のインスタンスではありません。")

    self.invert = False
    self.isaddnull = isaddnull
    self.output = output or sys.stdout
    self.outputcharset = outputcharset or 'utf-8'
    self.counts = [0] * N_COUNTS
    self.history = []
    self._switch = [ False ] * N_BITS
    self.__prevcountstr = ""

  def saverc(self):
    try:
      with open(self.rcfile, "wb") as f:
        pickle.dump(self.counts, f, 2)
        pickle.dump(self.history, f, 2)
        f.close()
    except IOError as e:
      logger.error("カウンタ値が保存できませんでした。原因：{0}".format(e.message))

  def loadrc(self, isreset):
    if isreset:
      return
    try:
      with open(self.rcfile, "rb") as f:
        self.counts = pickle.load(f)
        self.history = pickle.load(f)
        f.close()
      return True
    except IOError as e:
      logger.error("カウンタ値を読み込めませんでした。原因：{0}".format(e.message))
      return False

  # Setter
  def setinvert(self, invert):
    if invert is not None:
      self.invert = invert

  def countup(self, port):
    for bit in (USBIO_BIT.COUNT, USBIO_BIT.BONUS, USBIO_BIT.CHANCE, USBIO_BIT.SBONUS):
      checkbit = 1 << bit
      if port & checkbit:
        # 調査中ビットの状態が0->1になるとき
        if not self._switch[bit]:
          self._switch[bit] = True
          self.counterif.func_to_on(bit, port, self.counts, self.history)
      else:
        # 調査中ビットの状態が1->0になるとき
        if self._switch[bit]:
          self._switch[bit] = False
          self.counterif.func_to_off(bit, port, self.counts, self.history)

  def display(self):
    countstr = self.counterif.func_output(self.counts, self.history)
    if countstr != self.__prevcountstr:
        self.output.write(countstr)
        if self.isaddnull:
          self.output.write("\x00")
        else:
          self.output.write("\n")
        self.output.flush()
        self.__prevcountstr = countstr

  def reset_counter(self):
    for i in len(self.counts):
      self.counts[i] = 0

  def loop(self, interval):
    prev_port = -1
    while 1:
      port = self.hwreceiver.get_port_value(self.invert)
      if port != prev_port:
        prev_port = port
        self.countup(port)
        self.display()
      time.sleep(interval)

