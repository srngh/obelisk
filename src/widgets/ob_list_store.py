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


class ObListStore(Gio.ListStore):
    __gtype_name__ = 'ObListStore'

    username: str
    ip4_address: str
    ip6_address: str
    description: str
    protocol: str
    port: int
    auth: str

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

    def get_position(self, node):
        for index in range(self.get_n_items()):
            print(node.uuid, self.get_item(index).uuid)
            if node.uuid == self.get_item(index).uuid:
                return index

