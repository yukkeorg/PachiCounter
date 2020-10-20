# vim: ts=4 sts=4 sw=4 et

import sys
import enum
import logging
try:
    import ujson as json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        import json
from pachicounter.hardware import HwReceiver
from pachicounter.plugin import ICounter


logger = logging.getLogger("PachiCounter")


class SIGNAL_BIT(enum.IntEnum):
    COUNT = 0
    BONUS = 1
    CHANCE = 2
    SBONUS = 3
    LAST = 4


N_BITS = SIGNAL_BIT.LAST
BITMASK = (1 << SIGNAL_BIT.LAST) - 1


class PCounterError(Exception):
    pass


class CountData:
    def __init__(self, *args, colnames=None):
        if colnames is None:
            colnames = []
        elif isinstance(colnames, str):
            colnames = [colnames]
        else:
            colnames = list(colnames)
        colnames += args
        self.__dict__['counts'] = dict.fromkeys(colnames, 0)

    def __getitem__(self, key):
        return self.__dict__['counts'][key]

    def __setitem__(self, key, val):
        if key in self.__dict__['counts']:
            self.__dict__['counts'][key] = val

    __getattr__ = __getitem__

    __setattr__ = __setitem__

    def getdict(self):
        return self.__dict__['counts']

    def reset(self):
        for k in self.__dict__['counts']:
            self.__dict__['counts'][k] = 0

    def save(self, filename):
        with open(filename, 'wb') as fp:
            s = json.dumps(self.__dict__['counts'])
            fp.write(s.encode('utf-8'))

    def load(self, filename, raise_ok=False):
        try:
            with open(filename, 'rb') as fp:
                try:
                    data = json.load(fp)
                except Exception:
                    return
            for k in data:
                if k in self.__dict__['counts']:
                    self.__dict__['counts'][k] = data[k]
        except FileNotFoundError:
            if raise_ok:
                raise
            pass


class PCounter(object):
    def __init__(self, hardware, cif, countdata, eol=None, output=None):
        if not isinstance(hardware, HwReceiver):
            raise TypeError(u"hardware は HwReceiver のインスタンスではありません。")
        if not isinstance(cif, ICounter):
            raise TypeError(u"cif は ICounter のインスタンスではありません。")

        self.hardware = hardware
        self.cif = cif
        self.eol = '\0' if eol is None else eol
        self.output = output or sys.stdout
        self.countdata = countdata
        self.__switch = 0
        self.__prevcountstr = ""
        self.__prevportval = -1

    def countup(self, portval):
        for bit in (SIGNAL_BIT.COUNT,
                    SIGNAL_BIT.BONUS,
                    SIGNAL_BIT.CHANCE,
                    SIGNAL_BIT.SBONUS):
            checkbit = 1 << bit
            edgeup = bool(portval & checkbit)
            state = bool(self.__switch & checkbit)
            if edgeup and not state:
                # 調査中ビットの状態が0->1になるとき
                self.__switch |= checkbit
                self.cif.on(bit, portval, self.countdata)
            elif not edgeup and state:
                # 調査中ビットの状態が1->0になるとき
                self.__switch &= (~checkbit)
                self.cif.off(bit, portval, self.countdata)

    def display(self):
        countstr = self.cif.build(self.countdata)
        if countstr != self.__prevcountstr:
            self.__prevcountstr = countstr
            self.output.write(countstr)
            self.output.write(self.eol)
            self.output.flush()

    def loop(self):
        portval = self.hardware.get_port_value()
        if portval != self.__prevportval:
            self.__prevportval = portval
            self.countup(portval)
            self.display()
        return True
