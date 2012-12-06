#!/usr/bin/env python
# coding: utf-8

# Copyright (c) 2011-2012, Yusuke Ohshima
# All rights reserved.
#
# This program is under the 2-clauses BSD License.
# For details, please see LICENSE file.

import os
import sys

BASEDIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, BASEDIR)

from pcounter.app import App

if __name__ == '__main__':
  app = App(BASEDIR, sys.argv[1:])
  sys.exit(app.main())
