# coding: utf-8

# pachicounter interface for CR Virus Breaker.
# Version : 0.10 (2012/08/04)
# Auther  : Yukke.org <pcounter@yukke.org>

from vb import *

def init():
  return ICounter("virusbreaker_flat", to_on, to_off, output)

def output(counts, history):
  data_table = {
     'nowgames':          decolate_number(counts[COUNT_INDEX.COUNT], 3),
     'normalgametotal':   decolate_number(counts[COUNT_INDEX_NORMALGAMES], 4),
     'chancegame':        decolate_number(counts[COUNT_INDEX_CHANCEGAMES], 4),
     'bonus':             decolate_number(counts[COUNT_INDEX.BONUS], 3),
     'firstbonus':        decolate_number(counts[COUNT_INDEX.CHANCE], 2),
     'firstbonus_rate':   gen_bonusrate(counts[COUNT_INDEX_NORMALGAMES],
                                         counts[COUNT_INDEX.CHANCE]),
     'chain':             decolate_number(counts[COUNT_INDEX.CHAIN], 3),
     'chain_rate':        gen_bonusrate(counts[COUNT_INDEX_CHANCEGAMES],
                                         counts[COUNT_INDEX.CHAIN]),
  }


  if counts[COUNT_INDEX.CHAIN] > 0:
    less100 = counts[COUNT_INDEX.CHANCE] % 100
    less10 = less100 % 10
    if less10 in (1, 2, 3) and not (10 <= less100 < 20):
      t = '{0}{1}'.format(counts[COUNT_INDEX.CHANCE], ('st', 'nd', 'rd')[less10 - 1])
    else:
      t = '{0}th'.format(counts[COUNT_INDEX.CHANCE])

    # continue_possibilty = ((1.0 - falldown_possibility)
    #                            ** counts[COUNT_INDEX_CHANCEGAMES]) * 100
    data_table.update({
        #   'continuepossibility' : '{0:3.1f}%'.format(continue_possibilty),
       'vat'                 : t,
    })

    fmt = '<span color="#ffff00">{vat}VAT | {nowgames} / {chancegame} | {chain} <small>({chain_rate})</small></span>'

  else:
   fmt = '{nowgames} / {normalgametotal} | {bonus} / {firstbonus} <small>({firstbonus_rate})</small>'

  return fmt.format(**data_table)

