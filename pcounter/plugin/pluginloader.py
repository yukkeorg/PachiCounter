# coding: utf-8

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
    if pluginname in self._pluginnames:
      try:
        importedmodules = __import__(self._plugindir, 
                                     {}, {}, [pluginname])
      except ImportError:
        return None
      mod = importedmodules.__dict__.get(pluginname, None)
      return mod
    return None


