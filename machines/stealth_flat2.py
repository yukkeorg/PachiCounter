# coding: utf-8

from __future__ import print_function

import sys
from stealth import *

def init():
  return ICounter("stealth_flat", switchon_handler,
                                  switchoff_handler,
                                  output_handler)

def output_handler(counts, history):
  rem10 = counts[COUNT_INDEX.CHAIN] % 10
  rem100 = counts[COUNT_INDEX.CHAIN] % 100
  if rem10 in (1, 2, 3) and not (10 <= rem100 < 20):
    post = ('st', 'nd', 'rd')[rem10 - 1]
  else:
    post = 'th'
  chainstr = "{0}{1} Bonus".format(counts[COUNT_INDEX.CHAIN], post)

  display_data = {
    'nowcount'   : counts[COUNT_INDEX.COUNT],
    'totalcount' : counts[COUNT_INDEX.TOTALCOUNT],
    'bonus'      : counts[COUNT_INDEX.BONUS],
    'chain'      : chainstr,
  }

  print("{0}".format(counts[COUNT_INDEX.BONUS]), file=sys.stderr)

  if counts[COUNT_INDEX_STEALTH_CHANCETIME] == 1:
    counter_fmt = '<span color="#ffff33">{chain}</span>'
  else:
    counter_fmt = '{nowcount} / {totalcount}'

  return counter_fmt.format(**display_data)

