# coding: utf-8

from pcounter import pcounter, util

COUNT_INDEX_XFILES_XR = pcounter.COUNT_INDEX.USER
COUNT_INDEX_XFILES_NORMALGAMES = pcounter.COUNT_INDEX.USER + 1
COUNT_INDEX_XFILES_CHANCEGAMES = pcounter.COUNT_INDEX.USER + 2


def init():
  return pcounter.ICounter("xfiles", to_on, to_off, output)

  
def to_on(cbittype, bitgroup, counts, history):
  if cbittype == pcounter.USBIO_BIT.COUNT:
    counts[pcounter.COUNT_INDEX.COUNT] += 1
    counts[pcounter.COUNT_INDEX.TOTALCOUNT] += 1
    if bitgroup & (1 << pcounter.USBIO_BIT.CHANCE):
      counts[COUNT_INDEX_XFILES_CHANCEGAMES] += 1
    else:
      counts[COUNT_INDEX_XFILES_NORMALGAMES] += 1
  if cbittype == pcounter.USBIO_BIT.BONUS:
    counts[pcounter.COUNT_INDEX.BONUS] += 1
    if bitgroup & (1 << pcounter.USBIO_BIT.CHANCE):
      counts[pcounter.COUNT_INDEX.CHAIN] += 1
      if counts[pcounter.COUNT_INDEX.CHAIN] == 1:
        history.append(('UZ', counts[pcounter.COUNT_INDEX.COUNT]))
      elif counts[pcounter.COUNT_INDEX.CHAIN] == 2:
        counts[COUNT_INDEX_XFILES_XR] += 1
        history.append(('XR', counts[pcounter.COUNT_INDEX.COUNT]))
  if cbittype == pcounter.USBIO_BIT.CHANCE:
    counts[pcounter.COUNT_INDEX.CHANCE] += 1
  if cbittype == pcounter.USBIO_BIT.SBONUS:
    counts[pcounter.COUNT_INDEX.SBONUS] += 1

def to_off(cbittype, bitgroup, counts, history):
  if cbittype == pcounter.USBIO_BIT.BONUS:
    counts[pcounter.COUNT_INDEX.COUNT] = 0
  if cbittype == pcounter.USBIO_BIT.CHANCE:
    counts[pcounter.COUNT_INDEX.CHAIN] = 0
  
def output(counts, history):
  data_table = {
     'count':       util.decolate_number(counts[pcounter.COUNT_INDEX.COUNT], 4), 
     'totalcount':  util.decolate_number(counts[pcounter.COUNT_INDEX.TOTALCOUNT], 5), 
     'bonuscount':  util.decolate_number(counts[pcounter.COUNT_INDEX.SBONUS], 3),
     'uzcount':     util.decolate_number(counts[pcounter.COUNT_INDEX.CHANCE], 3), 
     'reserved':    util.decolate_number(counts[pcounter.COUNT_INDEX.BONUS], 3),
     'xrcount':     util.decolate_number(counts[COUNT_INDEX_XFILES_XR], 3),
     'normalcount': util.decolate_number(counts[COUNT_INDEX_XFILES_NORMALGAMES], 4),
     'uzxrcount':   util.decolate_number(counts[COUNT_INDEX_XFILES_CHANCEGAMES], 4),
     'xr_rate':     util.gen_bonusrate(counts[COUNT_INDEX_XFILES_NORMALGAMES], 
                                       counts[COUNT_INDEX_XFILES_XR]), 
     'uz_rate':     util.gen_bonusrate(counts[COUNT_INDEX_XFILES_NORMALGAMES], 
                                       counts[pcounter.COUNT_INDEX.CHANCE]), 
     'bonus_rate':  util.gen_bonusrate(counts[pcounter.COUNT_INDEX.TOTALCOUNT], 
                                       counts[pcounter.COUNT_INDEX.SBONUS]),
     'xr_chain':    util.gen_chain(counts[pcounter.COUNT_INDEX.CHAIN] - 1),
     'history':     util.gen_history(history, 3, sep="\n", isfill=True),
  }

  fmt = ('<span font-desc="Ricty Bold 14">' 
         '<span size="small"><u>Now</u></span>\n' 
         '<span size="x-large">{count}</span>\n')
  if counts[pcounter.COUNT_INDEX.CHAIN] > 1:
    add_fmt = '<span size="small"><u>XTRA-RUSH</u></span>{xr_chain}'
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
  fmt = fmt + add_fmt + '</span>'

  return fmt.format(**data_table)
  
