# coding: utf-8

import logging
from . import pyusbio

logger = logging.getLogger('PCounter')

class HwReceiverError(Exception): pass

class HwReceiver(object):
  def init(self):
    self.usbio = pyusbio.USBIO()
    if not self.usbio.find_and_init():
      raise HwReceiverError("Failed to initialize USB-IO 2.0 module.")

  def get_port_value(self):
    port0, port1 = self.usbio.send2read()
    port = (port1 << 8) + port0
    return port

