# coding: utf-8
# vim: ts=2 sts=2 sw=2 et

import os

class PluginLoader(object):
  def __init__(self, basedir, plugindir):
    self._plugindir = plugindir
    self._pluginnames = []
    # ディレクトリ内のプラグインファイルを収集 
    fullplugindir = os.path.join(basedir, plugindir)
    for fname in os.listdir(fullplugindir):
      if fname.endswith(".py") and not fname.startswith("__init__"):
        self._pluginnames.append(fname.replace(u".py", u""))

  def get(self, pluginname):
    """ 指定されたプラグインをインポートしてその型を返す """  
    if pluginname not in self._pluginnames:
      raise NameError("{0} is not found.".format(pluginname))
  module = __import__(self._plugindir, {}, {}, [pluginname])
  return getattr(module, pluginname)


class CounterPluginLoader(PluginLoader):
  """ PachiCounter用プラグインローダー """
  def get(self, pluginname):
    mod = super(CounterPluginLoader, self).get(pluginname)
    if mod is None:
      raise NameError("{0} is not found.".format(pluginname))
    if not callable(mod.init):
      raise AttributeError("{0} is not contain 'init' function".format(pluginname))
    return mod


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


