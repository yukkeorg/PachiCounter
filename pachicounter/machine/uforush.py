# coding: utf-8
# vim: ts=4 sts=4 sw=4 et

import time

from pachicounter.core import USBIO_BIT, CountData, json
from pachicounter.plugin import ICounter, UtilsMixin, BonusRound
from pachicounter.util import (gen_bonusrate, bit_is_enable,
                               calcLpsOnNorm, calcLpsOnChance)


class DeltaTime(object):
    def __init__(self):
        self.__prev = time.time()

    def getDelta(self):
        now = time.time()
        d = now - self.__prev
        self.__prev = now
        return d

    def check(self):
        self.__prev = time.time()


class uforush(ICounter, UtilsMixin):
    NORMAL_LPS = calcLpsOnNorm(3, 20)           # lose_pts/sec
    CHANCE_LPS = calcLpsOnChance(0.80)

    MAX_SPC = 20.0   # sec/count

    BonusRoundList = (
        BonusRound(nround=1,  limitsec=55.0,   gainpts=80),
        BonusRound(nround=2,  limitsec=65.0,   gainpts=160),
        BonusRound(nround=3,  limitsec=76.0,   gainpts=240),
        BonusRound(nround=4,  limitsec=88.0,   gainpts=320),
        BonusRound(nround=5,  limitsec=100.0,  gainpts=400),
        BonusRound(nround=6,  limitsec=110.0,  gainpts=480),
        BonusRound(nround=7,  limitsec=120.0,  gainpts=560),
        BonusRound(nround=8,  limitsec=136.0,  gainpts=640),
        BonusRound(nround=12, limitsec=9999.0, gainpts=960),
    )

    def __init__(self):
        self.gcdelta = DeltaTime()
        self.bonustime = DeltaTime()

    def createCountData(self):
        return CountData("count", "totalcount", "bonus",
                         "chance", "chain", "chancetime",
                         "isbonus", "sbonus", "spg", "spb",
                         "pbr", "voutput")

    def on(self, cbtype, iostatus, cd):
        ischance = bit_is_enable(iostatus, USBIO_BIT.CHANCE)

        if cbtype == USBIO_BIT.COUNT:
            cd.count += 1
            if not ischance:
                cd.totalcount += 1

            d = self.gcdelta.getDelta()
            lps = (self.NORMAL_LPS if not ischance else self.CHANCE_LPS)
            cd.spg = d
            cd.voutput += (min(self.MaxSPC, d) * lps)

        elif cbtype == USBIO_BIT.BONUS:
            self.bonustime.check()
            cd.bonus += 1
            cd.isbonus = 1
            if ischance:
                cd.chain += 1

        elif cbtype == USBIO_BIT.CHANCE:
            cd.chance += 1

    def off(self, cbtype, iostatus, cd):
        ischance = bit_is_enable(iostatus, USBIO_BIT.CHANCE)
        if cbtype == USBIO_BIT.BONUS:
            cd.isbonus = 0
            cd.count = 0
            if ischance:
                cd.chancetime = 1

            self.gcdelta.check()
            d = self.bonustime.getDelta()
            bi = self.detectBonus(d)
            cd.spb = d
            cd.pbr = bi.nround
            cd.voutput += bi.gainpts

        elif cbtype == USBIO_BIT.CHANCE:
            cd.chain = 0
            cd.chancetime = 0
            cd.totalcount += cd.count

    def build(self, cd):
        bonusrate = gen_bonusrate(cd.totalcount, cd.chance)
        if cd.chancetime == 1:
            dd = {
                "framesvg0": "resource/orangeflame_wide.svg",
                "0": {"text": "{count}<small></small>"},
                "1": {"text": "{chain}<small><small> CHAIN</small></small>"},
                "2": {"text": "{bonus}<small> ({chance})</small>"},
                "3": {"text": "{voutput:.0f}<small><small> PTS</small></small>"},
                "4": {"text": "UFO CHANCE ({pbr}R)"},
            }

            if cd.chain > 1:
                dd["4"]["text"] = "UFO RUSH ({pbr}R)"

            # self.bulk_set_color(dd, self.rgb2int(0xff, 0xff, 0x33))
            dd["0"]["color"] = self.rgb2int(0, 0, 0)
        else:
            dd = {
                "framesvg0": "resource/blueflame_wide.svg",
                "0": {"text": "{count}<small> / {totalcount}</small>"},
                "1": {"text": bonusrate},
                "2": {"text": "{bonus}<small> ({chance})</small>"},
                "3": {"text": "{voutput:.0f}<small><small> PTS</small></small>"},
                "4": {"text": "{spg:.2f}sec/G"},
            }
            self.bulk_set_color(dd, self.rgb2int(0xff, 0xff, 0xff))

        if cd.isbonus == 1:
            dd["framesvg0"] = "resource/orangeflame_wide.svg"
            dd["4"]["text"] = "BONUS TIME"
            # self.bulk_set_color(dd, self.rgb2int(0xff, 0xff, 0x33))
            dd["0"]["color"] = self.rgb2int(0, 0, 0)

        self.bulk_format_text(dd, **(cd.getdict()))

        return json.dumps(dd)
