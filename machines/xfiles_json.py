# coding: utf-8
# vim: ts=2 sts=2 sw=2 et

from pcounter.core import json, CountData, USBIO_BIT
from pcounter.plugin import ICounter, UtilsMixin
from pcounter.util import (gen_bonusrate, bit_is_enable)

class xfiles_json(ICounter, UtilsMixin):
  def createCountData(self):
    return CountData(('count', 'totalcount', 'chancegames', 
                      'normalgames', 'bonus', 'sbonus', 
                      'xr', 'chain', 'chance'))

  def on(self, cbittype, bitgroup, cd):
    if cbittype == USBIO_BIT.COUNT:
      cd['count'] += 1
      cd['totalcount'] += 1
      if bit_is_enable(bitgroup, USBIO_BIT.CHANCE):
        cd['chancegames'] += 1
      else:
        cd['normalgames'] += 1
    if cbittype == USBIO_BIT.BONUS:
      cd['bonus'] += 1
      if bit_is_enable(bitgroup, USBIO_BIT.CHANCE):
        cd['chain'] += 1
        if cd['chain'] == 1:
          pass
        elif cd['chain'] == 2:
          cd['xr'] += 1
          history.append(('XR', cd['count']))
    if cbittype == USBIO_BIT.CHANCE:
      cd['chance'] += 1
    if cbittype == USBIO_BIT.SBONUS:
      cd['sbonus'] += 1

  def off(self, cbittype, bitgroup, cd):
    if cbittype == USBIO_BIT.BONUS:
      cd['count'] = 0
    if cbittype == USBIO_BIT.CHANCE:
      cd['chain'] = 0

  def build(self, cd):
    dd = {
        '9'  : {'text': gen_bonusrate(cd['totalcount'], cd['sbonus'])},
        '10' : {'text': '{sbonus} / {chance} / {xr}'.format(**cd.counts)},
    }
    color = self.rgb2int(0xff, 0xff, 0xff)

    if cd['chain'] == 0:
      dd.update({ 
        '8'  : {'text': '{count} / {totalcount}'.format(**cd.counts)},
        '11' : {'text': ''},
      })
    elif cd['chain'] == 1:
      color = self.rgb2int(0x10, 0xff, 0x10)
      dd.update({
        '8'  : {'text': '{count} <small>OF</small> 5'.format(**cd.counts)},
        '11' : {'text': 'UFO-ZONE'},
      })
    else:
      color = self.rgb2int(0xff, 0xff, 0x10)
      dd.update({
        '8'  : {'text': '{count} <small>OF</small> 80'.format(**cd.counts)},
        '11' : {'text': 'XTRA-RUSH - {chain} Bonus Chain'.format(**cd.counts)},
      })
    self.bulk_set_color(dd, color)

    return json.dumps(dd)

