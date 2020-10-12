# vim: ts=4 sts=4 sw=4 et

VALID_RECEIVERS = {
    'dummy': ('pcounter.hardware.dummy', 'DummyReceiver'),
    'usbio': ('pcounter.hardware.usbio', 'UsbIoReceiver'),
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
    module = __import__(modname, globals(), locals(), [clsname])
    klass = getattr(module, clsname)
    return klass(*args, **kw)
