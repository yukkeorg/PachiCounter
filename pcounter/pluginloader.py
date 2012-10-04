# coding: utf-8

import os
from . import pcounter

class PluginLoader(object):
  def __init__(self, plugindir=None):
    if not os.path.exists(plugindir):
      raise OSError(u"{0} is not exists.".format(plugindir))
    self._plugindir = plugindir
    self._pluginnames = []
    self._importedmodules = None

    for fname in os.listdir(self._plugindir):
      if fname.endswith(".py") and not fname.startswith("__init__"):
        self._pluginnames.append(fname[:-3])

  def get(self, pluginname):
    if pluginname in self._pluginnames:
      try:
        importedmodules = __import__(self._plugindir, 
                                     globals(), locals(), 
                                     (pluginname, ), 0)
      except ImportError:
        return None
      mod = importedmodules.__dict__.get(pluginname, None)
      return mod
    return None


class CounterInterfacePluginLoader(PluginLoader):
  def __init__(self, plugindir):
    super(CounterInterfacePluginLoader, self).__init__(plugindir)

  def get(self, pluginname):
    mod = super(CounterInterfacePluginLoader, self).get(pluginname)
    if mod and callable(mod.init):
      ic = mod.init()
      if isinstance(ic, pcounter.ICounter):
        return ic
    return None
