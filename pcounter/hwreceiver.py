# coding: utf-8

class HwReceiverError(Exception): pass

class HwReceiver(object):
  def get_value(self):
    raise NotImplementedError

  def get_port_value(self):
    raise NotImplementedError

