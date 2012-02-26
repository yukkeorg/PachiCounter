# coding: utf-8

from pcounter import pcounter, util

def init():
  return pcounter.ICounter("stealth", pcounter.to_on_default, 
                                      pcounter.to_off_default,
                                      output)

def output(counts, history):
  bonus_rate = util.gen_bonusrate(counts[pcounter.COUNT_INDEX.TOTALCOUNT], 
                                  counts[pcounter.COUNT_INDEX.BONUS])
  chain = util.gen_chain(counts[pcounter.COUNT_INDEX.CHAIN], "Lock On!")
  fmt = '<span font-desc="Ricty Bold 15"><u>Games</u>\n' \
        '<span size="x-large">{0}</span>({1})\n' \
        '<u>Bonus</u>\n' \
        '<span size="large">{2}</span>/{3} ({4}){5}</span>'
  return fmt.format(util.decolate_number(counts[pcounter.COUNT_INDEX.COUNT], 4),
                 util.decolate_number(counts[pcounter.COUNT_INDEX.TOTALCOUNT], 5), 
                 util.decolate_number(counts[pcounter.COUNT_INDEX.BONUS], 2), 
                 util.decolate_number(counts[pcounter.COUNT_INDEX.CHANCE], 2), 
                 bonus_rate, chain)
