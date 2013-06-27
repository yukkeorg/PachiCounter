# coding: utf-8
# vim: ts=2 sts=2 sw=2 et

from hwreceiver import HwReceiver, HwReceiverError

class DummyReceiver(HwReceiver):
  def __init__(self):
    pass

  def get_port_value(self):
    return 0xff

