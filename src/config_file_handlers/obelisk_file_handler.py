# obelisk_loader.py
#
# Copyright 2025 simhof
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import yaml
from pathlib import Path

# To Do:
# Demote this to a ObeliskConfigFileHandler

class ObeliskFileHandler:
    def __init__(self):
        home_dir = Path.home()
        #self.filename = filename or (f"{home_dir}/.config/obelisk/obelisk_nested.yaml")


    def load_connections(self, filename):
        with open(filename) as file:
            self.connections = yaml.safe_load(file)


    def to_str(self):
        return self.connections

# To Do:
# write changes to file

### To be deleted
'''
    def to_conf(self):
        return parse_config(self.connections)

def parse_config(connections: dict):
    list_items = []
    for item in connections:
        match connections[item]['item_type']:
            case 'connection':
                connection_item = Item(connections[item]['item_title'])
                connection_item.ip4_address = connections[item]['ip4_address']
                connection_item.user = connections[item]['user']
                connection_item.user = connections[item]['item_description']
                connection_item.protocol = connections[item]['protocol']
                connection_item.auth = connections[item]['auth']
                list_items.append(connection_item)
            case 'folder':
                sub_items = connections[item]['connections']
                folder_item = Item(connections[item]['item_title'], children=parse_config(sub_items))
                list_items.append(folder_item)
    return list_items

class Item:
    def __init__(self, title, children=None):
        self.title = title
        self.children = children or []

    def __repr__(self):
        return f'{self.title}'
'''
