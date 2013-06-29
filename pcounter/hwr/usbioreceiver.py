# coding: utf-8
# vim: ts=2 sts=2 sw=2 et

from pcounter.hwr.hwreceiver import HwReceiver, HwReceiverError
from pcounter.hwr.pyusbio import pyusbio

class UsbIoReceiver(HwReceiver):
  def __init__(self, invert=True):
    self.invert = invert
    self.usbio = pyusbio.USBIO(timeout=50)
    if not self.usbio.find_and_init():
      raise HwReceiverError("Failed to initialize USB-IO 2.0 module.")

  def get_port_value(self):
    p0, p1 = self.usbio.send2read()
    p = (p1 << 8) + p0
    p = ~p if self.invert else p
    return p

