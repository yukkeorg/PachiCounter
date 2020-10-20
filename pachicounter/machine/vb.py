# vim: ts=4 sts=4 sw=4 et

from pachicounter.core import json, CountData, SIGNAL_BIT
from pachicounter.plugin import ICounter, UtilsMixin
from pachicounter.util import (gen_bonusrate, bit_is_enable)


class vb(ICounter, UtilsMixin):
    # 転落率
    FALLDOWN_POSSIBILITY = 1/338.5

    def __init__(self):
        self.bonus_history = []

    @property
    def machine_name(self):
        return "CR VirusBreaker (c) 2012 JB"

    def createCountData(self):
        return CountData(
            "count",
            "totalcount",
            "chancegames",
            "normalgames",
            "bonus",
            "chain",
            "chance",
        )

    def on(self, cbittype, bitgroup, cd):
        if cbittype == SIGNAL_BIT.COUNT:
            cd["count"] += 1
            cd["totalcount"] += 1
            if bit_is_enable(bitgroup, SIGNAL_BIT.CHANCE):
                cd["chancegames"] += 1
            else:
                cd["normalgames"] += 1
        elif cbittype == SIGNAL_BIT.BONUS:
            cd["bonus"] += 1
            if bit_is_enable(bitgroup, SIGNAL_BIT.CHANCE):
                cd["chain"] += 1
                self.bonus_history.insert(0, (cd["chain"], cd["count"]))
        elif cbittype == SIGNAL_BIT.CHANCE:
            cd["chance"] += 1

    def off(self, cbittype, bitgroup, cd):
        if cbittype == SIGNAL_BIT.BONUS:
            cd["count"] = 0
        if cbittype == SIGNAL_BIT.CHANCE:
            cd["count"] = 0
            cd["chain"] = 0
            cd["chancegames"] = 0
            self.bonus_history.clear()

    def build(self, cd):
        if cd["chain"] > 0:
            bonus_rate = gen_bonusrate(cd["chancegames"], cd["chain"])
            # vat = self.ordering(cd["chance"])
            # continue_possibilty = ((1.0 - FALLDOWN_POSSIBILITY)
            #                         ** cd["chancegames"]) * 100
            idx = len(self.bonus_history)
            if idx >= 5:
                idx = 5
            no_str = "\n".join([self.ordering(t[0]) for t in self.bonus_history[:idx]])
            cnt_str = "\n".join([str(t[1]) for t in self.bonus_history[:idx]])

            dd = {
                "framesvg0": "resource/orangeflame_wide_vb.svg",
                "0": {"text": "{count}<small> / {chancegames}</small>"},
                "1": {"text": bonus_rate},
                "2": {"text": "{bonus}<small> | {chance}</small>"},
                "3": {"text": "<small>VAT.</small>{chance} - {chain}<small> CHAIN</small>"},
                "4": {"text": no_str},
                "5": {"text": cnt_str},
            }
            self.bulk_set_color(dd, self.rgb2int(0xff, 0xff, 0x33))
            dd["0"]["color"] = self.rgb2int(0, 0, 0)
        else:
            color = self.rgb2int(0xff, 0xff, 0xff)
            bonus_rate = gen_bonusrate(cd["normalgames"], cd["chance"])
            dd = {
                "framesvg0": "resource/blueflame_wide_vb.svg",
                "0": {"text": "{count}<small> / {normalgames}</small>"},
                "1": {"text": bonus_rate},
                "2": {"text": "{bonus}<small> | {chance}</small>"},
                "3": {"text": ""},
                "4": {"text": ""},
                "5": {"text": ""},
            }
            self.bulk_set_color(dd, color)
        self.bulk_format_text(dd, **cd.counts)
        return json.dumps(dd)
