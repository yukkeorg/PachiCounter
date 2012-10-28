# coding: utf-8

import os
import sys
from . import pcounter

class PluginLoader(object):
  def __init__(self, basedir, plugindir):
    self._plugindir = plugindir
    self._pluginnames = []
    self._importedmodules = None

    fullplugindir = os.path.join(basedir, plugindir)
    for fname in os.listdir(fullplugindir):
      if fname.endswith(".py") and not fname.startswith("__init__"):
        self._pluginnames.append(fname.replace(u".py", u""))

  def get(self, pluginname):
    if pluginname in self._pluginnames:
      try:
        importedmodules = __import__(self._plugindir, {}, {}, [pluginname])
      except ImportError:
        return None
      mod = importedmodules.__dict__.get(pluginname, None)
      return mod
    return None


class CounterInterfacePluginLoader(PluginLoader):
  def __init__(self, basedir, plugindir):
    super(CounterInterfacePluginLoader, self).__init__(basedir, plugindir)

  def get(self, pluginname):
    mod = super(CounterInterfacePluginLoader, self).get(pluginname)
    if mod and callable(mod.init):
      ic = mod.init()
      if isinstance(ic, pcounter.ICounter):
        return ic
    return None
