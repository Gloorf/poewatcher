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
import os
from . import config as c
import time
import socket
import json
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
#It is kinda ugly :( should fix that :P        
def dict_to_csv(data):
        out = "{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10}".format(int(time.time()), data["character"], data["level"], data["psize"], data["iiq"], data["boss"], data["ambush"], data["beyond"], data["domination"],data["magic"], data["zana"])
        for i in range(68,83):
            out += "," + str(data["loot"].count(i))
        out += ","
        out += '|'.join(data["note"])
        out += ",{0},{1}".format(data["name"], data["mods"])
        return out 
def dict_from_csv(line):
    data = line.split(',')
    loot = []
    for i in range(11,26):
        if int(data[i]) > 0:
            for i in range(int(data[i])):
                loot.append(i+67)
    tmp ={"timestamp":data[0], "character":data[1],"level":data[2], "psize":data[3], "iiq":data[4], "boss": data[5], "ambush": data[6], "beyond": data[7],"domination": data[8],  "magic": data[9],"zana" : data[10], "loot":loot }
    return tmp

def contact_server(data):
    # Create a socket (SOCK_STREAM means a TCP socket)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

     # Connect to server and send data
    sock.connect((c.get("map_recorder", "server_host"), int(c.get("map_recorder", "server_port"))))
    b = json.dumps(data).encode('utf-8')
    sock.sendall(b)

   # Receive data from the server and shut down
    received = str(sock.recv(1024), "utf-8")
    return format(received)    
    
    
