#!/usr/bin/env python
# coding: utf-8

# Copyright (c) 2012, Yusuke Ohshima
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without modification, 
# are permitted provided that the following conditions are met:
# 
#   - Redistributions of source code must retain the above copyright notice, 
#     this list of conditions and the following disclaimer.
# 
#   - Redistributions in binary form must reproduce the above copyright notice, 
#     this list of conditions and the following disclaimer in the documentation 
#     and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND 
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED 
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. 
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, 
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, 
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, 
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY 
# OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE 
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF 
# THE POSSIBILITY OF SUCH DAMAGE.

from __future__ import print_function

import os
import sys
import codecs
import shlex
import subprocess
import signal

import pygtk
pygtk.require('2.0')
import gtk
import glib

class StdoutReader(object):
  def __init__(self, cmd_and_args):
    self.cmd_and_args = cmd_and_args
    self.callback_table = {}
    self.child = None
  
  def bind(self, eventname, callback):
    if callback and callable(callback):
      self.callback_table[eventname] = callback

  def run(self):
    try:
      self.child = subprocess.Popen(self.cmd_and_args, 
                                    stdout=subprocess.PIPE, 
                                    close_fds=True)
    except OSError, e:
      print(e.message)
      return
    try:
      glib.io_add_watch(self.child.stdout, 
                        glib.IO_IN | glib.IO_HUP, 
                        self._on_event)
    except glib.GError as e:
      self.terminate()
      print(e.message)
      return
    if "start" in self.callback_table:
      self.callback_table["start"]()

  def _on_event(self, fd, condition):
    if condition & glib.IO_IN:
      text = []
      while True:
        data = fd.read(1)
        if data == "\x00" or data == "": 
          break
        text.append(data)
      if "read_ok" in self.callback_table:
        text = ''.join(text)
        self.callback_table["read_ok"](text)

    if condition & glib.IO_HUP:
      self.child.poll()
      if "end" in self.callback_table:
        self.callback_table["end"]()
      return False
    return True

  def terminate(self):
    if self.child:
      self.child.terminate()
      self.child = None

  def is_running(self):
    if self.child:
      return (self.child.returncode is None)
    else:
      return False


class PCounterGuiWindow(gtk.Window):
  def __init__(self, argv):
    gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
    self.argv = argv
    self.spawn = None
    self.build_window()

  def build_window(self):
    self.set_title("PCounter GUI")
    #self.set_default_size(800, 600)
    self.connect("delete-event", self.on_delete)
    self.connect("destroy", self.on_destroy)

    vbox_root = gtk.VBox()
    self.add(vbox_root)

    vbox_main = gtk.VBox()
    vbox_main.set_spacing(8)
    vbox_root.pack_start(vbox_main, True)
    vbox_main.pack_start(self.build_box(), True)

    self.show_all()

  def build_box(self):
    vbox = gtk.VBox()

    hbox = gtk.HBox()
    hbox.set_spacing(8)
    vbox.pack_start(hbox, False)

    # hbox.pack_start(gtk.Label("CommandLine:"), False)
    # self.ent_exec_path = gtk.Entry()
    # self.ent_exec_path.set_text("python pcounter.py -r -i -t")
    # hbox.pack_start(self.ent_exec_path, True)

    self.btn_exec = gtk.Button("Run")
    self.btn_exec.set_size_request(100, -1)
    self.btn_exec.connect("clicked", self.on_exec)
    hbox.pack_start(self.btn_exec, False)

    self.output_text = gtk.Label()
    vbox.pack_start(self.output_text, True)

    return vbox

  # -- Internal Callback
  def on_exec(self, widget):
    if self.spawn and self.spawn.is_running():
      return 
    #cmdline = shlex.split(self.ent_exec_path.get_text())
    cmdline = ["python", "pcounter.py"] + self.argv
    self.spawn = StdoutReader(cmdline)
    self.spawn.bind("read_ok", self.on_read_ok)
    self.spawn.run()

  def on_read_ok(self, text):
    self.output_text.set_markup(text)

  def on_kill(self, widget):
    if self.spawn and self.spawn.is_running():
      sr.terminate()
    
  def on_delete(self, widget, event):
    pass

  def on_destroy(self, widget):
    if self.spawn and self.spawn.is_running():
      self.spawn.terminate()
    gtk.main_quit()


if __name__ == "__main__":
  cm = PCounterGuiWindow(sys.argv[1:])
  gtk.gdk.threads_init()
  gtk.main()
