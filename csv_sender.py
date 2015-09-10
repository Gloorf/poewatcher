#!/usr/bin/python3
# -*- coding: utf8 -*-
import config as c
import util
"""
Use only once, to send a whole CSV file. Ignores first line (assumed to be headers)
"""
with open(c.map_output_path, "r") as file:
    file.readline() #Go past first line[headers]
    for line in file:
        k = util.contactserver(util.dict_from_csv(line))
