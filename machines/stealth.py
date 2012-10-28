# coding: utf-8

from pcounter import pcounter, util

COUNT_INDEX_STEALTH_CHANCETIME = pcounter.COUNT_INDEX.USER

def init():
  return pcounter.ICounter("stealth", switchon_handler,
                                      switchoff_handler,
                                      output_handler)

def switchon_handler(cbittype, iostatus, counts, history):
  if cbittype == pcounter.USBIO_BIT.COUNT:
    counts[pcounter.COUNT_INDEX.COUNT] += 1
    if not util.bit_is_enable(iostatus, pcounter.USBIO_BIT.CHANCE):
      counts[pcounter.COUNT_INDEX.TOTALCOUNT] += 1

  if cbittype == pcounter.USBIO_BIT.BONUS:
    counts[pcounter.COUNT_INDEX.BONUS] += 1
    counts[COUNT_INDEX_STEALTH_CHANCETIME] = 1
    if util.bit_is_enable(iostatus, pcounter.USBIO_BIT.CHANCE):   # チャンス中なら
      counts[pcounter.COUNT_INDEX.CHAIN] += 1

  if cbittype == pcounter.USBIO_BIT.CHANCE:
    counts[pcounter.COUNT_INDEX.CHANCE] += 1
    history.append((None, counts[pcounter.COUNT_INDEX.COUNT]))

  if cbittype == pcounter.USBIO_BIT.SBONUS:
    counts[pcounter.COUNT_INDEX.SBONUS] += 1


def switchoff_handler(cbittype, iostatus, counts, history):
  if cbittype == pcounter.USBIO_BIT.BONUS:
    counts[pcounter.COUNT_INDEX.COUNT] = 0
  if cbittype == pcounter.USBIO_BIT.CHANCE:
    counts[pcounter.COUNT_INDEX.CHAIN] = 0
    counts[COUNT_INDEX_STEALTH_CHANCETIME] = 0


def output_handler(counts, history):
  display_data = {
    'nowcount'   : util.decolate_number(counts[pcounter.COUNT_INDEX.COUNT], 3),
    'totalcount' : util.decolate_number(counts[pcounter.COUNT_INDEX.TOTALCOUNT], 4),
    'bonus'      : util.decolate_number(counts[pcounter.COUNT_INDEX.BONUS], 2),
    'firstbonus' : util.decolate_number(counts[pcounter.COUNT_INDEX.CHANCE], 2),
    'bonusrate'  : util.gen_bonusrate(counts[pcounter.COUNT_INDEX.TOTALCOUNT],
                                  counts[pcounter.COUNT_INDEX.CHANCE]),
    'chain'      : util.gen_chain(counts[pcounter.COUNT_INDEX.CHAIN], "Chain"),
    'history'    : util.gen_history(history, 3, sep='  ', isfill=True),
  }

  gamecount_fmt = (
      '<u>START</u>\n'
      '<span size="x-large">{nowcount}</span>/{totalcount}\n'
      '<u>BONUS</u>\n'
      '<span size="large">{bonus}</span>/{firstbonus}({bonusrate})'
      '{chain}'
  )
  if counts[COUNT_INDEX_STEALTH_CHANCETIME] == 1:
    gamecount_fmt = '<span color="#ffff33">' + gamecount_fmt + '</span>'

  return gamecount_fmt.format(**display_data)

