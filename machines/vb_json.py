# coding: utf-8

try:
  import ujson as json
except ImportError:
  try:
    import simplejson as json
  except ImportError:
    import json

from pcounter.core import COUNT_INDEX, USBIO_BIT
from pcounter.counterplugin import ICounter
from pcounter.util import (decolate_number, gen_bonusrate, 
                           gen_bonusrate, gen_history,
                           gen_chain, bit_is_enable)

COUNT_INDEX_CHANCEGAMES = COUNT_INDEX.USER
COUNT_INDEX_NORMALGAMES = COUNT_INDEX.USER + 1

falldown_possibility = 1/338.5

def init():
  return ICounter("virusbreaker_json", to_on, to_off, output)


def to_on(cbittype, bitgroup, counts, history):
  if cbittype == USBIO_BIT.COUNT:
    counts[COUNT_INDEX.COUNT] += 1
    counts[COUNT_INDEX.TOTALCOUNT] += 1
    if bitgroup & (1 << USBIO_BIT.CHANCE):
      counts[COUNT_INDEX_CHANCEGAMES] += 1
    else:
      counts[COUNT_INDEX_NORMALGAMES] += 1

  if cbittype == USBIO_BIT.BONUS:
    counts[COUNT_INDEX.BONUS] += 1
    if bitgroup & (1 << USBIO_BIT.CHANCE):
      counts[COUNT_INDEX.CHAIN] += 1

  if cbittype == USBIO_BIT.CHANCE:
    counts[COUNT_INDEX.CHANCE] += 1
    history.append(('VAT', counts[COUNT_INDEX.COUNT]))

  if cbittype == USBIO_BIT.SBONUS:
    counts[COUNT_INDEX.SBONUS] += 1


def to_off(cbittype, bitgroup, counts, history):
  if cbittype == USBIO_BIT.BONUS:
    counts[COUNT_INDEX.COUNT] = 0
  if cbittype == USBIO_BIT.CHANCE:
    counts[COUNT_INDEX.COUNT] = 0
    counts[COUNT_INDEX.CHAIN] = 0
    counts[COUNT_INDEX_CHANCEGAMES] = 0


def output(counts, history):
  dt = {
     'nowgames':          counts[COUNT_INDEX.COUNT],
     'normalgame':        counts[COUNT_INDEX_NORMALGAMES],
     'chancegame':        counts[COUNT_INDEX_CHANCEGAMES],
     'bonus':             counts[COUNT_INDEX.BONUS],
     'firstbonus':        counts[COUNT_INDEX.CHANCE],
     'firstbonus_rate':   gen_bonusrate(counts[COUNT_INDEX_NORMALGAMES],
                                         counts[COUNT_INDEX.CHANCE]),
     'chain':             counts[COUNT_INDEX.CHAIN],
     'chain_rate':        gen_bonusrate(counts[COUNT_INDEX_CHANCEGAMES],
                                         counts[COUNT_INDEX.CHAIN]),
  }


  if counts[COUNT_INDEX.CHAIN] > 0:
    dt['vat'] = _ordering(counts[COUNT_INDEX.CHANCE])
    dd = {
      '8' : { 'text': '{nowgames} / {chancegame}'.format(**dt) },
      '9' : { 'text': dt['chain_rate'] },
      '10': { 'text': '{bonus} / {firstbonus}'.format(**dt) },
      '11': { 'text': '{vat} Virus Attack Time - {chain} Bonus combo'.format(**dt) },
    }
    _add_color(dd, _rgb(0xff, 0xff, 0))
  else:
    dd = {
      '8' : { 'text': '{nowgames} / {normalgame}'.format(**dt) },
      '9' : { 'text': dt['firstbonus_rate'] },
      '10': { 'text': '{bonus} / {firstbonus}'.format(**dt) },
      '11': { 'text': '' },
    }
    _add_color(dd, _rgb(0xff, 0xff, 0xff))
  return json.dumps(dd)


def _add_color(d, color):
  for k in d:
    d[k]['color'] = color

def _rgb(r, g, b, a=0xff):
  return (a << 24) + (r << 16) + (g << 8) + b 

def _ordering(n):
  less100 = n % 100
  less10 = less100 % 10
  if less10 in (1, 2, 3) and not (10 <= less100 < 20):
    t = '{0}{1}'.format(n, ('st', 'nd', 'rd')[less10 - 1])
  else:
    t = '{0}th'.format(n)
  return t

