# Overview
A python script for Path Of Exile controlled by in game text input (it scans the Client.txt file).

#Installation

  You will need python3 and [watchdog](https://pypi.python.org/pypi/infi.watchdog/0.6.3). watchdog can be easily installed using pip.
  
# Features

* Whisper (and others channels if you want) notifier. Uses notify-send. This is primarily done for Linux, but it works on windows using [notify-send](http://vaskovsky.net/notify-send/).
* Map recorder. Simplifies recording map by avoiding you to alt-tab every time you want to write it down. It scans only local channel, and message by you. An example of a map recording :
```
ms:75,14,134,m #Map level 75, 14 pack size, 134 IIQ, with magic monsters.
ml:76 #Got a level 76 map
ml:78,75 #You can input multiple maps
mn:loot mjolner #You can add as much notes as you want
me:1 # You killed 1 boss on this maps
```
* map start : (keyword)map_level,map_packsize,map_iiq[,bmz]. The last is optional, and you can use 1, 2 or 3 of them. "b" is for Beyond mod, "m" is for magic monsters, "z" for zana.
* map loot : (keyword)map_level[,map_n_level...]. Pretty straightforward
* map note : (keyword)note. The note can be any size, comma will be removed though (to avoid breaking the .csv) ; multiples notes will be separated by a "|"
* map end : (keyword)[boss_killed]. You can omit boss_killed, in this case the default value in config.py will be used

The keywords and separator(default is ",") can be changed in config.py.

*Generic recorder. This can works with any finite numbers of value you want to record. An example (suited for MF run on dominus/voll for example) is used here ; simply changes the "generic_headers" in config.py
