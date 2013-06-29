# coding: utf-8
# vim: ts=2 sts=2 sw=2 et

from pcounter.core import USBIO_BIT, CountData, json
from pcounter.plugin import ICounter
from pcounter.util import gen_bonusrate, bit_is_enable

def init():
  ic = ICounter(switchon_handler,
                switchoff_handler,
                output_handler)
  cd = CountData(('count', 'totalcount', 'bonus', 
                  'chance', 'chain', 'chancetime', 'isbonus',
                  'sbonus'))
  return (ic, cd)


def switchon_handler(cbtype, iostatus, cd):
  if cbtype == USBIO_BIT.COUNT:
    cd['count'] += 1
    if not bit_is_enable(iostatus, USBIO_BIT.CHANCE):
      cd['totalcount'] += 1
  elif cbtype == USBIO_BIT.BONUS:
    cd['bonus'] += 1
    cd['isbonus'] = 1
    if bit_is_enable(iostatus, USBIO_BIT.CHANCE):   # チャンス中なら
      cd['chain'] += 1
  elif cbtype == USBIO_BIT.CHANCE:
    cd['chance'] += 1
    #history.append((None, cd.counts[COUNT_INDEX.COUNT]))
  elif cbtype == USBIO_BIT.SBONUS:
    cd['sbonus'] += 1


def switchoff_handler(cbtype, iostatus, cd):
  if cbtype == USBIO_BIT.BONUS:
    cd['isbonus'] = 0
    cd['count'] = 0
    if bit_is_enable(iostatus, USBIO_BIT.CHANCE):   # チャンス中なら
      cd['chancetime'] = 1
  elif cbtype == USBIO_BIT.CHANCE:
    cd['count'] = 0
    cd['chain'] = 0
    cd['chancetime'] = 0


def output_handler(cd):
  d = cd.counts
  bonusrate = gen_bonusrate(d['totalcount'], d['chance'])
  if cd['chancetime'] == 1: 
    chainstr = "STEALTH RUSH - {0} Bonus".format(_ordering(d['chain']))
    color = _rgb(0xff, 0xff, 0x33)
    dd = {
      '8'  : { 'text': '{count} <small>OF</small> 99'.format(**d)},
      '9'  : { 'text': bonusrate,},
      '10' : { 'text': '{bonus} / {chance}'.format(**d)},
      '11' : { 'text': chainstr}
    }
  else:
    if cd['isbonus'] == 1:
      color = _rgb(0xff, 0xff, 0x33)
    else:
      color = _rgb(0xff, 0xff, 0xff)
    dd = {
      '8'  : { 'text': '{count} / {totalcount}'.format(**d) },
      '9'  : { 'text': bonusrate },
      '10' : { 'text': '{bonus} / {chance}'.format(**d) },
      '11' : { 'text': ' ' }
    }
  _bulk_set_color(dd, color)
  return json.dumps(dd)


def _bulk_set_color(d, color):
  for k in d:
    d[k]['color'] = color

def _rgb(r, g, b, a=0xff):
    return (a << 24) + (r << 16) + (g << 8) + b

def _ordering(n):
  rem10 = n % 10
  rem100 = n % 100
  if rem10 in (1, 2, 3) and not (10 <= rem100 < 20):
    post = ('st', 'nd', 'rd')[rem10 - 1]
  else:
    post = 'th'
  return str(n)+post
  
