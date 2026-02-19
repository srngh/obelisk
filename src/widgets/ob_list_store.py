# ob_list_store.py
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

from gi.repository import GObject, Gio

import yaml

from .ob_tree_node import ObTreeNode


class ObListStore(Gio.ListStore):
    __gtype_name__ = 'ObListStore'

    """
    A ListStore for organizing the TreeListStore
    """

    def __init__(self, name: str, uuid: str):
        self._name = name
        self._uuid = uuid

        super().__init__()

    @GObject.Property(type=str)
    def name(self) -> str:
        return self._name

    @GObject.Property(type=str)
    def uuid(self) -> str:
        return self._uuid


def ob_list_store_representer(dumper: yaml.SafeDumper, ob_list_store: ObListStore) -> yaml.nodes.MappingNode:
    return dumper.represent_mapping('!Folder', {
        'name': ob_list_store.name,
        'uuid': ob_list_store.uuid,
        'connections': ob_list_store.connections,
  })


def ob_list_store_constructor(loader, node):
    values = loader.construct_mapping(node)
    return ObListStore(**values)
