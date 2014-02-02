#!/usr/bin/env python
# coding: utf-8

# Pachi Counter
#
# Copyright (c) 2011-2014, Yusuke Ohshima
# All rights reserved.
#
# License: MIT.
# For details, please see LICENSE file.

import os
import sys

BASEDIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, BASEDIR)

from pcounter.app import App

app = App(BASEDIR)
sys.exit(app.main())
