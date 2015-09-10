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
from collections import OrderedDict
from config import default_boss
import os
import time
import inspect
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
            open(output_path, "w+")
        with open(output_path, "r+") as file:
            if os.path.getsize(output_path) == 0:
                file.write(headers)
                file.write("\n")
                print("Created output csv file for MapRecorder")
                
        
    def parse_message(self, msg, char_name):
        for abbr,func in self.actions:
            if abbr in msg:
                #We don't need to pass char_name to other function than add_map [still kinda ugly, will works on this to make it better]
                if len(inspect.getargspec(func)[0]) == 3:
                    func(msg.replace(abbr,""), char_name)
                else:
                    func(msg.replace(abbr, ""))


    def to_csv(self, data):
        out = "{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10}".format(int(time.time()), data["character"], data["level"], data["psize"], data["iiq"], data["boss"], data["ambush"], data["beyond"], data["domination"],data["magic"], data["zana"])
        for i in range(68,83):
            out += "," + str(data["loot"].count(i))
        out += ","
        out += '|'.join(data["note"])
        return out          
                
    def running(self):
        return len(self.data) > 0
        
                      
    def add_map(self, msg, char_name):
        info = msg.split(self.separator)
        #In case of user input error, assume empty
        while len(info) < 4:
            info.append("")            
        tmp=OrderedDict({"character":char_name,"level":0, "psize":0, "iiq":0, "ambush": ("a" in info[3]), "beyond": ("b" in info[3]),"domination": ("d" in info[3]),  "magic": ("m" in info[3]),"zana" : ("z" in info[3]), "boss":0, "loot":[], "note":[]})
        #We remove all non-digit character
        for i in range(0,3):
            info[i] = ''.join(filter(lambda x: x.isdigit(), info[i]))
            info[i] = info[i] if info[i] else 0
        tmp["level"] = info[0]
        tmp["psize"] = info[1]
        tmp["iiq"] = info[2]
        self.data.append(tmp)
        print("Started map, with level = {0}, psize = {1}, iiq = {2}, ambush = {5}, beyond = {3}, domination = {4}, magic = {6}, zana = {7}".format(tmp["level"], tmp["psize"], tmp["iiq"], tmp["beyond"], tmp["domination"], tmp["ambush"], tmp["magic"], tmp["zana"]))
        
        
    def add_loot(self, msg):
        if len(self.data) > 0:
            info = [int(''.join(filter(lambda x: x.isdigit(), y))) for y in msg.split(self.separator)]
            self.data[-1]["loot"] += info
            print("Adding loot : {0}".format(', '.join(str(x) for x in info)))
        else:
            print("ERR: adding loot with no active map")
            
            
    def add_note(self, msg):
        if len(self.data) > 0:
            #Remove the comma to not break the .csv
            self.data[-1]["note"].append(msg.replace(",",""))
            print("Adding note : {0}".format(msg))
        else:
            print("ERR: adding note with no active map")
            
            
    def end_map(self, msg):
        if len(self.data) > 0:
            self.data[-1]["boss"] = ''.join(filter(lambda x: x.isdigit(), msg))
            self.data[-1]["boss"] = self.data[-1]["boss"] if self.data[-1]["boss"] else default_boss
            output = self.to_csv(self.data[-1])
            with open(self.output_path, "a") as file_out:
                file_out.write(output)
                file_out.write("\n")
            print("Map ended, i wrote : {0}".format(output))
            self.data = self.data[:-1]
        else:
            print("ERR: ending map with no active map")
