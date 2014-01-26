# coding: utf-8
# vim: ts=2 sts=2 sw=2 et

import time

from pcounter.core import USBIO_BIT, CountData, json
from pcounter.plugin import ICounter, UtilsMixin
from pcounter.util import gen_bonusrate, bit_is_enable

class DeltaTime(object):
  def __init__(self):
    self.__prev = time.time()

  def getDelta(self):
    now = time.time()
    d = now - self.__prev
    self.__prev = now
    return d

  def check(self):
    self.__prev = time.time()


class BonusRoundInfo(object):
  def __init__(self, _round, _maxsec, _bonuspt):
    self.round = _round
    self.maxsec = _maxsec
    self.bonuspt = _bonuspt

def calcLossPerSecNorm(bc, r):
  return 1.6667 * (-1.0 + ((bc * r) / (250.0 + bc * r)))

def calcLossPerSecChance(base):
  return 1.6667 * (-1.0 + base)


class uforush(ICounter, UtilsMixin):
  LosePerSec = (calcLossPerSecNorm(3, 20),  # 打出し1.6個/s 250玉で60個賞球があるときの
                calcLossPerSecChance(0.90))

  BonusRound = (
    BonusRoundInfo( 1,   55.0,  80),
    BonusRoundInfo( 2,   65.0, 160),
    BonusRoundInfo( 3,   76.0, 240),
    BonusRoundInfo( 4,   88.0, 320),
    BonusRoundInfo( 5,  100.0, 400),
    BonusRoundInfo( 6,  110.0, 480),
    BonusRoundInfo( 7,  120.0, 560),
    BonusRoundInfo( 8,  136.0, 640),
    BonusRoundInfo(12, 9999.0, 960),
  )

  def __init__(self):
    self.gcdelta = DeltaTime()
    self.bonustime = DeltaTime()

  def createCountData(self):
    return CountData(('count', 'totalcount', 'bonus', 
                    'chance', 'chain', 'chancetime', 'isbonus',
                    'sbonus', 'spg', 'spb', 'pbr', 'voutput'))

  def detectBonus(self, t):
    for bi in self.BonusRound:
      if t < bi.maxsec:
        return bi

  def on(self, cbtype, iostatus, cd):
    if cbtype == USBIO_BIT.COUNT:
      cd['count'] += 1
      ischance = bit_is_enable(iostatus, USBIO_BIT.CHANCE)
      if not ischance:
        cd['totalcount'] += 1

      d = self.gcdelta.getDelta()
      cd['spg'] = d
      cd['voutput'] += (min(40.0, d) * self.LosePerSec[1 if ischance else 0])

    elif cbtype == USBIO_BIT.BONUS:
      self.bonustime.check()
      cd['bonus'] += 1
      cd['isbonus'] = 1
      if bit_is_enable(iostatus, USBIO_BIT.CHANCE):
        cd['chain'] += 1

    elif cbtype == USBIO_BIT.CHANCE:
      cd['chance'] += 1
    elif cbtype == USBIO_BIT.SBONUS:
      cd['sbonus'] += 1


  def off(self, cbtype, iostatus, cd):
    if cbtype == USBIO_BIT.BONUS:
      cd['isbonus'] = 0
      cd['count'] = 0
      if bit_is_enable(iostatus, USBIO_BIT.CHANCE):
        cd['chancetime'] = 1
      self.gcdelta.check()
      d = self.bonustime.getDelta()
      bi = self.detectBonus(d)
      cd['spb'] = d
      cd['voutput'] += bi.bonuspt
      cd['pbr'] = bi.round

    elif cbtype == USBIO_BIT.CHANCE:
      cd['chain'] = 0
      cd['chancetime'] = 0
      cd['totalcount'] += cd['count']


  def build(self, cd):
    d = cd.counts
    bonusrate = gen_bonusrate(d['totalcount'], d['chance'])
    if cd['chancetime'] == 1: 
      color = self.rgb2int(0xff, 0xff, 0x33)
      dd = {
        'framesvg0': 'resource/orangeflame_wide.svg',
        '0'  : { 'text': '{count}<small></small>'.format(**d)},
        '1'  : { 'text': '{chain}<small> CHAIN</small>'.format(**d)},
        '2'  : { 'text': '{bonus}<small> ({chance})</small>'.format(**d) },
        '3'  : { 'text': '{voutput:.0f}<small><small>PTS</small></small>'.format(**d)},
        '4'  : { 'text': 'SPG:{spg:.2f} SPB:{spb:.2f} PBR:{pbr}r'.format(**d)},
      }
      self.bulk_set_color(dd, color)
      dd['0']['color'] = self.rgb2int(0, 0, 0)
    else:
      dd = {
        'framesvg0': 'resource/blueflame_wide.svg',
        '0' : { 'text': '{count}<small> / {totalcount}</small>'.format(**d) },
        '1' : { 'text': bonusrate },
        '2' : { 'text': '{bonus}<small> ({chance})</small>'.format(**d) },
        '3' : { 'text': '{voutput:.0f}<small><small>PTS</small></small>'.format(**d)},
        '4' : { 'text': 'SPG:{spg:.2f} SPB:{spb:.2f} PBR:{pbr}r'.format(**d)},
      }
      if cd['isbonus'] == 1:
        dd['framesvg0'] = 'resource/orangeflame_wide.svg'
        self.bulk_set_color(dd, self.rgb2int(0xff, 0xff, 0x33))
        dd['0']['color'] = self.rgb2int(0, 0, 0)
      else:
        self.bulk_set_color(dd, self.rgb2int(0xff, 0xff, 0xff))
    return json.dumps(dd)
