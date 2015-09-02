#!/usr/bin/python3
# -*- coding: utf8 -*-
from collections import OrderedDict
import os
class GenericRecorder():
    def __init__(self, actions, separator, output_path, headers):
        
        self.output_path = output_path
        self.separator = separator
        self.headers = headers
        self.actions = []
        for pr in actions:
            self.actions.append((pr[1], getattr(self, pr[2])))
        if not os.path.isfile(output_path):
            open(output_path, "w+")
        with open(output_path, "r+") as file:
            if os.path.getsize(output_path) == 0:
                file.write(','.join(headers))
                file.write("\n")
                print("Created output csv file for GenericRecorder")
    def parse_message(self, msg):
        for abbr,func in self.actions:
            if abbr in msg:
                func(msg.replace(abbr,""))
    def add_loot(self, msg):
        info = msg.split(self.separator)
        while len(info) < len(self.headers):
            info.append("")
        csv = ",".join(info)
        with open(self.output_path, "a") as file:
            file.write(csv)
            file.write("\n")
        print("GenericRecorder wrote : {0}".format(csv))
