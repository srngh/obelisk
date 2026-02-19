# obelisk_file_handler.py
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


# from pathlib import Path

import yaml
# To Do:
# Demote this to a ObeliskConfigFileHandler

from ..widgets.ob_list_store import ObListStore, ob_list_store_constructor, ob_list_store_representer
from ..widgets.ob_tree_node import ObTreeNode, ob_tree_node_constructor, ob_tree_node_representer
from .connection_types.folder import Folder, folder_constructor, folder_representer
from .connection_types.item import Item, item_constructor, item_representer


class ObeliskFileHandler:
    # def __init__(self):
    # home_dir = Path.home()
    # self.filename = filename or (f"{home_dir}/.config/obelisk/obelisk_nested.yaml")
    def __init__(self, filename: str):
        self.filename = filename
        self.connections: dict

    # old, need to replace
    def load_connections(self):
        with open(self.filename) as file:
            self.connections = yaml.safe_load(file)

    def to_str(self):
        return self.connections

    # non-functional
    # def write(self, config):
    #     with open(self.filename, 'w') as file:
    #         yaml.dump(config, filename, default_flow_style=False)

    def load_config(self):
        with open(self.filename) as file:
            self.connections = yaml.load(file, Loader=get_loader())

    def write_config(self):
        with open(self.file_name, 'w') as file:
            yaml.dump(self.connections, file, sort_keys=False, Dumper=get_dumper())


def get_loader():
    loader = yaml.SafeLoader
    loader.add_constructor('!Folder', folder_constructor)
    loader.add_constructor('!Item', item_constructor)
    return loader


def get_dumper():
    safe_dumper = yaml.SafeDumper
    safe_dumper.add_representer(Folder, folder_representer)
    safe_dumper.add_representer(Item, item_representer)
    return safe_dumper


