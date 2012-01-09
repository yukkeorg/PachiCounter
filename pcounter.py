#!/usr/bin/env python
# coding: utf-8

# Copyright (c) 2011, Yusuke Ohshima
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without modification, 
# are permitted provided that the following conditions are met:
# 
#   - Redistributions of source code must retain the above copyright notice, 
#     this list of conditions and the following disclaimer.
# 
#   - Redistributions in binary form must reproduce the above copyright notice, 
#     this list of conditions and the following disclaimer in the documentation 
#     and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND 
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED 
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. 
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, 
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, 
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, 
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY 
# OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE 
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF 
# THE POSSIBILITY OF SUCH DAMAGE.

from __future__ import print_function

import os
import sys
import time
import pickle
import optparse
import logging
import signal

BASEDIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, BASEDIR)

import pyusbio 

logger = logging.getLogger("PCounter")
RC_FILE = os.path.expanduser("~/.counterrc")

def enum(*seq, **named):
  enums = dict(zip(seq, range(len(seq))), **named)
  return type('Enum', (), enums)

class ICounter(object):
  def __init__(self, func_to_on=None, func_to_off=None, func_output=None):
    self.func_to_on = func_to_on
    self.func_to_off = func_to_off
    self.func_output = func_output


WAIT_TIME = 0.1    # sec
USBIO_BIT = enum('COUNT', 'BONUS', 'CHANCE', 'SBONUS', 
                 'RESERVED1', 'RESERVED2', 'LAST')
COUNT_INDEX = enum('COUNT', 'BONUS', 'CHANCE', 'SBONUS', 
                   'TOTALCOUNT', 'CHAIN', 'USER',
                   LAST=20 )

N_BITS_GROUP = pyusbio.N_PORT / USBIO_BIT.LAST
N_BITS = USBIO_BIT.LAST
N_COUNTS = COUNT_INDEX.LAST

BITMASK = (1 << USBIO_BIT.LAST) - 1
BITSHIFT =  USBIO_BIT.LAST

if sys.platform == 'win32':
  CAHR_ENCODE = 'cp932'
else:
  CHAR_ENCODE = 'utf-8'


class PCounterError(Exception): pass
class PCounterInitFailed(PCounterError): pass

class PCounter(object):
  def __init__(self, rcfile=None, outputfile=None, icounters=None, isreset=False, isaddnull=True):
    self.rcfile = rcfile if rcfile else RC_FILE 
    self.usbio = None
    self.counts = [ [0] * N_COUNTS for i in range(N_BITS_GROUP) ]
    self.onFlag = [ [ False ] * N_BITS for i in range(N_BITS_GROUP) ]
    self.icounters = icounters if icounters else ([None] * N_BITS_GROUP)
    self.isaddnull = isaddnull
    self.isreset = isreset
    self.prev_outputstrs = [""] * N_BITS_GROUP

  def init_device(self):
    self.usbio = pyusbio.USBIO()
    if not self.usbio.find_and_init():
      logger.error(u"USB-IOモジュールの初期化に失敗しました。")
      return False
    return True

  def save(self):
    try:
      with open(self.rcfile, "wb") as f:
        pickle.dump(self.counts, f, -1)
    except IOError, e:
      logger.error(u"カウンタ値が保存できませんでした。原因：{0}".format(e.message))

  def load(self):
    try:
      with open(self.rcfile, "rb") as f:
        self.counts = pickle.load(f)
      return True
    except IOError, e:
      logger.error(u"カウンタ値を読み込めませんでした。原因：{0}".format(e.message))
      return False

  def get_usbio_data(self):
    port0, port1 = self.usbio.send2read()
    port = (port1 << 8) + port0
    return port

  def countup(self, port):
    # グループ単位で処理
    for grp in xrange(N_BITS_GROUP):
      bitgroup = (port >> (N_BITS * grp)) & BITMASK
      counts = self.counts[grp]
      flags = self.onFlag[grp]
      icounter = self.icounters[grp]

      for bit in (USBIO_BIT.COUNT, USBIO_BIT.BONUS, USBIO_BIT.CHANCE, USBIO_BIT.SBONUS):
        if (bitgroup & (1 << bit)) != 0:
          # 状態がOff→Onになるとき
          if not flags[bit]:
            flags[bit] = True
            if icounter and callable(icounter.func_to_on):
              icounter.func_to_on(bit, bitgroup, counts)
        else:
          # 状態がOn→Offになるとき
          if flags[bit]:
            flags[bit] = False
            if icounter and callable(icounter.func_to_off):
              icounter.func_to_off(bit, bitgroup, counts)

  def display(self):
    for grp in range(N_BITS_GROUP):
      if self.icounters[grp] and callable(self.icounters[grp].func_output):
        countstr = self.icounters[grp].func_output(self.counts[grp])
        if countstr != self.prev_outputstrs[grp]:
          self.prev_outputstrs[grp] = countstr
          sys.stdout.write(countstr.encode(CHAR_ENCODE))
          if self.isaddnull:
            sys.stdout.write("\x00")
          sys.stdout.flush()

  def mainloop(self):
    self.init_device()
    if not self.isreset:
      if not self.load():
        raise PCounterInitFailed
    try:
      while True:
        port = self.get_usbio_data()
        self.countup(port)
        self.display()
        time.sleep(WAIT_TIME)
    except KeyboardInterrupt:
      pass
    return 0


def to_on_default(cbittype, bitgroup, counts):
  if cbittype == USBIO_BIT.COUNT:
    counts[COUNT_INDEX.COUNT] += 1
    counts[COUNT_INDEX.TOTALCOUNT] += 1
  if cbittype == USBIO_BIT.BONUS:
    counts[COUNT_INDEX.BONUS] += 1
    if bitgroup & (1 << USBIO_BIT.CHANCE):   # チャンス中なら
      counts[COUNT_INDEX.CHAIN] += 1
  if cbittype == USBIO_BIT.CHANCE:
    counts[COUNT_INDEX.CHANCE] += 1
  if cbittype == USBIO_BIT.SBONUS:
    counts[COUNT_INDEX.SBONUS] += 1


def to_off_default(cbittype, bitgroup, counts):
  if cbittype == USBIO_BIT.BONUS:
    counts[COUNT_INDEX.COUNT] = 0
  if cbittype == USBIO_BIT.CHANCE:
    counts[COUNT_INDEX.CHAIN] = 0


def decolate_number(num, digit, zero_color=None):
  if zero_color is None:
    zero_color = "#888888"
  s = "{{0:0{0}}}".format(digit).format(num)
  idx = digit - len(str(num))
  if idx < 1:
    return s
  return '<span color="{0}">'.format(zero_color) + s[0:idx] + '</span>' + s[idx:]


def gen_bonusrate(total, now):
  try:
    bonus_rate = '<span size="x-small">1/</span>{0:.1f}'.format(float(total)/now)
  except ZeroDivisionError:
    bonus_rate = '<span size="x-small">1/</span>-.-'
  return bonus_rate


def gen_chain(n_chain, suffix=None):
  if suffix is None:
    suffix = "Chain(s)"
  chain = ""
  if n_chain > 0:
    chain = '\n<span size="x-large">{0}</span> {1}'.format(decolate_number(n_chain, 3), suffix)
  return chain




### FOR CR STEALTH
def output_for_stealth(counts):
  bonus_rate = gen_bonusrate(counts[COUNT_INDEX.TOTALCOUNT], counts[COUNT_INDEX.BONUS])
  chain = gen_chain(counts[COUNT_INDEX.CHAIN], "Lock On!")
  fmt = u'<span font-desc="Ricty Bold 15"><u>Games</u>\n' \
        u'<span size="x-large">{0}</span>({1})\n' \
        u'<u>Bonus</u>\n' \
        u'<span size="large">{2}</span>/{3} ({4}){5}</span>'
  return fmt.format(decolate_number(counts[COUNT_INDEX.COUNT], 4),
                 decolate_number(counts[COUNT_INDEX.TOTALCOUNT], 5), 
                 decolate_number(counts[COUNT_INDEX.BONUS], 2), 
                 decolate_number(counts[COUNT_INDEX.CHANCE], 2), 
                 bonus_rate, chain)


### FOR CR X-FILES
COUNT_INDEX_XFILES_XR = COUNT_INDEX.USER
COUNT_INDEX_XFILES_NORMALGAMES = COUNT_INDEX.USER + 1
COUNT_INDEX_XFILES_CHANCEGAMES = COUNT_INDEX.USER + 2

def to_on_xfiles(cbittype, bitgroup, counts):
  if cbittype == USBIO_BIT.COUNT:
    counts[COUNT_INDEX.COUNT] += 1
    counts[COUNT_INDEX.TOTALCOUNT] += 1
    if bitgroup & (1 << USBIO_BIT.CHANCE):
      counts[COUNT_INDEX_XFILES_CHANCEGAMES] += 1
    else:
      counts[COUNT_INDEX_XFILES_NORMALGAMES] += 1
  if cbittype == USBIO_BIT.BONUS:
    counts[COUNT_INDEX.BONUS] += 1
    if bitgroup & (1 << USBIO_BIT.CHANCE):
      counts[COUNT_INDEX.CHAIN] += 1
      if counts[COUNT_INDEX.CHAIN] == 2:
        counts[COUNT_INDEX_XFILES_XR] += 1
  if cbittype == USBIO_BIT.CHANCE:
    counts[COUNT_INDEX.CHANCE] += 1
  if cbittype == USBIO_BIT.SBONUS:
    counts[COUNT_INDEX.SBONUS] += 1

def to_off_xfiles(cbittype, bitgroup, counts):
  if cbittype == USBIO_BIT.BONUS:
    counts[COUNT_INDEX.COUNT] = 0
  if cbittype == USBIO_BIT.CHANCE:
    counts[COUNT_INDEX.CHAIN] = 0
  
def output_for_xfiles(counts):
  data_table = {
     'count':       decolate_number(counts[COUNT_INDEX.COUNT], 4), 
     'totalcount':  decolate_number(counts[COUNT_INDEX.TOTALCOUNT], 5), 
     'bonuscount':  decolate_number(counts[COUNT_INDEX.SBONUS], 3),
     'uzcount':     decolate_number(counts[COUNT_INDEX.CHANCE], 3), 
     'reserved':    decolate_number(counts[COUNT_INDEX.BONUS], 3),
     'xrcount':     decolate_number(counts[COUNT_INDEX_XFILES_XR], 3),
     'normalcount': decolate_number(counts[COUNT_INDEX_XFILES_NORMALGAMES], 4),
     'uzxrcount':   decolate_number(counts[COUNT_INDEX_XFILES_CHANCEGAMES], 4),
     'xr_rate':     gen_bonusrate(counts[COUNT_INDEX_XFILES_NORMALGAMES], counts[COUNT_INDEX_XFILES_XR]), 
     'uz_rate':     gen_bonusrate(counts[COUNT_INDEX_XFILES_NORMALGAMES], counts[COUNT_INDEX.CHANCE]), 
     'bonus_rate':  gen_bonusrate(counts[COUNT_INDEX.TOTALCOUNT], counts[COUNT_INDEX.SBONUS]),
     'xr_chain':    gen_chain(counts[COUNT_INDEX.CHAIN] - 1),
  }

  fmt = u'<span font-desc="Ricty Bold 14">' \
        u'<span size="small"><u>Now</u></span>\n<span size="x-large">{count}</span>\n' \
        u'<span size="small"><u>Total</u></span>\n<span size="large">{totalcount}</span>({normalcount}+{uzxrcount})\n'
  if counts[COUNT_INDEX.CHAIN] > 1:
    fmt = fmt + u'<span size="small"><u>XTRA-RUSH</u></span>{xr_chain}'
  else:
    fmt = fmt + u'<span size="small"><u>Bonus</u></span>\n.XR:<span size="large">{xrcount}</span>({xr_rate})\n.UZ:<span size="large">{uzcount}</span>({uz_rate})\nALL:<span size="large">{bonuscount}</span>({bonus_rate})'
  fmt = fmt + u'</span>'

  return fmt.format(**data_table)




if __name__ == '__main__':
  icounter_table= {
    'stealth' : ICounter(to_on_default, 
                         to_off_default, 
                         output_for_stealth),
    'xfiles'  : ICounter(to_on_xfiles, 
                         to_off_xfiles, 
                         output_for_xfiles),
  }

  parse = optparse.OptionParser()
  parse.add_option("-r", "--reset", dest="reset", action="store_true")
  parse.add_option("-t", "--types", dest="types")
  (opt, args) = parse.parse_args()

  icounters = [None] * N_BITS_GROUP
  if opt.types:
    _types = opt.types.split(',')
    l = min(len(_types), N_BITS_GROUP)
    icounters[0:l] = [ icounter_table.get(_types[i], None) for i in range(l) ]

  pc = PCounter(icounters=icounters, isreset=opt.reset)

  # シグナルハンドラ用メソッド
  def signal_handler(signum, stackframe):
    if signum == signal.SIGTERM:
      pc.save()
      sys.exit(2)
  signal.signal(signal.SIGTERM, signal_handler)

  ret = pc.mainloop()
  pc.save()

  sys.exit(ret)

