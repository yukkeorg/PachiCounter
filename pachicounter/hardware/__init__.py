# vim: ts=4 sts=4 sw=4 et

import importlib


VALID_RECEIVERS = {
    'dummy': ('pachicounter.hardware.dummy', 'DummyReceiver'),
    'usbio': ('pachicounter.hardware.usbio', 'UsbIoReceiver'),
}


class HwReceiverError(Exception):
    pass


class HwReceiver(object):
    def get_port_value(self):
        raise NotImplementedError


def hwReceiverFactory(name, *args, **kw):
    if name not in VALID_RECEIVERS:
        raise NameError("{0} receiver object is not found")

    modname, clsname = VALID_RECEIVERS[name]
    module = importlib.import_module(modname)
    klass = getattr(module, clsname)

    return klass(*args, **kw)
