# coding: utf-8
# vim: ts=2 sts=2 sw=2 et

class HwReceiverError(Exception): pass

class HwReceiver(object):
  def get_port_value(self):
    raise NotImplementedError

