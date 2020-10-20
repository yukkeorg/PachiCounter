# vim: ts=4 sts=4 sw=4 et
#####################################################################
# Pachi Counter
# Copyright (c) 2011-2020, Yusuke Ohshima All rights reserved.
#
# License: MIT.
# For details, please see LICENSE file.
#####################################################################


def bit_is_enable(val, bit):
    return bool(val & (1 << bit))


def ordering(n):
    less100 = n % 100
    less10 = less100 % 10
    if less10 in (1, 2, 3) and not (10 <= less100 < 20):
        t = str(n) + ('st', 'nd', 'rd')[less10 - 1]
    else:
        t = str(n) + 'th'
    return t


def bulk_set_color(d, color):
    for k in d:
        d[k]['color'] = color


def rgb(r, g, b, a=0xff):
    return (a << 24) + (r << 16) + (g << 8) + b


def decolate_number(num, min_disp_digit, num_color=None, zero_color=None):
    if zero_color is None:
        zero_color = '#888888'
    last_zero_pos = max(min_disp_digit - len(str(num)), 0)
    raw_num_str = '{{0:0{0}}}'.format(min_disp_digit).format(num)

    if num_color is None:
        num_fmt = str(num)
    else:
        num_fmt = ('<span color="{0}">{1}</span>'
                   .format(num_color, raw_num_str[last_zero_pos:]))
    if last_zero_pos == 0:
        zero_fmt = ''
    else:
        zero_fmt = ('<span color="{0}">{1}</span>'
                    .format(zero_color, raw_num_str[0:last_zero_pos]))
    return ''.join((zero_fmt, num_fmt))


def gen_bonusrate(total, now, numesize=None, ndec=1):
    numesize = numesize or "small"
    nd = 10 ** ndec
    try:
        p = int((float(total) / now) * nd)
        d = p // nd
        f = p % nd
        ratestr = ('<span size="{{2}}">'
                   '1/</span>{{0}}<small>.{{1:0{}}}</small>'.format(ndec))
        bonus_rate = ratestr.format(d, f, numesize)
    except ZeroDivisionError:
        bonus_rate = ('<span size="{0}">1/</span>-.<small>{1}</small>'
                      .format(numesize, "-"*ndec))
    return bonus_rate


def gen_chain(n_chain, suffix=None):
    suffix = suffix or "Chain(s)"
    chain = ""
    if n_chain > 0:
        chain = ('\n<span size="xx-large">{0}</span>{1}'
                 .format(decolate_number(n_chain, 3),
                         suffix))
    return chain


def gen_history(history, n, sep=" ", isfill=False):
    a = []
    if history:
        n = min(n, 5)
        for h in list(reversed(history))[0:n]:
            if h[0] is None:
                a.append(str(h[1]))
            else:
                a.append('{1}<span size="small">({0})</span>'.format(*h))
    if isfill:
        for i in range(5):
            a.append('')
    return sep.join(a[:n])


def calcLpsOnNorm(bc, r):
    return 1.6667 * (-1.0 + ((bc * r) / (250.0 + bc * r)))


def calcLpsOnChance(base):
    return 1.6667 * (-1.0 + base)
