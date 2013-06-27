# coding: utf-8
# vim: ts=2 sts=2 sw=2 et

try:
  import ujson as json
except ImportError:
  try:
    import simplejson as json
  except ImportError:
    import json

from pcounter.core import USBIO_BIT, CountData
from pcounter.plugin import ICounter
from pcounter.util import gen_bonusrate, bit_is_enable

def init():
  ic = ICounter(switchon_handler,
                switchoff_handler,
                output_handler)
  cd = CountData(('count', 'totalcount', 'bonus', 
                  'chance', 'chain', 'chancetime',
                  'sbonus'))
  return ic, cd


def switchon_handler(cbtype, iostatus, cd):
  if cbtype == USBIO_BIT.COUNT:
    cd['count'] += 1
    if not bit_is_enable(iostatus, USBIO_BIT.CHANCE):
      cd['totalcount'] += 1

  if cbtype == USBIO_BIT.BONUS:
    cd['bonus'] += 1
    if bit_is_enable(iostatus, USBIO_BIT.CHANCE):   # チャンス中なら
      cd['chain'] += 1

  if cbtype == USBIO_BIT.CHANCE:
    cd['chance'] += 1
    #history.append((None, cd.counts[COUNT_INDEX.COUNT]))

  if cbtype == USBIO_BIT.SBONUS:
    cd['sbonus'] += 1


def switchoff_handler(cbtype, iostatus, cd):
  if cbtype == USBIO_BIT.BONUS:
    cd['count'] = 0
  if cbtype == USBIO_BIT.CHANCE:
    cd['chain'] = 0
    cd['chancetime'] = 0


def output_handler(cd):
  d = cd.counts
  bonusrate = gen_bonusrate(d['totalcount'], d['chance'])
  if d['chancetime'] == 1:
    chainstr = "STEALTH RUSH - {0} Bonus".format(_ordering(d['chain']))
    color = _rgb(0xff, 0xff, 0x33)
    d = {
      '8'  : { 'text': '{count} OF 99'.format(**d), 'color': color },
      '9'  : { 'text': bonusrate, 'color': color},
      '10' : { 'text': '{bonus} / {chance}'.format(**d), 'color': color },
      '11' : { 'text': chainstr, 'color': color }
    }
  else:
    color = _rgb(0xff, 0xff, 0xff)
    d = {
      '8'  : { 'text': '{count} / {totalcount}'.format(**d), 'color': color },
      '9'  : { 'text': bonusrate, 'color': color},
      '10' : { 'text': '{bonus} / {chain}'.format(**d), 'color': color },
      '11' : { 'text': ' ' }
    }

  return json.dumps(d)


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
  
