# coding: utf-8
# vim: ts=2 sts=2 sw=2 et

from pcounter.core import json, CountData, USBIO_BIT
from pcounter.plugin import ICounter, UtilsMixin
from pcounter.util import (gen_bonusrate, bit_is_enable)


class vb(ICounter, UtilsMixin):
  FALLDOWN_POSSIBILITY = 1/338.5

  def createCountData(self):
    return CountData(("count", "totalcount", "chancegames", 
                      "normalgames", "bonus", "chain", "chance"))

  def on(self, cbittype, bitgroup, cd):
    if cbittype == USBIO_BIT.COUNT:
      cd["count"] += 1
      cd["totalcount"] += 1
      if bit_is_enable(bitgroup, USBIO_BIT.CHANCE):
        cd["chancegames"] += 1
      else:
        cd["normalgames"] += 1
    elif cbittype == USBIO_BIT.BONUS:
      cd["bonus"] += 1
      if bit_is_enable(bitgroup, USBIO_BIT.CHANCE):
        cd["chain"] += 1
    elif cbittype == USBIO_BIT.CHANCE:
      cd["chance"] += 1

  def off(self, cbittype, bitgroup, cd):
    if cbittype == USBIO_BIT.BONUS:
      cd["count"] = 0
    if cbittype == USBIO_BIT.CHANCE:
      cd["count"] = 0
      cd["chain"] = 0
      cd["chancegames"] = 0

  def build(self, cd):
    if cd["chain"] > 0:
      bonus_rate = gen_bonusrate(cd["chancegames"], cd["chain"])
      # vat = self.ordering(cd["chance"])
      # continue_possibilty = ((1.0 - FALLDOWN_POSSIBILITY)
      #                            ** cd["chancegames"]) * 100
      dd = {
        "framesvg0" : "resource/orangeflame_wide.svg", 
        "0" : {"text": "{count}<small> / {chancegames}</small>" },
        "1" : {"text": bonus_rate },
        "2" : {"text": "{bonus} / {chance}" },
        "3" : {"text": " " },
        "4" : {"text": "{0} VAT - {chain} Bonus" }
      }
      self.bulk_set_color(dd, self.rgb2int(0xff, 0xff, 0x33))
      dd["8"]["color"] = self.rgb2int(0, 0, 0)
    else:
      color = self.rgb2int(0xff, 0xff, 0xff)
      bonus_rate = gen_bonusrate(cd["normalgames"], cd["chance"])
      dd = {
        "framesvg0" : "resource/blueflame_wide.svg",
        "0" : {"text": "{count}<small> / {normalgames}</small>" },
        "1" : {"text": bonus_rate },
        "2" : {"text": "{bonus} / {chance}" },
        "3" : {"text": "" },
        "4" : {"text": "" }
      }
      self.bulk_set_color(dd, color)
    self.buld_format_text(dd, **cd.counts)
    return json.dumps(dd)
