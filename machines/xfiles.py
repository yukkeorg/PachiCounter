# coding: utf-8

from pcounter.core import COUNT_INDEX, USBIO_BIT
from pcounter.counterplugin import ICounter
from pcounter.util import (decolate_number, gen_bonusrate, 
                           gen_bonusrate, gen_history,
                           gen_chain, bit_is_enable)

COUNT_INDEX_XFILES_XR = COUNT_INDEX.USER
COUNT_INDEX_XFILES_NORMALGAMES = COUNT_INDEX.USER + 1
COUNT_INDEX_XFILES_CHANCEGAMES = COUNT_INDEX.USER + 2


def init():
  return ICounter("xfiles", to_on, to_off, output)


def to_on(cbittype, bitgroup, counts, history):
  if cbittype == USBIO_BIT.COUNT:
    counts[COUNT_INDEX.COUNT] += 1
    counts[COUNT_INDEX.TOTALCOUNT] += 1
    if bitgroup & (1 << USBIO_BIT.CHANCE):
      counts[COUNT_INDEX_XFILES_CHANCEGAMES] += 1
    else:
      counts[COUNT_INDEX_XFILES_NORMALGAMES] += 1
  if cbittype == USBIO_BIT.BONUS:
    counts[COUNT_INDEX.BONUS] += 1
    if bitgroup & (1 << USBIO_BIT.CHANCE):
      counts[COUNT_INDEX.CHAIN] += 1
      if counts[COUNT_INDEX.CHAIN] == 1:
        history.append(('UZ', counts[COUNT_INDEX.COUNT]))
      elif counts[COUNT_INDEX.CHAIN] == 2:
        counts[COUNT_INDEX_XFILES_XR] += 1
        history.append(('XR', counts[COUNT_INDEX.COUNT]))
  if cbittype == USBIO_BIT.CHANCE:
    counts[COUNT_INDEX.CHANCE] += 1
  if cbittype == USBIO_BIT.SBONUS:
    counts[COUNT_INDEX.SBONUS] += 1

def to_off(cbittype, bitgroup, counts, history):
  if cbittype == USBIO_BIT.BONUS:
    counts[COUNT_INDEX.COUNT] = 0
  if cbittype == USBIO_BIT.CHANCE:
    counts[COUNT_INDEX.CHAIN] = 0

def output(counts, history):
  data_table = {
     'count':       decolate_number(counts[COUNT_INDEX.COUNT], 3),
     'totalcount':  decolate_number(counts[COUNT_INDEX.TOTALCOUNT], 4),
     'bonuscount':  decolate_number(counts[COUNT_INDEX.SBONUS], 3),
     'uzcount':     decolate_number(counts[COUNT_INDEX.CHANCE], 2),
     'reserved':    decolate_number(counts[COUNT_INDEX.BONUS], 3),
     'xrcount':     decolate_number(counts[COUNT_INDEX_XFILES_XR], 2),
     'normalcount': counts[COUNT_INDEX_XFILES_NORMALGAMES],
     'uzxrcount':   counts[COUNT_INDEX_XFILES_CHANCEGAMES],
     'xr_rate':     gen_bonusrate(counts[COUNT_INDEX_XFILES_NORMALGAMES],
                                       counts[COUNT_INDEX_XFILES_XR]),
     'uz_rate':     gen_bonusrate(counts[COUNT_INDEX_XFILES_NORMALGAMES],
                                       counts[COUNT_INDEX.CHANCE]),
     'bonus_rate':  gen_bonusrate(counts[COUNT_INDEX.TOTALCOUNT],
                                       counts[COUNT_INDEX.SBONUS]),
     'xr_chain':    gen_chain(counts[COUNT_INDEX.CHAIN] - 1),
     'history':     gen_history(history, 3, sep="\n", isfill=True),
  }

  fmt = ('<span size="small"><u>Start</u></span>\n'
         '<span size="x-large">{count}</span>\n')
  if counts[COUNT_INDEX.CHAIN] > 1:
    add_fmt = ('<span size="small"><u>XTRA-RUSH</u></span>{xr_chain}\n'
               '<span size="small"><u>TotalBonus</u>\n{totalcount}({bonus_rate})</span>\n')

  else:
    add_fmt = ('<span size="small"><u>Total</u></span>\n'
               '<span size="large">{totalcount}</span>\n'
               '<span size="small">{normalcount}+{uzxrcount}</span>\n'
               '<span size="small"><u>Bonus</u></span>\n'
               '<span size="large">{bonuscount}</span><span size="small">({bonus_rate})</span>\n'
               'UZ:<span size="large">{uzcount}</span><span size="small">({uz_rate})</span>\n'
               'XR:<span size="large">{xrcount}</span><span size="small">({xr_rate})</span>\n'
               '<span size="small"><u>History</u></span>\n'
               '{history}')
  fmt = fmt + add_fmt

  return fmt.format(**data_table)

