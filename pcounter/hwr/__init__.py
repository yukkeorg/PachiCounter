# coding: utf-8
# vim: ts=2 sts=2 sw=2 et

from pcounter.hwr.hwreceiver import HwReceiver

_RECEIVERS = {
  'dummy': ('pcounter.hwr.dummyreceiver', 'DummyReceiver'),
  'usbio': ('pcounter.hwr.usbioreceiver', 'UsbIoReceiver'),
}

def hwreceiverFactory(name):
  if name not in _RECEIVERS:
    raise NameError("{0} receiver object is not found")

  modname, clsname = _RECEIVERS[name]
  module = __import__(modname, globals(), locals(), [clsname])
  klass = getattr(module, clsname)
  return klass()
