# coding: utf-8

# pachicounter interface for CR Virus Breaker.
# Version : 0.10 (2012/08/04)
# Auther  : Yukke.org <pcounter@yukke.org>

from pcounter.core import COUNT_INDEX, USBIO_BIT
from pcounter.counterplugin import ICounter
from pcounter.util import (decolate_number, gen_bonusrate, 
                           gen_bonusrate, gen_history,
                           gen_chain, bit_is_enable)

COUNT_INDEX_CHANCEGAMES = COUNT_INDEX.USER
COUNT_INDEX_NORMALGAMES = COUNT_INDEX.USER + 1

falldown_possibility = 1/338.5

def init():
  return ICounter("virusbreaker", to_on, to_off, output)


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
  data_table = {
     'nowgames':          decolate_number(counts[COUNT_INDEX.COUNT], 3),
     'normalgametotal':   decolate_number(counts[COUNT_INDEX_NORMALGAMES], 4),
     'chancegame':        decolate_number(counts[COUNT_INDEX_CHANCEGAMES], 4),
     'totalgames':        decolate_number(counts[COUNT_INDEX.TOTALCOUNT], 4),
     'bonus':             decolate_number(counts[COUNT_INDEX.BONUS], 3),
     'firstbonus':        decolate_number(counts[COUNT_INDEX.CHANCE], 2),
     'firstbonus_rate':   gen_bonusrate(counts[COUNT_INDEX_NORMALGAMES],
                                         counts[COUNT_INDEX.CHANCE]),
     'chain':             decolate_number(counts[COUNT_INDEX.CHAIN], 3),
     'history':           gen_history(history, 3, sep="\n", isfill=True),
  }


  if counts[COUNT_INDEX.CHAIN] > 0:
    less100 = counts[COUNT_INDEX.CHANCE] % 100
    less10 = less100 % 10
    if less10 in (1, 2, 3) and not (10 <= less100 < 20):
      t = '{0}{1}'.format(counts[COUNT_INDEX.CHANCE], ('st', 'nd', 'rd')[less10 - 1])
    else:
      t = '{0}th'.format(counts[COUNT_INDEX.CHANCE])

    continue_possibilty = ((1.0 - falldown_possibility)
                               ** counts[COUNT_INDEX_CHANCEGAMES]) * 100
    data_table.update({
       'continuepossibility' : '{0:.2f}%'.format(continue_possibilty),
       'vat'                 : t,
    })

    fmt = ('<span color="#ffff00">'
           '<span size="large"><u>{vat} VAT</u></span>\n'
           '<span size="small">Start</span>\n'
           '<span size="x-large">{nowgames}</span>/{chancegame}\n'
           '<span size="small">Chain</span>\n'
           '<span size="large">{chain}</span>\n'
           '<span size="small">Continue Possibility : {continuepossibility}</span>'
           '</span>')

  else:
    fmt = ('<span size="small"><u>Start</u></span>\n'
           '<span size="x-large">{nowgames}</span>/{normalgametotal}\n'
           '<span size="small"><u>Bonus</u></span>\n'
           '<span size="large">{bonus}</span>/{firstbonus} {firstbonus_rate}')

  return fmt.format(**data_table)

