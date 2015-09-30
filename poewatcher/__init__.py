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
__all__ = ['notifier', 'recorders', 'config', 'poe_handler', 'interfaces', 'log', "csv_manager"]


from .config import config
from . import utils
#Meh, really not sure of how i should do that
from .utils import windows, Map
from .log import SoundHandler, WarningFilter, TextHandler
from .notifier import Notifier
from .recorders import GenericRecorder, MapRecorder
from .poe_handler import PoeHandler
from .interfaces import Application
from .csv_manager import CsvManager
import logging
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())
