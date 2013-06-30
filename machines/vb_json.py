# coding: utf-8
# vim: ts=2 sts=2 sw=2 et

from pcounter.core import json, CountData, USBIO_BIT
from pcounter.plugin import ICounter, UtilsMixin
from pcounter.util import (gen_bonusrate, bit_is_enable)

falldown_possibility = 1/338.5

class vb_json(ICounter, UtilsMixin):
  def createCountData(self):
    return CountData(('count', 'totalcount', 'chancegames', 
                      'normalgames', 'bonus', 'chain', 'chance'))

  def on(self, cbittype, bitgroup, cd):
    if cbittype == USBIO_BIT.COUNT:
      cd['count'] += 1
      cd['totalcount'] += 1
      if bit_is_enable(bitgroup, USBIO_BIT.CHANCE):
        cd['chancegames'] += 1
      else:
        cd['normalgames'] += 1
    elif cbittype == USBIO_BIT.BONUS:
      cd['bonus'] += 1
      if bit_is_enable(bitgroup, USBIO_BIT.CHANCE):
        cd['chain'] += 1
    elif cbittype == USBIO_BIT.CHANCE:
      cd['chance'] += 1

  def off(self, cbittype, bitgroup, cd):
    if cbittype == USBIO_BIT.BONUS:
      cd['count'] = 0
    if cbittype == USBIO_BIT.CHANCE:
      cd['count'] = 0
      cd['chain'] = 0
      cd['chancegames'] = 0

  def build(self, cd):
    if cd['chain'] > 0:
      color = self.rgb2int(0xff, 0xff, 0x33)
      bonus_rate = gen_bonusrate(cd['chancegames'], cd['chain'])
      vat = self.ordering(cd['chance'])
      # continue_possibilty = ((1.0 - falldown_possibility)
      #                            ** cd['chancegames']) * 100
      dd = {
        'framesvg' : 'resource/orangeflame_wide.svg', 
        '8'  : {'text': '{count} / {chancegames}'.format(**cd.counts) },
        '9'  : {'text': bonus_rate },
        '10' : {'text': '{bonus} / {chance}'.format(**cd.counts) },
        '11' : {'text': '{0} VAT - {chain} Bonus(s)'.format(vat, **cd.counts) }
      }
      self.bulk_set_color(dd, color)
      dd['8']['color'] = self.rgb2int(0, 0, 0)
    else:
      color = self.rgb2int(0xff, 0xff, 0xff)
      bonus_rate = gen_bonusrate(cd['normalgames'], cd['chance'])
      dd = {
        'framesvg' : 'resource/blueflame_wide.svg', 
        '8'  : {'text': '{count} / {normalgames}'.format(**cd.counts) },
        '9'  : {'text': bonus_rate },
        '10' : {'text': '{bonus} / {chance}'.format(**cd.counts) },
        '11' : {'text': '' }
      }
      self.bulk_set_color(dd, color)
    return json.dumps(dd)


