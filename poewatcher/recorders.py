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
from . import config as c
from . import utils
from .utils import Map, MAP_MIN_LEVEL, MAP_MAX_LEVEL 
import os
import re
import time
import inspect
import pyperclip
import logging
import base64
loggerGen = logging.getLogger(__name__+".GenericRecorder")
loggerMap = logging.getLogger(__name__+".MapRecorder")
class GenericRecorder():
    """ Simple recorder who save to a .csv basic recording """
    def __init__(self, actions, separator, output_path, headers):
        
        self.output_path = output_path
        self.separator = separator
        self.headers = headers
        self.actions = []
        for pr in actions:
            self.actions.append((pr[1], getattr(self, pr[2])))
        if not os.path.isfile(output_path):
            open(output_path, "w+", encoding='utf8')
        with open(output_path, "r+", encoding='utf8') as file:
            if os.path.getsize(output_path) == 0:
                file.write(','.join(headers))
                file.write("\n")
                loggerGen.info("Created output csv file")
    def parse_message(self, msg, char_name):
        """ find matching keywords and start associated function """
        for abbr,func in self.actions:
            if msg.startswith(abbr):
                func(msg.replace(abbr,""), char_name)
    def add_loot(self, msg, char_name):
        info = [char_name, str(int(time.time()))]
        info += msg.split(self.separator)
        while len(info) < len(self.headers):
            info.append("")
        csv = ",".join(info)
        with open(self.output_path, "a", encoding='utf8') as file:
            file.write(csv)
            file.write("\n")
        loggerGen.info("GenericRecorder wrote : {0}".format(csv))
        
        

MAP_HEADERS = "timestamp,character,level,pack size,IIQ,boss,ambush,beyond,domination,magic,zana,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,notes,name,mods"
MAP_PREFIXES = ["Anarchic","Antagonist's","Armoured","Bipedal","Burning","Capricious","Ceremonial","Chaining","Demonic","Emanant",
"Fecund","Feral","Fleet","Freezing","Grounded","Hexproof","Incombustible","Mirrored","Molten","Multifarious","Otherworldly",
"Overlord's","Punishing","Savage","Shocking","Skeletal","Slithering","Splitting","Titan's","Twinned","Undead","Unwavering","Zana's", 
"Enraged", "Labyrinthine", "Massive", "Villainous" ]
MAP_SUFFIXES = ["of Balance","of Bloodlines","of Congealment","of Deadlines","of Desecration","of Elemental Weakness","of Endurance","of Enfeeblement","of Exposure","of Flames","of Frenzy","of Fracturing","of Giants","of Hemomancy","of Ice","of Insulation","of Lightning","of Power","of Smothering","of Stasis","of Temporal Chains","of Venom","of Vulnerability", "of Commanders", "of Hordes", "of Suffering", "of the Warlord"]

class MapRecorder():
    """ Manager who creates/destroy/edit new Map object based on user input 
    Also sends map data to a server
    """
    def __init__(self, actions, separator, output_path):
        self.actions = []
        for pr in actions:
            self.actions.append((pr[1], getattr(self, pr[2]))) 
        self.separator = separator
        self.output_path = output_path
        self.data = []
        self.last_map_mods = ""
        if not os.path.isfile(output_path):
            open(output_path, "w+", encoding='utf-8')
        with open(output_path, "r+", encoding='utf-8') as file:
            if os.path.getsize(output_path) == 0:
                file.write(MAP_HEADERS)
                file.write("\n")
                loggerMap.info("Created output csv file")
                
        
    def parse_message(self, msg, char_name):
        """ find matching keywords and start associated function """
        matches = []
        for abbr,func in self.actions:
            if msg.startswith(abbr):
                #We don't need to pass char_name to other function than add_map [still kinda ugly, will works on this to make it better]
                if len(inspect.getargspec(func)[0]) == 3:
                    func(msg.replace(abbr,""), char_name)
                else:
                    func(msg.replace(abbr, ""))


         
                
    def running(self):
        return len(self.data) > 0
        
                      
    def add_map(self, msg, char_name):
        """ Add a Map Object to self.data
        Can be done via input or clipboard data
        """
        #We get the information from the clipboard if the msg is empty
        if not msg:
            tmp = self.map_data_from_clipboard(msg, char_name)
        else:
            tmp = self.map_data_from_user_input(msg, char_name)
        #Ugly hack to avoid double error message (in case of wrong data in clipboard)
        if tmp.psize == -3:
            return
        if tmp.level < MAP_MIN_LEVEL or tmp.level > MAP_MAX_LEVEL:
            loggerMap.error("Tried to start map with a wrong level : {0}. Cancelling map start".format(tmp.level))
        else:
            self.data.append(tmp)
            loggerMap.info("Started {0}".format(tmp))        
        
    def map_data_from_clipboard(self, msg, char_name):
        """ Return a Map Object, try to use information in clipboard.
        Will not work with clipboard information not conform to PoE clipboard data
        """
        info = pyperclip.paste()
        if info == self.last_map_mods:
            loggerMap.warning("Starting a map with the same mods as before !")
        self.last_map_mods = info
        #Check if the clipboard data is actually a map
        if info.startswith("Rarity:") and "Travel to this Map by using it in the Eternal Laboratory" in info:
            lines = info.split("\n")
            name = ""
            if "Normal" in lines[0]: #normal maps have the name directly after rarity
                name = lines[1]
            if "Magic" in lines[0]: #We need to remove prefix + suffix
                name = lines[1]
                for affix in MAP_PREFIXES + MAP_SUFFIXES:
                    name = name.replace(affix, "")
            if "Rare" or "Unique" in lines[0]:#Rare/unique got their name between the Rarity: and the actual name
                name = lines[2]        
            name = name.replace(" Map","").strip() #Some cleanup
            if not name:
                loggerMap.warning("Couldn't get map name from clipboard data")
            #We store in b64 because of the many commas, \n and other stuff that can screw up the .csv
            #Also, directly decode bytes to string cause no point in storing bytes (we'll write them like every other stirngs)
            mods = base64.b64encode(bytes(info, 'utf-8')).decode("utf-8")
            regex_level = re.compile("Map Tier: \d{1,2}")
            regex_psize = re.compile("Monster Pack Size: \+\d{1,3}")
            regex_quantity = re.compile("Item Quantity: \+\d{1,3}")
            level = psize = quantity = 0
            magic = "more Magic Monsters" in info
            if regex_level.search(info):
                #Thanks to new map tier we don't directly have the level anymore in the clipboard data >.<
                level = int(regex_level.findall(info)[0].replace("Map Tier: ","")) + 67
            if regex_psize.search(info):
                psize = int(regex_psize.findall(info)[0].replace("Monster Pack Size: +",""))
            if regex_quantity.search(info):
                quantity = int(regex_quantity.findall(info)[0].replace("Item Quantity: +",""))  
            quantity += int(c.get("map_recorder", "additional_iiq"))
            tmp = Map.from_raw_data(char_name, level, psize, quantity, 
            boss=0, ambush=False, beyond=False, domination=False, magic=magic, zana=False, name=name, mods=mods)
            #tmp = {"character":char_name,"level":level, "psize":psize, "iiq":quantity, "ambush": False, "beyond": False,"domination": False,  "magic": magic, "zana" : False, "boss":0, "loot":[], "note":[], "name":name, "mods":mods}
            return tmp
        else:
            loggerMap.error("Trying to use clipboard data but couldn't find a map-like data in clipboard, aborting")
            tmp = Map({"level":0, "psize":-3}, {}, [])
            return tmp
            
            
    def map_data_from_user_input(self, msg, char_name):
        """ Return a Map Object based on user input 
        Check README for more information about the msg format
        """
        #We want lvl,psize,iiq,[mods]
        info = msg.split(self.separator)
        #In case of user input error, assume empty
        while len(info) < 4:
            info.append("")            
        #We remove all non-digit character
        for i in range(0,3):
            info[i] = ''.join(filter(lambda x: x.isdigit(), info[i]))
            info[i] = int(info[i]) if info[i].isdigit() else 0
        tmp = Map.from_raw_data(char_name, info[0], info[1], info[2], 
        boss=0, ambush=("a" in info[3]), beyond=("b" in info[3]), domination=("d" in info[3]), magic=("m" in info[3]), zana=("z" in info[3]), name="", mods="")
        return tmp

    def edit_map(self, msg):
        """ Edit last active Map. Uses map_data_from_user_input syntax.
        /!\ Erase old data if new corresponding data is inputed
        """
        tmp = self.map_data_from_user_input(msg, self.data[-1].character)
        info = msg.split(self.separator)
        log = "Edited map"
        if len(info) < 1:
            loggerMap.warning("Called edit_map without arguments")
            return
        #Update data if it exists
        if len(info) > 0:
            self.data[-1].update_level(tmp.level)
            log += ", with new level {0}".format(tmp.level)
        if len(info) > 1:
            self.data[-1].update_psize(tmp.psize)
            log += ", with new pack size {0}".format(tmp.psize)
        if len(info) > 2:
            self.data[-1].update_iiq(tmp.iiq)
            log += ", with new IIQ {0}".format(tmp.iiq)
        self.data[-1].update_mods(tmp.ambush, tmp.beyond, tmp.domination, tmp.magic, tmp.zana)
        if self.data[-1].zana:
            log +=", with Zana"
        if self.data[-1].ambush:
            log +=", with Ambush"
        if self.data[-1].domination:
            log +=", with Domination"
        if self.data[-1].magic:
            log +=", with magic monsters"            
            
        loggerMap.info(log)
    def edit_mods(self, msg):
        """ Edit last active map mods 
        /!\ Erase old values """
        ambush = "a" in msg
        beyond = "b" in msg
        domination = "d" in msg
        magic = "m" in msg
        zana = "z" in msg
        self.data[-1].update_mods(ambush,beyond,domination,magic,zana)
        log = "Added mods"
        if self.data[-1].zana:
            log +=" Zana"
        if self.data[-1].ambush:
            log +=", Ambush"
        if self.data[-1].domination:
            log +=", Domination"
        if self.data[-1].magic:
            log +=", magic monsters"      
        loggerMap.info(log)
        
    def update_name(self, msg):
        """ Replace last active Map name by msg """
        if len(self.data) > 0:
            if msg:
                self.data[-1]["name"] = msg
                loggerMap.info("Updating name to : {0}".format(msg))
            else:
                loggerMap.warning("Trying to update name with an empty name")
        else:
            loggerMap.error("Updating name with no active map")
    def add_loot(self, msg):
        """ Add map loot to the last active Map """
        if len(self.data) > 0:
            #Removing non-digit characte & cast everything to int
            info = [''.join(filter(lambda x: x.isdigit(), y)) for y in msg.split(self.separator)]
            info = [int(x) if x.isdigit() else 0 for x in info]
            if any(x < MAP_MIN_LEVEL or x > MAP_MAX_LEVEL for x in info):
                loggerMap.warning("Warning : logging invalid maps (level < {0} or > {1})".format(MAP_MIN_LEVEL, MAP_MAX_LEVEL))
            else:
                self.data[-1].add_loot(info)
                loggerMap.info("Adding loot : {0}".format(', '.join(str(x) for x in info)))
        else:
            loggerMap.error("adding loot with no active map")
            
            
    def add_note(self, msg):
        """Add a note to the last active Map """
        if len(self.data) > 0:
            self.data[-1].add_note(msg)
            loggerMap.info("Adding note : {0}".format(msg))
        else:
            loggerMap.error("adding note with no active map")


    def abort_map(self, msg):
        """ Remove last active Map without saving it"""
        if len(self.data) > 0:
            loggerMap.info("Removing last map")
            self.data = self.data[:-1]       
        else:
            loggerMap.error("aborting map with no active map")
            
    def end_map(self, msg):
        """Saves data to local file, optionally sends data to server """
        if len(self.data) > 0:
            boss = ''.join(filter(lambda x: x.isdigit(), msg))
            boss = int(boss) if boss else int(c.get("map_recorder","default_boss"))
            self.data[-1].update_boss(boss)
            csv = self.data[-1].to_csv()
            with open(self.output_path, "a", encoding='utf-8') as file_out:
                file_out.write(csv)
                file_out.write("\n")
            loggerMap.info("Map ended, i wrote : {0}".format(csv))
            if c.getboolean("map_recorder", "send_data"):
                self.send_map(self.data[-1])
            self.data = self.data[:-1]
        else:
            loggerMap.error("ending map with no active map")        
            
    def send_map(self, data):
        """Send a map object to server (using json) ; 
        If the server can't be reached, saves data to a separate file instead
        """
        csv = data.to_csv()
        response = utils.send_map_to_server(data)
        if "OK" in response:
            loggerMap.info("Server response : {0}".format(response))
        elif "FAIL" in response:
            #Invalid data sent
            loggerMap.error("Server response: {0}".format(response))
        else:
            #If server down, stores data to a local file
            loggerMap.error("Server response: {0}".format(response))
            output_path = "unsent_" + self.output_path
            if not os.path.isfile(output_path):
                open(output_path, "w+", encoding='utf-8')
            with open(output_path, "a", encoding='utf-8') as file:
                if os.path.getsize(output_path) == 0:
                    file.write(MAP_HEADERS)
                    file.write("\n")
                    loggerMap.info("Created output csv file for unsent data")
                file.write(csv)
                file.write("\n")
            loggerMap.info("Logged data to {0}, you can send them later by typing 'map:force_send'".format(output_path))
            
            
