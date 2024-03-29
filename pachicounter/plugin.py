# vim: ts=4 sts=4 sw=4 et
#####################################################################
# Pachi Counter
# Copyright (c) 2011-2020, Yusuke Ohshima All rights reserved.
#
# License: MIT.
# For details, please see LICENSE file.
#####################################################################

import importlib
from typing import Tuple

from pachicounter.util import calcLpsOnNorm, calcLpsOnChance


class PluginLoader:
    def getClass(self, pluginname):
        """ 指定されたプラグインをインポートしてその型を返す """
        modname = ".".join(("pachicounter", "machine", pluginname))
        module = importlib.import_module(modname)
        return getattr(module, pluginname)

    def getInstance(self, pluginname, args=None):
        klass = self.getClass(pluginname)
        if args is None:
            return klass()
        else:
            return klass(args)


class BonusRound:
    def __init__(self, nround: int, limitsec: float, gainpts: int):
        self.nround: int = nround
        self.limitsec: float = limitsec
        self.gainpts: int = gainpts


class BonusDetectorBase:
    BonusRoundList: Tuple[BonusRound] = ()

    def detectBonus(self, t: float):
        for bi in self.BonusRoundList:
            if t < bi.limitsec:
                return bi


class ICounter:
    LPS = (
        calcLpsOnNorm(3, 20),         # losepts/sec
        calcLpsOnChance(0.90),
    )
    MaxSPC: float = 40.0       # sec/count

    def createCountData(self):
        raise NotImplementedError

    def on(self, bit, state, countdata):
        raise NotImplementedError

    def off(self, bit, state, countdata):
        raise NotImplementedError

    def build(self, cd):
        raise NotImplementedError


class UtilsMixin(object):
    def bulk_set_color(self, d, color):
        for k in d:
            if isinstance(d[k], dict):
                d[k]['color'] = color

    def bulk_format_text(self, d, *args, **kw):
        for k in d:
            if isinstance(d[k], dict):
                if 'text' in d[k]:
                    d[k]['text'] = d[k]['text'].format(*args, **kw)

    def rgb2int(self, r, g, b, a=0xff):
        return (a << 24) + (r << 16) + (g << 8) + b

    def ordering(self, n):
        rem10 = n % 10
        rem100 = n % 100
        if rem10 in (1, 2, 3) and not (10 <= rem100 < 20):
            post = ('st', 'nd', 'rd')[rem10 - 1]
        else:
            post = 'th'
        return str(n)+post
