# vim: ts=4 sts=4 sw=4 et

from pachicounter.core import SIGNAL_BIT, CountData, json
from pachicounter.plugin import ICounter, UtilsMixin
from pachicounter.util import gen_bonusrate, bit_is_enable


class stealth(ICounter, UtilsMixin):
    def createCountData(self):
        return CountData('count', 'totalcount', 'bonus',
                         'chance', 'chain', 'chancetime', 'isbonus',
                         'sbonus')

    def on(self, cbtype, iostatus, cd):
        if cbtype == SIGNAL_BIT.COUNT:
            cd['count'] += 1
            if not bit_is_enable(iostatus, SIGNAL_BIT.CHANCE):
                cd['totalcount'] += 1
        elif cbtype == SIGNAL_BIT.BONUS:
            cd['bonus'] += 1
            cd['isbonus'] = 1
            if bit_is_enable(iostatus, SIGNAL_BIT.CHANCE):       # チャンス中
                cd['chain'] += 1
        elif cbtype == SIGNAL_BIT.CHANCE:
            cd['chance'] += 1
        elif cbtype == SIGNAL_BIT.SBONUS:
            cd['sbonus'] += 1

    def off(self, cbtype, iostatus, cd):
        if cbtype == SIGNAL_BIT.BONUS:
            cd['isbonus'] = 0
            cd['count'] = 0
            if bit_is_enable(iostatus, SIGNAL_BIT.CHANCE):       # チャンス中
                cd['chancetime'] = 1
        elif cbtype == SIGNAL_BIT.CHANCE:
            cd['count'] = 0
            cd['chain'] = 0
            cd['chancetime'] = 0

    def build(self, cd):
        d = cd.counts
        bonusrate = gen_bonusrate(d['totalcount'], d['chance'])
        if cd['chancetime'] == 1:
            chainstr = "STEALTH RUSH - {0} Bonus".format(self.ordering(d['chain']))
            color = self.rgb2int(0xff, 0xff, 0x33)
            dd = {
                'framesvg0': 'resource/orangeflame_wide.svg',
                '0': {'text': '{count} <small>OF</small> 99'.format(**d)},
                '1': {'text': bonusrate},
                '2': {'text': '{bonus} / {chance}'.format(**d)},
                '4': {'text': chainstr}
            }
            self.bulk_set_color(dd, color)
            dd['0']['color'] = self.rgb2int(0, 0, 0)
        else:
            dd = {
                'framesvg0': 'resource/blueflame_wide.svg',
                '0': {'text': '{count} / {totalcount}'.format(**d)},
                '1': {'text': bonusrate},
                '2': {'text': '{bonus} / {chance}'.format(**d)},
                '4': {'text': ' '}
            }
            if cd['isbonus'] == 1:
                dd['framesvg0'] = 'resource/orangeflame_wide.svg'
                self.bulk_set_color(dd, self.rgb2int(0xff, 0xff, 0x33))
                dd['0']['color'] = self.rgb2int(0, 0, 0)
            else:
                self.bulk_set_color(dd, self.rgb2int(0xff, 0xff, 0xff))
        return json.dumps(dd)
