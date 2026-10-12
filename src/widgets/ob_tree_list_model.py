# ob_tree_list_model.py
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

from gi.repository import Gtk

from dataclasses import dataclass

from .ob_tree_node import ObTreeNode
from .ob_list_store import ObListStore

@dataclass
class ObTreeModel:
    """
    This is just an intermediary class, since Gtk.TreeListModel can't be sublassed.
    """

    def __init__(self, active_stores=None, conn=None):
        self.active_stores=active_stores
        self.conn = conn

        self.root_store = self.get_children(parent_uuid=None, uuid='00000000-0000-0000-0000-000000000000')

        self.name_sorter = Gtk.StringSorter.new()
        self.name_sorter.set_expression(Gtk.PropertyExpression.new(ObTreeNode, None, 'name'))
        self.name_sorter.set_ignore_case(True)

        self.sorted_model = Gtk.SortListModel.new(
            model=self.root_store,
            sorter=self.name_sorter
        )

        self.tree_list_model = Gtk.TreeListModel.new(
            self.sorted_model,
            passthrough=False,
            autoexpand=False,
            create_func=self.create_child_model
        )


    def create_child_model(self, item):
        """
        The TreeModel create_func for working with an sqlite db.

        :param item: The item to run the create_func on.
        :type item: ObTreeNode
        """
        if item.is_folder:
            store = self.get_children(parent_uuid=item.uuid)
            if self.active_stores is not None:
                self.active_stores[item.uuid] = store

            return Gtk.SortListModel.new(model=store, sorter=self.name_sorter)
        return None

    def get_root_store(self):
        """
        Get the root store.
        """
        return self.root_store

    def get_children(self, parent_uuid=None, uuid=None):
        """
        Fetch all Connections belonging to parent_uuid.
        The uuid of the resulting Liststore can be passed.

        :param parent_uuid: The UUID of the items parent
        :type parent_uuid: str
        :param uuid: The root ListStores UUID
        :type uuid: str
        :return: An ObListStore containing all child Nodes
        :rtype: ObListStore
        """
        cursor = self.conn.cursor()

        parent_name = ''

        if parent_uuid is not None:
            cursor.execute('SELECT name FROM connections WHERE uuid = ?', (parent_uuid,))
            parent_name = cursor.fetchone()[0]

        if parent_uuid is None:
            # Items directly in the root
            cursor.execute('SELECT uuid, name, is_folder FROM connections WHERE parent_uuid IS NULL')
        else:
            cursor.execute(
                'SELECT uuid, name, is_folder FROM connections WHERE parent_uuid = ?',
                (parent_uuid,)
            )

        rows = cursor.fetchall()

        if uuid is not None:
            store = ObListStore(uuid=parent_uuid, name=parent_name)
        else:
            store = ObListStore(uuid=uuid, name=parent_name)

        for row in rows:
            store.append(ObTreeNode(uuid=row[0], name=row[1], is_folder=bool(row[2]), parent_uuid=parent_uuid))
        return store


