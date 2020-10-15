# coding: utf-8
# vim: ts=4 sts=4 sw=4 et

from pachicounter.core import json, CountData, USBIO_BIT
from pachicounter.plugin import ICounter, UtilsMixin
from pachicounter.pctypes import enum
from pachicounter.util import (gen_bonusrate, bit_is_enable)

STATE = enum('NORMAL', 'UFOZONE', 'XTRARUSH')


class xfiles(ICounter, UtilsMixin):
    def __init__(self):
        self.state = STATE.NORMAL

    def createCountData(self):
        return CountData('count', 'totalcount', 'chancegames',
                         'normalgames', 'bonus', 'sbonus',
                         'xr', 'chain', 'chance')

    def on(self, cbittype, bitgroup, cd):
        if cbittype == USBIO_BIT.COUNT:
            cd.count += 1
            cd.totalcount += 1
            if bit_is_enable(bitgroup, USBIO_BIT.CHANCE):
                cd.chancegames += 1
                # 直撃のEXTRA-RUSHは、最初の5回転のみではUFO-ZONEと見分けが
                # つかないため、UFO-ZONE状態中に5回転以上回ったら、直撃の
                # XTRA-RUSHだったと判定する。
                if self.state == STATE.UFOZONE and cd.count > 5:
                    self.state = STATE.EXTRARUSH
                    cd.xr += 1
            else:
                cd.normalgames += 1
        if cbittype == USBIO_BIT.BONUS:
            cd.bonus += 1
            if bit_is_enable(bitgroup, USBIO_BIT.CHANCE):
                cd.chain += 1
                if self.state == STATE.NORMAL:
                    self.state = STATE.UFOZONE
                elif self.state == STATE.UFOZONE:
                    self.state = STATE.XTRARUSH
                    cd.xr += 1
        if cbittype == USBIO_BIT.CHANCE:
            cd.chance += 1
        if cbittype == USBIO_BIT.SBONUS:
            cd.sbonus += 1

    def off(self, cbittype, bitgroup, cd):
        if cbittype == USBIO_BIT.BONUS:
            cd.count = 0
        if cbittype == USBIO_BIT.CHANCE:
            self.state = STATE.NORMAL
            cd.chain = 0

    def build(self, cd):
        dd = {
            '1': {'text': gen_bonusrate(cd.totalcount, cd.sbonus)},
            '2': {'text': '{sbonus} / {chance} / {xr}'},
        }
        color = self.rgb2int(0xff, 0xff, 0xff)

        if self.state == STATE.NORMAL:
            dd.update({
                '0': {'text': '{count} / {totalcount}'},
                '4': {'text': ''},
            })

        elif self.state == STATE.UFOZONE:
            color = self.rgb2int(0x10, 0xff, 0x10)
            dd.update({
                '0': {'text': '{count} <small>OF</small> 5'},
                '4': {'text': 'UFO-ZONE'},
            })

        elif self.state == STATE.XTRARUSH:
            color = self.rgb2int(0xff, 0xff, 0x10)
            dd.update({
                '0': {'text': '{count}<small> OF 80</small>'},
                '4': {'text': 'XTRA-RUSH - {chain} Bonus Chain'},
            })

        self.bulk_set_color(dd, color)
        self.bulk_format_text(dd, **(cd.getdict()))

        return json.dumps(dd)
