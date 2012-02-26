# coding: utf-8


import sys
import pickle
import logging
logger = logging.getLogger("PCounter")

from . import util


USBIO_BIT = util.enum('COUNT', 'BONUS', 'CHANCE', 'SBONUS', 
                      'RESERVED1', 'RESERVED2', 'LAST')
COUNT_INDEX = util.enum('COUNT', 'BONUS', 'CHANCE', 'SBONUS', 
                        'TOTALCOUNT', 'CHAIN', 'USER',
                        LAST=20 )

N_BITS = USBIO_BIT.LAST
N_COUNTS = COUNT_INDEX.LAST
BITMASK = (1 << USBIO_BIT.LAST) - 1
BITSHIFT = USBIO_BIT.LAST

class PCounterError(Exception): pass
class PCounterInitFailed(PCounterError): pass

class ICounter(object):
  def __init__(self, name=None, func_to_on=None, func_to_off=None, func_output=None):
    self.name = name
    self.func_to_on = func_to_on
    self.func_to_off = func_to_off
    self.func_output = func_output


class PCounter(object):
  def __init__(self, counterif, rcfile, 
               isaddnull=True, output=None, outputcharset=None):
    self.rcfile = rcfile
    self.counterif = counterif
    self.isaddnull = isaddnull
    self.output = output or sys.stdout
    self.outputcharset = outputcharset or 'utf-8'

    self.counts = [0] * N_COUNTS 
    self.history = []
    self._switch = [ False ] * N_BITS 
    self._prev_outputstrs = "" 


  def save_rc(self):
    try:
      with open(self.rcfile, "wb") as f:
        pickle.dump(self.counts, f, 2)
        pickle.dump(self.history, f, 2)
    except IOError as e:
      logger.error("カウンタ値が保存できませんでした。原因：{0}".format(e.message))

  def load_rc(self, isreset):
    if isreset:
      return
    try:
      with open(self.rcfile, "rb") as f:
        self.counts = pickle.load(f)
        self.history = pickle.load(f)
      return True
    except IOError as e:
      logger.error("カウンタ値を読み込めませんでした。原因：{0}".format(e.message))
      return False

  def countup(self, port):
    for bit in (USBIO_BIT.COUNT, USBIO_BIT.BONUS, USBIO_BIT.CHANCE, USBIO_BIT.SBONUS):
      checkbit = 1 << bit
      if port & checkbit:
        # 状態がOff→Onになるとき
        if not self._switch[bit]:
          self._switch[bit] = True
          if self.counterif and callable(self.counterif.func_to_on):
            self.counterif.func_to_on(bit, port, self.counts, self.history)
      else:
        # 状態がOn→Offになるとき
        if self._switch[bit]:
          self._switch[bit] = False
          if self.counterif and callable(self.counterif.func_to_off):
            self.counterif.func_to_off(bit, port, self.counts, self.history)

  def display(self):
    if self.counterif and callable(self.counterif.func_output):
      countstr = self.counterif.func_output(self.counts, self.history)
      if countstr != self._prev_outputstrs:
        self._prev_outputstrs = countstr
        #self.output.write(countstr.encode(self.outputcharset))
        self.output.write(countstr)
        if self.isaddnull:
          self.output.write("\x00")
        self.output.flush()

  def reset_counter(self):
    for i in len(self.counts):
      self.counts[i] = 0


def to_on_default(cbittype, iostatus, counts, history):
  if cbittype == USBIO_BIT.COUNT:
    counts[COUNT_INDEX.COUNT] += 1
    counts[COUNT_INDEX.TOTALCOUNT] += 1
  if cbittype == USBIO_BIT.BONUS:
    counts[COUNT_INDEX.BONUS] += 1
    if iostatus & (1 << USBIO_BIT.CHANCE):   # チャンス中なら
      counts[COUNT_INDEX.CHAIN] += 1
  if cbittype == USBIO_BIT.CHANCE:
    counts[COUNT_INDEX.CHANCE] += 1
  if cbittype == USBIO_BIT.SBONUS:
    counts[COUNT_INDEX.SBONUS] += 1


def to_off_default(cbittype, iostatus, counts, history):
  if cbittype == USBIO_BIT.BONUS:
    counts[COUNT_INDEX.COUNT] = 0
  if cbittype == USBIO_BIT.CHANCE:
    counts[COUNT_INDEX.CHAIN] = 0


def output_default(counts, history):
  pass


