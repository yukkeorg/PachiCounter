#!/usr/bin/env python3
# coding: utf-8
# vim: ts=4 sts=4 sw=4 et

"""
    Pachi Counter

    Copyright (c) 2011-2014, Yusuke Ohshima
    All rights reserved.

    License: MIT.
    For details, please see LICENSE file.
"""

import os
from pachicounter.app import App


BASEDIR = os.path.dirname(os.path.realpath(os.path.join(__file__)))


def main():
    App(BASEDIR).main()


if __name__ == "__main__":
    main()
