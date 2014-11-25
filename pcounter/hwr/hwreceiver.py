# coding: utf-8
# vim: ts=4 sts=4 sw=4 et

class HwReceiverError(Exception): pass

class HwReceiver(object):
    def get_port_value(self):
        raise NotImplementedError

