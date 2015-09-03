#!/usr/bin/python3
# -*- coding: utf8 -*-
#Copyright (C) 2015 Guillaume DUPUY <glorf@glorf.fr>
#This file is part of Watch Poe.

#Watch PoE is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#Watch PoE is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>
import re
import time
import os
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from map_recorder import * 
from notifier import *
from generic_recorder import *
import config as c
if os.name == "nt":
    windows = True
    import subprocess
    from win32gui import GetWindowText, GetForegroundWindow
else:
    windows = False
    from subprocess import PIPE, Popen
def active_window_title():
    title = ""
    if windows:
        title = GetWindowText(GetForegroundWindow())
    else:
    #I know it's complicated compared to windows, but it should work with any WM :)
        root = Popen(['xprop', '-root'],  stdout=PIPE)
        for i in root.stdout:
            if "_NET_ACTIVE_WINDOW(WINDOW):" in str(i):
                id_ = i.split()[4]
                id_w = Popen(['xprop', '-id', id_], stdout=PIPE)
        for j in id_w.stdout:
            if 'WM_ICON_NAME(STRING)' in str(j):
                #We remove the last 3 character who are "\n'" (\ and n as normal character, not an actual linebreak, strange behaviour here)
                title = str(j).split("WM_ICON_NAME(STRING) = ")[1].replace('"', '')[:-3]
    return title
def poe_active():
    if active_window_title() == "Path of Exile" or active_window_title() == "Default - Wine desktop":
        return True
    else:
        return False
class PoeHandler(FileSystemEventHandler):
    def __init__(self, usernames, actions, log_path):
        self.usernames = usernames
        self.notifier = c.notifier_on
        self.actions = []
        for pr in actions:
            self.actions.append((pr[1], getattr(self, pr[2])))
        self.file = open(log_path + "Client.txt", "r")
        first = self.file.readline() #Read the first line
        for last in self.file: pass #Loop through the whole file (place us at the end of file)

    def find_message(self, line):
        regex_msg = re.compile("\[INFO Client \d+\] (.*)")
        if regex_msg.search(line):
            return regex_msg.findall(line)[0]
        return ""
    def strip_username(self, line):
        for name in self.usernames:
            if name + ": " in line:
                return (line.replace(name + ": ", ""), name)
        return ("", "")
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith("Client.txt"):
            for line in self.file:
                message = self.find_message(line)
                if message:
                    for abbr, func in self.actions:
                        if abbr in message:
                            func()
                    if not poe_active() and self.notifier:
                        notifier.parse_message(message)
                    stripped, name = self.strip_username(message)
                    name = c.logged_username if c.logged_username else name
                    if stripped:
                        map_recorder.parse_message(stripped, name)
                        generic_recorder.parse_message(self.strip_username(message))
    def notifier_off(self):
        print("Turning off notifier")
        self.notifier = False
    def notifier_on(self):
        print("Turning on notifier")
        self.notifier = True
    def poetrade_off(self):
        print("Turning offline poe.trade")
        requests.post(c.poetrade_url + "/offline")
    def poetrade_on(self):
        print("Turning online poe.trade")
        requests.post(c.poetrade_url)

map_recorder = MapRecorder(c.map_actions, c.separator, c.map_output_path)
notifier = Notifier(c.notifier_channels, c.notifier_title, c.notifier_icon_path, windows)
generic_recorder = GenericRecorder(c.generic_actions, c.separator, c.generic_output_path, c.generic_headers)
poe_handler = PoeHandler(c.usernames, c.handler_actions, c.log_path)
observer = Observer()
observer.schedule(poe_handler, c.log_path, recursive=False)
observer.start()
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()


