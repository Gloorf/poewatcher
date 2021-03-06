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
import ast
from collections import OrderedDict
import logging
logger = logging.getLogger(__name__)
MAP_MIN_LEVEL = 66
MAP_MAX_LEVEL = 82
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
def create_loot():
    """Return an orderedDict (for easy iterations) with [[68,82]] as keys, 0 as value """
    out = OrderedDict()
    for i in range(68, 83):
        out[i] = 0
    return out
def dict_to_tackle_csv(data):
    zana_mod = 1 if (data["ambush"] or data["domination"]) else ""
    #First Lvl, IIQ, psize, kill, instance crash, Zana mission, Zana mod
    output = "{0},{1},{2},{3},{4},{5},{6}".format(data["level"],data["iiq"],data["psize"],data["boss"],"",(1 if data["zana"] else ""), zana_mod)
    #Second data from 82 to 68
    for i in range(82,67,-1):
        output += "," + str(data["loot"].count(i))
    return output
     
def send_map_to_server(data):
    """ Send a json string to the server """
    # Create a socket (SOCK_STREAM means a TCP socket)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
         # Connect to server and send data
        sock.connect((c.get("map_recorder", "server_host"), int(c.get("map_recorder", "server_port"))))
        #This way the server candifferentiate "old" and "new" way to send data
        data.is_obj = True
        b = data.to_json().encode('utf-8')
        sock.sendall(b)
       # Receive data from the server and shut down
        received = str(sock.recv(1024), "utf-8")
        return format(received)
    except Exception as e:
        return format(e)       
class Map(object):
    """Hold a map (currently being recorded/runned or not).
    Can be initialised :
    * from raw data (based on user input)
    * from csv (when loading from a file)
    * from json (when transmitted over netwokr)
    * from dict, if you want
    """
    ## Import / Export methods
    def __init__(self, data, loot, notes):
        for key, value in data.items():
            setattr(self, key, value)
        if loot:
            self.loot = loot
        else:
            self.loot = create_loot()
        self.notes = notes
    @classmethod
    def from_raw_data(cls, character_name, level, psize, iiq, boss=0, ambush=False, beyond=False, domination=False, magic=False, zana=False, name="", mods="", loot = {}, notes = []):
        """Takes a lot of parameters and return a map """
        data = {"timestamp":int(time.time()), "character":character_name, "level": level, "psize":psize, "iiq":iiq, "boss":boss, #Mandatory part
                "ambush":ambush, "beyond":beyond, "domination":domination, "magic":magic, "zana":zana, #ZSpecial map mods
                "name":name, "mods":mods}
        m = cls(data, loot, notes)
        return m
    @classmethod
    def from_csv(cls, raw_csv):
        """Takes a csv line (no headers !) and return a Map"""
        info = raw_csv.rstrip().split(',')
        #That's not so great error handling but w/e
        if len(info) < 27:
            print("CSV is too little, big problem !!")
            return
        #Legacy handling
        if len(info) < 29:
            info.append("")
            info.append("")
        data = {"timestamp":info[0], "character":info[1],"level":info[2], "psize":info[3], "iiq":info[4], "boss": info[5], "ambush": ast.literal_eval(info[6]), "beyond": ast.literal_eval(info[7]),"domination": ast.literal_eval(info[8]),  "magic": ast.literal_eval(info[9]),"zana" : ast.literal_eval(info[10]), "name":info[27], "mods":info[28]}
        loot = create_loot()
        for i in range(11, 26):
            if int(info[i]) > 0:
                loot[i+57]=int(info[i])
        notes = info[26].split('|')
        m = cls(data, loot, notes)
        return m
    @classmethod
    def from_json(cls, raw_json):
        """Takes a json string (not binary !) and return a Map"""
        data = json.loads(raw_json)
        #Json does not allow integer key, so our loot keys are cast to str during transfer
        int_loot = {int(k):v for k,v in data["loot"].items()}
        loot = OrderedDict(sorted(int_loot.items(), key=lambda t: t[0]))
        notes = data["notes"]
        data.pop("loot", None)
        data.pop("notes", None)
        m1 = Map(data, loot, notes)
        return m1
    def to_json(self):
        """Return a json string (not binary !) containing the map """
        # See http://stackoverflow.com/questions/3768895/python-how-to-make-a-class-json-serializable
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
        pass
    def to_csv(self):
        """Return a line in a CSV file"""
        #Still ugly, need to fix it :P
        out = "{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10}".format(self.timestamp, self.character, self.level, self.psize, self.iiq, self.boss, self.ambush, self.beyond, self.domination,self.magic, self.zana)
        for i in range(68,83):
            out += "," + str(self.loot[i])
        out += ","
        out += '|'.join(self.notes)
        out += ",{0},{1}".format(self.name, self.mods)
        return out
    def to_tackle_csv(self):
        """Return a line in a CSV file, tackle's 70 format"""
        zana_mod = 1 if (self.ambush or self.domination) else ""
        #First Lvl, IIQ, psize, kill, instance crash, Zana mission, Zana mod
        output = "{0},{1},{2},{3},{4},{5},{6}".format(self.level,self.iiq,self.psize,self.boss,"",(1 if self.zana else ""), zana_mod)
        #Second data from 82 to 68
        for i in range(82,67,-1):
            output += "," + str(self.loot[i])
        return output
    ## Functions that does stuff
    def add_loot(self, loot):
        """ Add loot, either a single int or a list of int """
        if isinstance(loot, int):
            loot = [loot]
        for l in loot:
            self.loot[l] += 1
        
    def add_note(self, note):
        """ Add note ; remove comma to avoid breaking  the .csv"""
        self.notes.append(note.replace(",",""))
    def update_name(self, name):
        """ Replace old map name with new map name (if not empty)"""
        if name:
            self.name = name
    def update_boss(self, boss):
        """ Update number of boss"""
        self.boss = boss
    def update_iiq(self, value):
        """ Update IIQ """
        if value < 0:
            logger.warning("Tried to set an IIQ < 0, aborting")
        else:
            self.iiq = value
    def update_level(self, value):
        """ Update Level"""
        if value < MAP_MIN_LEVEL or value > MAP_MAX_LEVEL:
            logger.warning("Tried to set a level < {0} or > {0}, aborting".format(MAP_MIN_LEVEL, MAP_MAX_LEVEL))
        else:
            self.level = value
    def update_psize(self, value):
        """ Update pack size """
        if value < 0:
            logger.warning("Tried to set a psize < 0, aborting")
        else:
            self.psize = value
    def update_mods(self, ambush, beyond, domination, magic, zana):
        """ Update all mods ; must be boolean !"""
        self.ambush = ambush
        self.beyond = beyond
        self.domination = domination
        self.magic = magic
        self.zana = zana
    ## I love magic methods
    def __str__(self):
        s = "{8} map, with level = {0}, psize = {1}, iiq = {2}, ambush = {5}, beyond = {3}, domination = {4}, magic = {6}, zana = {7}".format(self.level, self.psize, self.iiq, self.beyond, self.domination, self.ambush, self.magic, self.zana, self.name)
        return s
        