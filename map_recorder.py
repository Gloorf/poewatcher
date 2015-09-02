#!/usr/bin/python3
# -*- coding: utf8 -*-
from collections import OrderedDict
from config import default_boss
import os  
headers ="level,pack size,IIQ,boss,beyond,magic,zana,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,notes"
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
                
        
    def parse_message(self, msg):
        for abbr,func in self.actions:
            if abbr in msg:
                func(msg.replace(abbr, ""))
    
                
    def to_csv(self, data):
        out = str(data["level"]) + "," + str(data["psize"]) + "," + str(data["iiq"]) + "," + str(data["boss"]) + "," + str(data["beyond"]) + "," + str(data["magic"]) + "," + str(data["zana"])
        for i in range(68,83):
            out += "," + str(data["loot"].count(i))
        out += ","
        out += '|'.join(data["note"])
        return out          
                
              
    def add_map(self, msg):
        info = msg.split(self.separator)
        #In case of user input error, assume empty
        while len(info) < 4:
            info.append("")            
        tmp=OrderedDict({"level":0, "psize":0, "iiq":0, "beyond": ("b" in info[3]),"magic": ("m" in info[3]),"zana" : ("z" in info[3]), "boss":0, "loot":[], "note":[]})
        #We remove all non-digit character
        for i in range(0,3):
            info[i] = ''.join(filter(lambda x: x.isdigit(), info[i]))
            info[i] = info[i] if info[i] else 0
        tmp["level"] = info[0]
        tmp["psize"] = info[1]
        tmp["iiq"] = info[2]
        self.data.append(tmp)
        print("Started map, with level = {0}, psize = {1}, iiq = {2}, beyond = {3}, magic = {4}, zana = {5}".format(tmp["level"], tmp["psize"], tmp["iiq"], tmp["beyond"], tmp["magic"], tmp["zana"]))
        
        
    def add_loot(self, msg):
        if len(self.data) > 0:
            info = [''.join(filter(lambda x: x.isdigit(), y)) for y in msg.split(self.separator)]
            self.data[-1]["loot"] += info
            print("Adding loot : {0}".format(', '.join(info)))
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
            #We assume 1 boss killed (an option on this could be nice)
            self.data[-1]["boss"] = self.data[-1]["boss"] if self.data[-1]["boss"] else default_boss
            output = self.to_csv(self.data[-1])
            with open(self.output_path, "a") as file_out:
                file_out.write(output)
                file_out.write("\n")
            print("Map ended, i wrote : {0}".format(output))
            self.data = self.data[:-1]
        else:
            print("ERR: ending map with no active map")
