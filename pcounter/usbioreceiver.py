# coding: utf-8

import sys
from hwreceiver import HwReceiver
from pyusbio import pyusbio

class UsbIoReceiver(HwReceiver):
  def __init__(self):
    self.usbio = pyusbio.USBIO(timeout=50)
    if not self.usbio.find_and_init():
      raise hwreceiver.HwReceiverError("Failed to initialize USB-IO 2.0 module.")

  def get_port_value(self, invert=False):
    port0, port1 = self.usbio.send2read()
    port = (port1 << 8) + port0
    port = ~port if invert else port
    return port

