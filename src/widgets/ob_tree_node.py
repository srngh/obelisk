# ob_tree_node.py
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


class ObTreeNode(GObject.GObject):
    __gtype_name__ = 'ObTreeNode'

    username: str = ''
    ip4_address: str
    description: str = ''
    protocol: str = 'ssh'
    port: int = 22
    auth: str = ''

    def __init__(self, name: str, uuid: str, is_folder=False):
        super().__init__()
        self._name = name
        self._uuid = uuid
        self.is_folder = is_folder
        self.children = Gio.ListStore.new(ObTreeNode) if is_folder else None

    @GObject.Property(type=str)
    def name(self) -> str:
        return self._name

    @GObject.Property(type=str)
    def uuid(self) -> str:
        return self._uuid

    def __repr__(self):
        return f'{self.name}, {self.uuid}'

    def add_child(self, child_node):
        if self.children is not None:
            self.children.append(child_node)
