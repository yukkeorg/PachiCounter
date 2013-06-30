# coding: utf-8
# vim: ts=2 sts=2 sw=2 et

from pcounter.core import USBIO_BIT, CountData, json
from pcounter.plugin import ICounter, UtilsMixin
from pcounter.util import gen_bonusrate, bit_is_enable

class stealth_json(ICounter, UtilsMixin):
  def createCountData(self):
    return CountData(('count', 'totalcount', 'bonus', 
                    'chance', 'chain', 'chancetime', 'isbonus',
                    'sbonus'))

  def on(self, cbtype, iostatus, cd):
    if cbtype == USBIO_BIT.COUNT:
      cd['count'] += 1
      if not bit_is_enable(iostatus, USBIO_BIT.CHANCE):
        cd['totalcount'] += 1
    elif cbtype == USBIO_BIT.BONUS:
      cd['bonus'] += 1
      cd['isbonus'] = 1
      if bit_is_enable(iostatus, USBIO_BIT.CHANCE):   # チャンス中
        cd['chain'] += 1
    elif cbtype == USBIO_BIT.CHANCE:
      cd['chance'] += 1
    elif cbtype == USBIO_BIT.SBONUS:
      cd['sbonus'] += 1


  def off(self, cbtype, iostatus, cd):
    if cbtype == USBIO_BIT.BONUS:
      cd['isbonus'] = 0
      cd['count'] = 0
      if bit_is_enable(iostatus, USBIO_BIT.CHANCE):   # チャンス中
        cd['chancetime'] = 1
    elif cbtype == USBIO_BIT.CHANCE:
      cd['count'] = 0
      cd['chain'] = 0
      cd['chancetime'] = 0


  def build(self, cd):
    d = cd.counts
    bonusrate = gen_bonusrate(d['totalcount'], d['chance'])
    if cd['chancetime'] == 1: 
      chainstr = "STEALTH RUSH - {0} Bonus".format(_ordering(d['chain']))
      color = self.rgb2int(0xff, 0xff, 0x33)
      dd = {
        '8'  : { 'text': '{count} <small>OF</small> 99'.format(**d)},
        '9'  : { 'text': bonusrate,},
        '10' : { 'text': '{bonus} / {chance}'.format(**d)},
        '11' : { 'text': chainstr}
      }
    else:
      if cd['isbonus'] == 1:
        color = self.rgb2int(0xff, 0xff, 0x33)
      else:
        color = self.rgb2int(0xff, 0xff, 0xff)
      dd = {
        '8'  : { 'text': '{count} / {totalcount}'.format(**d) },
        '9'  : { 'text': bonusrate },
        '10' : { 'text': '{bonus} / {chance}'.format(**d) },
        '11' : { 'text': ' ' }
      }
    self.bulk_set_color(dd, color)
    return json.dumps(dd)

