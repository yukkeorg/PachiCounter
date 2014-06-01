# coding: utf-8
# vim: ts=2 sts=2 sw=2 et

import os
from pcounter.util import calcLpsOnNorm, calcLpsOnChance

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
    imp = __import__(self._plugindir, {}, {}, [pluginname])
    module = getattr(imp, pluginname)
    return getattr(module, pluginname)


class BonusRound(object):
  def __init__(self, nround, limitsec, gainpts):
    self.nround = nround
    self.limitsec = limitsec
    self.gainpts = gainpts


class ICounter(object):
  LPS = (calcLpsOnNorm(3, 20),     # losepts/sec
         calcLpsOnChance(0.90))
  MaxSPC = 40.0   # sec/count
  BonusRoundList = ()

  def detectBonus(self, t):
    for bi in self.BonusRoundList:
      if t < bi.limitsec:
        return bi

  def createCountData(self):
    raise NotImplemented()

  def on(self, bit, state, countdata):
    raise NotImplemented()

  def off(self, bit, state, countdata):
    raise NotImplemented()

  def build(self, cd):
    raise NotImplemented()



class UtilsMixin(object):
  def bulk_set_color(self, d, color):
    for k in d:
      if isinstance(d[k], dict):
        d[k]['color'] = color

  def bulk_format_text(self, d, *args, **kw):
    for k in d:
      if isinstance(d[k], dict):
        if 'text' in d[k]:
          d[k]['text'] = d[k]['text'].format(*args, **kw)

  def rgb2int(self, r, g, b, a=0xff):
      return (a << 24) + (r << 16) + (g << 8) + b

  def ordering(self, n):
    rem10 = n % 10
    rem100 = n % 100
    if rem10 in (1, 2, 3) and not (10 <= rem100 < 20):
      post = ('st', 'nd', 'rd')[rem10 - 1]
    else:
      post = 'th'
    return str(n)+post

