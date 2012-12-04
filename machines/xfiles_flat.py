# coding: utf-8

from xfiles import *

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
        pass
      elif counts[COUNT_INDEX.CHAIN] == 2:
        counts[COUNT_INDEX_XFILES_XR] += 1
  if cbittype == USBIO_BIT.CHANCE:
    counts[COUNT_INDEX.CHANCE] += 1
  if cbittype == USBIO_BIT.SBONUS:
    counts[COUNT_INDEX.SBONUS] += 1

def to_off(cbittype, bitgroup, counts, history):
  if cbittype == USBIO_BIT.BONUS:
    counts[COUNT_INDEX.COUNT] = 0
  if cbittype == USBIO_BIT.CHANCE:
    counts[COUNT_INDEX.CHAIN] = 0
    counts[COUNT_INDEX_XFILES_CHANCEGAMES] = 0

def output(counts, history):
  data_table = {
     'count':       decolate_number(counts[COUNT_INDEX.COUNT], 3),
     'totalcount':  decolate_number(counts[COUNT_INDEX.TOTALCOUNT], 4),
     'bonuscount':  decolate_number(counts[COUNT_INDEX.SBONUS], 3),
     'uzcount':     decolate_number(counts[COUNT_INDEX.CHANCE], 2),
     'reserved':    decolate_number(counts[COUNT_INDEX.BONUS], 3),
     'xrcount':     decolate_number(counts[COUNT_INDEX_XFILES_XR], 2),
     'normalcount': decolate_number(counts[COUNT_INDEX_XFILES_NORMALGAMES], 4),
     'uzxrcount':   decolate_number(counts[COUNT_INDEX_XFILES_CHANCEGAMES], 4),
     'xr_chain':    decolate_number(counts[COUNT_INDEX.CHAIN] - 1, 3),
     'xr_rate':     gen_bonusrate(counts[COUNT_INDEX_XFILES_NORMALGAMES],
                                       counts[COUNT_INDEX_XFILES_XR]),
     'uz_rate':     gen_bonusrate(counts[COUNT_INDEX_XFILES_NORMALGAMES],
                                       counts[COUNT_INDEX.CHANCE]),
     'bonus_rate':  gen_bonusrate(counts[COUNT_INDEX.TOTALCOUNT],
                                       counts[COUNT_INDEX.SBONUS]),
  }


  if counts[COUNT_INDEX.CHAIN] == 0:
    fmt = ('{count}/{normalcount} | {bonuscount}/{uzcount}/{xrcount} | {uz_rate}')

  elif counts[COUNT_INDEX.CHAIN] == 1:
    fmt = ('<span color="green">'
           'UFO-ZONE | {count}/{normalcount} | {bonuscount}/{uzcount}/{xrcount} | {uz_rate}</span>')

  else:
    fmt = ('<span color="yellow">'
           'XTRA-RUSH | {count}/{uzxrcount} | {xr_chain}/{bonuscount} | {bonus_rate}</span>')

  return fmt.format(**data_table)

