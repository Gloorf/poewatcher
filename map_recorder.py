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
from config import config as c
import os
import time
import inspect
import util
from log import logger
headers ="timestamp,character,level,pack size,IIQ,boss,ambush,beyond,domination,magic,zana,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,notes"

class MapRecorder():
    def __init__(self, actions, separator, output_path):
        self.actions = []
        for pr in actions:
            self.actions.append((pr[1], getattr(self, pr[2]))) 
        self.separator = separator
        self.output_path = output_path
        self.data = []
        if not os.path.isfile(output_path):
            open(output_path, "w+", encoding='utf-8')
        with open(output_path, "r+", encoding='utf-8') as file:
            if os.path.getsize(output_path) == 0:
                file.write(headers)
                file.write("\n")
                logger.info("Created output csv file for MapRecorder")
                
        
    def parse_message(self, msg, char_name):
        for abbr,func in self.actions:
            if abbr in msg:
                #We don't need to pass char_name to other function than add_map [still kinda ugly, will works on this to make it better]
                if len(inspect.getargspec(func)[0]) == 3:
                    func(msg.replace(abbr,""), char_name)
                else:
                    func(msg.replace(abbr, ""))


         
                
    def running(self):
        return len(self.data) > 0
        
                      
    def add_map(self, msg, char_name):
        info = msg.split(self.separator)
        #In case of user input error, assume empty
        while len(info) < 4:
            info.append("")            
        tmp={"character":char_name,"level":0, "psize":0, "iiq":0, "ambush": ("a" in info[3]), "beyond": ("b" in info[3]),"domination": ("d" in info[3]),  "magic": ("m" in info[3]),"zana" : ("z" in info[3]), "boss":0, "loot":[], "note":[]}
        #We remove all non-digit character
        for i in range(0,3):
            info[i] = ''.join(filter(lambda x: x.isdigit(), info[i]))
            info[i] = info[i] if info[i] else 0
        tmp["level"] = info[0]
        tmp["psize"] = info[1]
        tmp["iiq"] = info[2]
        self.data.append(tmp)
        logger.info("Started map, with level = {0}, psize = {1}, iiq = {2}, ambush = {5}, beyond = {3}, domination = {4}, magic = {6}, zana = {7}".format(tmp["level"], tmp["psize"], tmp["iiq"], tmp["beyond"], tmp["domination"], tmp["ambush"], tmp["magic"], tmp["zana"]))
        
        
    def add_loot(self, msg):
        if len(self.data) > 0:
            info = [int(''.join(filter(lambda x: x.isdigit(), y))) for y in msg.split(self.separator)]
            self.data[-1]["loot"] += info
            logger.info("Adding loot : {0}".format(', '.join(str(x) for x in info)))
        else:
            logger.error("adding loot with no active map")
            
            
    def add_note(self, msg):
        if len(self.data) > 0:
            #Remove the comma to not break the .csv
            self.data[-1]["note"].append(msg.replace(",",""))
            logger.info("Adding note : {0}".format(msg))
        else:
            logger.error("ERR: adding note with no active map")


    def abort_map(self, msg):
        if len(self.data) > 0:
            logger.info("Removing last map")
            self.data = self.data[:-1]       
        else:
            logger.error("ERR: aborting map with no active map")
            
    def end_map(self, msg):
        if len(self.data) > 0:
            self.data[-1]["boss"] = ''.join(filter(lambda x: x.isdigit(), msg))
            self.data[-1]["boss"] = self.data[-1]["boss"] if self.data[-1]["boss"] else c.get("map_recorder","default_boss")
            output = util.dict_to_csv(self.data[-1])
            with open(self.output_path, "a", encoding='utf-8') as file_out:
                file_out.write(output)
                file_out.write("\n")
            logger.info("Map ended, i wrote : {0}".format(output))
            if c.getboolean("map_recorder", "send_data"):
                self.data[-1]["timestamp"] = int(time.time())
                self.data[-1]["username"] = self.data[-1]["character"] if c.getboolean("map_recorder", "send_data") else "anonymous"
                response = util.contact_server(self.data[-1])
                if "OK" in response:
                    logger.info("Server response: {0}".format(response))
                else:
                    logger.error("Server response: {0}".format(response))
            self.data = self.data[:-1]
        else:
            logger.error("ERR: ending map with no active map")
