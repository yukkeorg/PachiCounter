# coding: utf-8

from stealth import *

def init():
  return ICounter("stealth_flat", switchon_handler,
                                  switchoff_handler,
                                  output_handler)

def output_handler(counts, history):
  display_data = {
    'nowcount'   : decolate_number(counts[COUNT_INDEX.COUNT], 3),
    'totalcount' : decolate_number(counts[COUNT_INDEX.TOTALCOUNT], 4),
    'bonus'      : decolate_number(counts[COUNT_INDEX.BONUS], 2),
    'firstbonus' : decolate_number(counts[COUNT_INDEX.CHANCE], 2),
    'bonusrate'  : gen_bonusrate(counts[COUNT_INDEX.TOTALCOUNT],
                             counts[COUNT_INDEX.CHANCE]),
    'chain'      : decolate_number(counts[COUNT_INDEX.CHAIN], 2),
  }

  if counts[COUNT_INDEX_STEALTH_CHANCETIME] == 1:
    counter_fmt = ( '<span color="#ffff33">'
                    '{nowcount} / {totalcount} | {bonus} / {firstbonus} | {chain}'
                    '</span>' )
  else:
    counter_fmt = '{nowcount} / {totalcount} | {bonus} / {firstbonus} | {bonusrate}'

  return counter_fmt.format(**display_data)

