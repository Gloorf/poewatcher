#!/usr/bin/python3
# -*- coding: utf8 -*-
import re
import time
import os
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
    def __init__(self, usernames, log_path):
        self.usernames = usernames
        self.notifier = True
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
                    if "notifier on:" in message:
                        self.notifier = True
                    if "notifier off:" in message:
                        self.notifier = False
                    if not poe_active() and self.notifier:
                        notifier.parse_message(message)
                    stripped, name = self.strip_username(message)
                    if stripped:
                        map_recorder.parse_message(stripped, name)
                        generic_recorder.parse_message(self.strip_username(message))
                         


map_recorder = MapRecorder(c.map_actions, c.separator, c.map_output_path)
notifier = Notifier(c.notifier_channels, c.notifier_title, c.notifier_icon_path, windows)
generic_recorder = GenericRecorder(c.generic_actions, c.separator, c.generic_output_path, c.generic_headers)
event_handler = PoeHandler(c.usernames, c.log_path)
observer = Observer()
observer.schedule(event_handler, c.log_path, recursive=False)
observer.start()
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()


