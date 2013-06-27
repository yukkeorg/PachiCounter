# coding: utf-8
# vim: ts=2 sts=2 sw=2 et

from hwreceiver import HwReceiver
from dummyreceiver import DummyReceiver
from usbioreceiver import UsbIoReceiver

_RECEIVERS = {
  'dummy': DummyReceiver,
  'usbio': UsbIoReceiver,
}

def hwreceiverFactory(name):
  if name in _RECEIVERS:
    return _RECEIVERS[name]()
  else:
    raise NameError("{0} receiver object is not found")
