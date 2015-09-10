#!/usr/bin/python3
# -*- coding: utf8 -*-
#Copyright (C) 2015 Guillaume DUPUY <glorf@glorf.fr>
#This file is part of Watch Poe.

#Watch PoE is free software: you can redistribute it and/or modify
#it under the terms of the GNU Affero General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#Watch PoE is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU Affero General Public License for more details.

#You should have received a copy of the GNU Affero General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>
import re
import time
import requests
from watchdog.events import FileSystemEventHandler
import config as c

class PoeHandler(FileSystemEventHandler):
    def __init__(self, usernames, actions, log_path):
        self.usernames = usernames
        self.notifier = c.notifier_on
        self.actions = []
        self.messages = []
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
                #We store the message and process them later (in the main loop)
                if message:
                    self.messages.append(message)
                    for abbr, func in self.actions:
                        if abbr in message:
                            func()
                            
                            
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
