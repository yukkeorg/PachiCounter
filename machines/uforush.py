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
  def __init__(self, nround, limitsec, gainpts):
    self.nround = nround
    self.limitsec = limitsec
    self.gainpts = gainpts


def calcLpsOnNorm(bc, r):
  return 1.6667 * (-1.0 + ((bc * r) / (250.0 + bc * r)))

def calcLpsOnChance(base):
  return 1.6667 * (-1.0 + base)


class uforush(ICounter, UtilsMixin):
  LPS = (calcLpsOnNorm(3, 20),     # losepts/sec
         calcLpsOnChance(0.90))

  MaxSPC = 40.0   # sec/count

  BonusRound = (
    BonusRoundInfo(nround= 1, limitsec=  55.0, gainpts= 80),
    BonusRoundInfo(nround= 2, limitsec=  65.0, gainpts=160),
    BonusRoundInfo(nround= 3, limitsec=  76.0, gainpts=240),
    BonusRoundInfo(nround= 4, limitsec=  88.0, gainpts=320),
    BonusRoundInfo(nround= 5, limitsec= 100.0, gainpts=400),
    BonusRoundInfo(nround= 6, limitsec= 110.0, gainpts=480),
    BonusRoundInfo(nround= 7, limitsec= 120.0, gainpts=560),
    BonusRoundInfo(nround= 8, limitsec= 136.0, gainpts=640),
    BonusRoundInfo(nround=12, limitsec=9999.0, gainpts=960),
  )

  def __init__(self):
    self.gcdelta = DeltaTime()
    self.bonustime = DeltaTime()

  def createCountData(self):
    return CountData(('count', 'totalcount', 'bonus',
                      'chance', 'chain', 'chancetime',
                      'isbonus', 'sbonus', 'spg', 'spb',
                      'pbr', 'voutput'))

  def detectBonus(self, t):
    for bi in self.BonusRound:
      if t < bi.limitsec:
        return bi

  def on(self, cbtype, iostatus, cd):
    ischance = bit_is_enable(iostatus, USBIO_BIT.CHANCE)

    if cbtype == USBIO_BIT.COUNT:
      cd['count'] += 1
      if not ischance:
        cd['totalcount'] += 1

      d = self.gcdelta.getDelta()
      cd['spg'] = d
      cd['voutput'] += (min(self.MaxSPC, d)
                         * self.LPS[int(ischance)])

    elif cbtype == USBIO_BIT.BONUS:
      self.bonustime.check()
      cd['bonus'] += 1
      cd['isbonus'] = 1
      if ischance:
        cd['chain'] += 1

    elif cbtype == USBIO_BIT.CHANCE:
      cd['chance'] += 1
    elif cbtype == USBIO_BIT.SBONUS:
      cd['sbonus'] += 1


  def off(self, cbtype, iostatus, cd):
    ischance = bit_is_enable(iostatus, USBIO_BIT.CHANCE)
    if cbtype == USBIO_BIT.BONUS:
      cd['isbonus'] = 0
      cd['count'] = 0
      if ischance:
        cd['chancetime'] = 1

      self.gcdelta.check()
      d = self.bonustime.getDelta()
      bi = self.detectBonus(d)
      cd['spb'] = d
      cd['pbr'] = bi.nround
      cd['voutput'] += bi.gainpts

    elif cbtype == USBIO_BIT.CHANCE:
      cd['chain'] = 0
      cd['chancetime'] = 0
      # cd['totalcount'] += cd['count']


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
        '3'  : { 'text': '{voutput:.0f}<small><small> PTS</small></small>'.format(**d)},
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
        '3' : { 'text': '{voutput:.0f}<small><small> PTS</small></small>'.format(**d)},
        '4' : { 'text': 'SPG:{spg:.2f} SPB:{spb:.2f} PBR:{pbr}r'.format(**d)},
      }
      if cd['isbonus'] == 1:
        dd['framesvg0'] = 'resource/orangeflame_wide.svg'
        self.bulk_set_color(dd, self.rgb2int(0xff, 0xff, 0x33))
        dd['0']['color'] = self.rgb2int(0, 0, 0)
      else:
        self.bulk_set_color(dd, self.rgb2int(0xff, 0xff, 0xff))
    return json.dumps(dd)
