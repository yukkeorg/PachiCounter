# coding: utf-8

from pluginloader import PluginLoader

class ICounter(object):
  """ コールバックインターフェース """
  def __init__(self, name=None, func_to_on=None, func_to_off=None, func_output=None):
    self.name = name
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
  def __init__(self, basedir, plugindir):
    super(CounterPluginLoader, self).__init__(basedir, plugindir)

  def get(self, pluginname):
    mod = super(CounterPluginLoader, self).get(pluginname)
    if mod and callable(mod.init):
      ic = mod.init()
      if isinstance(ic, ICounter):
        return ic
    return None

