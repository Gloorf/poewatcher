#!/usr/bin/python3
# -*- coding: utf8 -*-
#Copyright (C) 2015 Guillaume DUPUY <glorf@glorf.fr>
#This file is part of Poe Watcher.

#PoE Watcher is free software: you can redistribute it and/or modify
#it under the terms of the GNU Affero General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#PoE Watcher is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU Affero General Public License for more details.

#You should have received a copy of the GNU Affero General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>
import logging
import pyglet
import tkinter
class WarningFilter(logging.Filter):
    def filter(self, rec):
        return rec.levelno == logging.WARNING
class SoundHandler(logging.Handler):
    def __init__(self, sound_file, volume):
        super().__init__()
        self.sound = pyglet.media.load(sound_file, streaming=False)
        self.volume = volume
    def emit(self, record):
        self.sound.play().volume = self.volume

class TextHandler(logging.Handler):
    """This class allows you to log to a tkinter Text or ScrolledText widget"""
    def __init__(self, text):
        # run the regular Handler __init__
        logging.Handler.__init__(self)
        # Store a reference to the Text it will log to
        self.text = text
        self.text.tag_config("warning", foreground="orange")
        self.text.tag_config("error", foreground="red")
        self.text.tag_config("normal", foreground="black")

    def emit(self, record):
        msg = self.format(record)
        def append():
            self.text.configure(state='normal')
            if record.levelno == logging.WARNING:
                self.text.insert(tkinter.END, msg + '\n', ("warning"))
            elif record.levelno == logging.ERROR:
                self.text.insert(tkinter.END, msg + '\n', ("error"))
            else:
                self.text.insert(tkinter.END, msg + '\n', ("normal"))
            
            self.text.configure(state='disabled')
            # Autoscroll to the bottom
            self.text.yview(tkinter.END)
        # This is necessary because we can't modify the Text from other threads
        self.text.after(0, append)
log = logging.getLogger(__name__)

def dummy():
    log.info("This is an info")
    log.warning("This is a warning")
    log.error("This is an error")
