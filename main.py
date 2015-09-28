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
import logging.config
import time
import json
import tkinter
from poewatcher.log import SoundHandler, WarningFilter, TextHandler
from poewatcher import Application, windows, utils
from poewatcher import config as c
from poewatcher import MapRecorder, Notifier, GenericRecorder, PoeHandler, Application

## GUI init
root = tkinter.Tk()
#alpha sometimes doesn't work under some WM without that
root.wait_visibility(root)
root.wm_attributes('-alpha',float(c.get('gui_log_displayer', 'alpha')))
root.wm_attributes('-topmost', c.getboolean('gui_log_displayer', 'always_on_top'))
gui = Application(c.get_actions('gui_log_displayer'), c.getboolean("gui_log_displayer", "active"), master=root)
#Hide gui at start if needed
if not gui.isActive():
    root.withdraw()
## Script init
map_recorder = MapRecorder(c.get_actions("map_recorder"), c.get("global","separator"), c.get("map_recorder","output_path"))
notifier = Notifier(c.get_list("notifier","channels"), c.get("notifier","title"), c.get("notifier","icon_path"), windows)
generic_recorder = GenericRecorder(c.get_actions("generic_recorder"), c.get("global","separator"), c.get("generic_recorder","output_path"), c.get_list("generic_recorder","headers"))
poe_handler = PoeHandler( c.get_actions("handler"), c.get_list("global","usernames"), c.get("global","log_path"))

##Logging init 
# It's important that this come after GUI/config init because we use it in the logging
logging_options = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt":"%H:%M"
        }
    },
    "filters" : {
        "warning" : {
            "()":WarningFilter
            }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "stream": "ext://sys.stdout"
        },

        "file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "filename": "watch.log",
            "maxBytes": 10485760,
            "backupCount": 20,
            "encoding": "utf8"
        },
        "sound_error_handler": {
            "class": "poewatcher.log.SoundHandler",
            "level": "ERROR",
            "formatter": "simple",
            "sound_file": "extras/error.wav",
            "volume": float(c.get("global", "volume"))
       },
        "sound_warning_handler": {
            "class": "poewatcher.log.SoundHandler",
            "level": "WARNING",
            "filters": ["warning"],
            "formatter": "simple",
            "sound_file": "extras/warning.wav",
            "volume": float(c.get("global","volume"))
       },
       "gui_display_handler": {
            "class": "poewatcher.log.ExtendedNotebookHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "notebook": gui.nb
            }

    },

    "loggers": {
        "poewatcher": {
            "level": "DEBUG",
            "propagate": "yes"
        }
    },

    "root": {
        "level": "DEBUG",
        "handlers": ["console", "gui_display_handler", "file_handler", "sound_warning_handler", "sound_error_handler"]
    }
}
logging.config.dictConfig(logging_options)
logger = logging.getLogger(__name__)
logger.info("started watch_poe")


##Main loop
# We need to do like this because of tkinter (otherwise a while True: works well)
def loop():
    poe_handler.read_new_lines()
    for message in poe_handler.messages:
        if not utils.poe_active() and poe_handler.notifier:
            notifier.parse_message(message)
        stripped, name = poe_handler.strip_username(message)
        name = c.get("map_recorder","logged_username") if c.get("map_recorder","logged_username") else name
        if stripped:
            old_state = map_recorder.running()
            old_gui_state = gui.isActive()
            map_recorder.parse_message(stripped, name)
            generic_recorder.parse_message(stripped, name)
            poe_handler.parse_message(stripped)
            gui.parse_message(stripped)
            state = map_recorder.running()
            #Interactive hiding ;)
            if old_gui_state != gui.isActive():
                if gui.isActive():
                    root.update()
                    root.deiconify()
                else:
                    root.withdraw()
            #Change of stat (either map started/map ended)
            if c.getboolean("handler","offline_while_maps") and state != old_state:
                if state:
                    poe_handler.poetrade_off()
                else:
                    poe_handler.poetrade_on()
    
    poe_handler.messages.clear()
    root.after(1000, loop)
try:

    root.after(1000, loop)
    root.mainloop()

            

            
except KeyboardInterrupt:
    logger.info("Stopping watch_poe")


