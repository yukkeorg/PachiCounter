# coding: utf-8

def enum(*seq, **named):
  enums = dict(zip(seq, range(len(seq))), **named)
  return type('Enum', (), enums)


def decolate_number(num, digit, zero_color=None):
  if zero_color is None:
    zero_color = "#888888"
  s = "{{0:0{0}}}".format(digit).format(num)
  idx = digit - len(str(num))
  if idx < 1:
    return s
  return '<span color="{0}">'.format(zero_color) + s[0:idx] + '</span>' + s[idx:]


def gen_bonusrate(total, now):
  try:
    bonus_rate = '<span size="x-small">1/</span>{0:.1f}'.format(float(total)/now)
  except ZeroDivisionError:
    bonus_rate = '<span size="x-small">1/</span>-.-'
  return bonus_rate


def gen_chain(n_chain, suffix=None):
  if suffix is None:
    suffix = "Chain(s)"
  chain = ""
  if n_chain > 0:
    chain = '\n<span size="xx-large">{0}</span>{1}'.format(decolate_number(n_chain, 3), suffix)
  return chain


def gen_history(history, n):
  if history and len(history) > 0:
    a = []
    n = min(n, 5)
    for h in list(reversed(history))[0:n]:
      a.append(u'{1}<span size="small">({0})</span>'.format(*h))
  return u' '.join(a)

