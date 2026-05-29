# ob_list_store.py
#
# Copyright 2026 simhof
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

from .ob_tree_node import ObTreeNode

class ObListStore(Gio.ListStore):
    __gtype_name__ = 'ObListStore'

    username: str
    address: str
    description: str
    protocol: str
    port: int
    auth: str

    """
    A ListStore for organizing the TreeListStore
    """

    def __init__(self, uuid: str, name: str):
        self._uuid = uuid
        self._name = name

        super().__init__(item_type=ObTreeNode)

    @GObject.Property(type=str)
    def name(self) -> str:
        return self._name

    @GObject.Property(type=str)
    def uuid(self) -> str:
        return self._uuid

