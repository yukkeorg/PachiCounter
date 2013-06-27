# coding: utf-8

from pluginloader import PluginLoader

class ICounter(object):
  """ コールバックインターフェース """
  def __init__(self, func_to_on, func_to_off, func_output):
    if callable(func_to_on):
      self.func_to_on = func_to_on
    else:
      raise TypeError("func_to_on is not function.")

    if callable(func_to_off):
      self.func_to_off = func_to_off
    else:
      raise TypeError("func_to_off is not function.")

    if callable(func_output):
      self.func_output = func_output
    else:
      raise TypeError("func_output is not function.")


class CounterPluginLoader(PluginLoader):
  """ PachiCounter用プラグインローダー """
  def get(self, pluginname):
    mod = super(CounterPluginLoader, self).get(pluginname)
    if mod is None:
      raise NameError("{0} is not found.".format(pluginname))
    if not callable(mod.init):
      raise AttributeError("{0} is not contain 'init' function".format(pluginname))
    return mod
