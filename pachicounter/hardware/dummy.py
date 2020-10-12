# coding: utf-8
# vim: ts=4 sts=4 sw=4 et

from . import HwReceiver


class DummyReceiver(HwReceiver):
    def __init__(self):
        pass

    def get_port_value(self):
        return 0xff
