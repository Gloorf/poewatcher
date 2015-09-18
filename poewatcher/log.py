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
logger = logging.getLogger(__name__)
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
""" Add a line to a ScrolledText
If the ScrolledText have a warning/error/normal tag, it will be used for nice formatting """        
def append(text, record, msg):
    text.configure(state='normal')
    if record.levelno == logging.WARNING:
        text.insert(tkinter.END, msg + '\n', ("warning"))
    elif record.levelno == logging.ERROR:
        text.insert(tkinter.END, msg + '\n', ("error"))
    else:
        text.insert(tkinter.END, msg + '\n', ("normal"))
    text.configure(state='disabled')
# Autoscroll to the bottom
    text.yview(tkinter.END)
                    
class ExtendedNotebookHandler(logging.Handler):
    """Logs to an ExtendedNotebook, putting every log in the first tab and creating a tab for each additional the log can come from
       TODO : abort creation of class if notebook is *not* an ExtendedNotebook """
    def __init__(self, notebook):
        logging.Handler.__init__(self)
        self.nb = notebook
            
    def emit(self, record):
        msg = self.format(record)
        selected = self.nb.find_tab_by_name(record.module)
        #If we don't have a tab, just create one
        
        if selected == -1:
            self.nb.add_tab(record.module)
            selected = len(self.nb.tabs) - 1
        
        # This is necessary because we can't modify the Text from other threads
        #Add information to the tabs + all tab (the 1st one)
        self.nb.tabs[selected].after(0, append(self.nb.tabs[selected], record, msg))
        self.nb.tabs[0].after(0, append(self.nb.tabs[0], record, msg))     
        
