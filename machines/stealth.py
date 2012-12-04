# coding: utf-8

from pcounter.core import COUNT_INDEX, USBIO_BIT
from pcounter.counterplugin import ICounter
from pcounter.util import (decolate_number, gen_bonusrate, 
                           gen_bonusrate, gen_history,
                           gen_chain, bit_is_enable)


COUNT_INDEX_STEALTH_CHANCETIME = COUNT_INDEX.USER


def init():
  return ICounter("stealth", switchon_handler,
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
  display_data = {
    'nowcount'   : decolate_number(counts[COUNT_INDEX.COUNT], 3),
    'totalcount' : decolate_number(counts[COUNT_INDEX.TOTALCOUNT], 4),
    'bonus'      : decolate_number(counts[COUNT_INDEX.BONUS], 2),
    'firstbonus' : decolate_number(counts[COUNT_INDEX.CHANCE], 2),
    'bonusrate'  : gen_bonusrate(counts[COUNT_INDEX.TOTALCOUNT],
                             counts[COUNT_INDEX.CHANCE]),
    'chain'      : gen_chain(counts[COUNT_INDEX.CHAIN], "Chain"),
    'history'    : gen_history(history, 3, sep='  ', isfill=True),
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

