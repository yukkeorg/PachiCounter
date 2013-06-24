# coding: utf-8
# vim: ts=2 sts=2 sw=2 et

from __future__ import print_function

import sys
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


COUNT_INDEX_STEALTH_CHANCETIME = COUNT_INDEX.USER


def init():
  return ICounter("stealth_json", switchon_handler,
                                  switchoff_handler,
                                  output_handler)


def switchon_handler(cbittype, iostatus, counts, history):
  if cbittype == USBIO_BIT.COUNT:
    counts[COUNT_INDEX.COUNT] += 1
    if not bit_is_enable(iostatus, USBIO_BIT.CHANCE):
      counts[COUNT_INDEX.TOTALCOUNT] += 1

  if cbittype == USBIO_BIT.BONUS:
    counts[COUNT_INDEX.BONUS] += 1
    counts[COUNT_INDEX_STEALTH_CHANCETIME] = 1
    if bit_is_enable(iostatus, USBIO_BIT.CHANCE):   # チャンス中なら
      counts[COUNT_INDEX.CHAIN] += 1

  if cbittype == USBIO_BIT.CHANCE:
    counts[COUNT_INDEX.CHANCE] += 1
    history.append((None, counts[COUNT_INDEX.COUNT]))

  if cbittype == USBIO_BIT.SBONUS:
    counts[COUNT_INDEX.SBONUS] += 1


def switchoff_handler(cbittype, iostatus, counts, history):
  if cbittype == USBIO_BIT.BONUS:
    counts[COUNT_INDEX.COUNT] = 0
  if cbittype == USBIO_BIT.CHANCE:
    counts[COUNT_INDEX.CHAIN] = 0
    counts[COUNT_INDEX_STEALTH_CHANCETIME] = 0


def output_handler(counts, history):
  dd = {
    'nowcount'   : counts[COUNT_INDEX.COUNT],
    'totalcount' : counts[COUNT_INDEX.TOTALCOUNT],
    'bonus'      : counts[COUNT_INDEX.BONUS],
    'firstbonus' : counts[COUNT_INDEX.CHANCE],
    'bonusrate'  : gen_bonusrate(counts[COUNT_INDEX.TOTALCOUNT],
                             counts[COUNT_INDEX.CHANCE]),
    'chain'      : "{0} Bonus".format(_ordering(counts[COUNT_INDEX.CHAIN]))
  }

  if counts[COUNT_INDEX_STEALTH_CHANCETIME] == 1:
    color = _rgb(0xff, 0xff, 0x33)
    d = {
      '8'  : { 'text': '{nowcount} OF 99'.format(**dd), 'color': color },
      '9'  : { 'text': '{bonusrate}'.format(**dd), 'color': color},
      '10' : { 'text': '{bonus} / {firstbonus}'.format(**dd), 'color': color },
      '11' : { 'text': 'STEALTH RUSH - {chain}'.format(**dd), 'color': color }
    }
  else:
    color = _rgb(0xff, 0xff, 0xff)
    d = {
      '8'  : { 'text': '{nowcount} / {totalcount}'.format(**dd), 'color': color },
      '9'  : { 'text': '{bonusrate}'.format(**dd), 'color': color},
      '10' : { 'text': '{bonus} / {firstbonus}'.format(**dd), 'color': color },
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
  
