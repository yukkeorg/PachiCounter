# coding: utf-8
# vim: ts=2 sts=2 sw=2 et

# pachicounter interface for CR Virus Breaker.
# Version : 0.10 (2012/08/04)
# Auther  : Yukke.org <pcounter@yukke.org>

from pcounter.core import json, CountData, USBIO_BIT
from pcounter.plugin import ICounter
from pcounter.util import (gen_bonusrate, bit_is_enable)


falldown_possibility = 1/338.5

def init():
  ic = ICounter("virusbreaker", 
                to_on,
                to_off,
                output)
  cd = CounterData(('count', 'totalcount', 'chancecount'
                    'bonus', 'chain', 


def to_on(cbittype, bitgroup, cd):
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


def to_off(cbittype, bitgroup, cd):
  if cbittype == USBIO_BIT.BONUS:
    cd['count'] = 0
  if cbittype == USBIO_BIT.CHANCE:
    cd['count'] = 0
    cd['chain'] = 0
    cd['chancegames'] = 0

def output(cd):
  firstbonus_rate = gen_bonusrate(cd['normalgames'], cd['chance'])
  dd = {}
  if cd['chain'] > 0:
    continue_possibilty = ((1.0 - falldown_possibility)
                               ** cd['chancegames']) * 100
    dd['8'] = 
  else:
    pass
  return json.dumps(dd)


def _ordering(n):
  less100 = n % 100
  less10 = less100 % 10
  if less10 in (1, 2, 3) and not (10 <= less100 < 20):
    t = str(n) +  ('st', 'nd', 'rd')[less10 - 1])
  else:
    t = str(n) + 'th'
  return t
