# ob_config.py
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

import os
import sqlite3
from pathlib import Path
from uuid import uuid4

from gi.repository import GObject, Gio, Gtk

from .db_handler.obelisk_db_handler import ObeliskDBHandler
from .db_handler.generic_node import Node
from .widgets.ob_tree_list_model import ObTreeModel
from .widgets.ob_list_store import ObListStore
from .widgets.ob_tree_node import ObTreeNode


class ObDBConfig(GObject.Object, Gio.ListModel):
    __gtype_name__ = 'ObDBConfig'
    """
    This class holds the configuration of a loaded config file.
    """

    def __init__(self, db_handler: ObeliskDBHandler = None, **kwargs):
        super().__init__(**kwargs)
        self.autosave = False
        self.db_handler = db_handler
        self.config_type = 'obelisk'
        self.initialize_config_path()

        self.active_stores = {}

        self.tree_model = ObTreeModel(active_stores=self.active_stores, conn=self.db_handler.conn)

        self.tree_list_model = self.tree_model.tree_list_model

        # self.root_store = self.get_children(parent_uuid=None, uuid='00000000-0000-0000-0000-000000000000')

        # self.tree_list_model = Gtk.TreeListModel.new(
        #     self.root_store,
        #     passthrough=False,
        #     autoexpand=False,
        #     create_func=self.create_child_model
        # )
        self.selection_model = Gtk.SingleSelection(model=self.tree_list_model)

    def save(self):
        """
        Write the current configuration to file
        """
        # add a cleanup method to remove orphaned auth entries
        self.db_handler.conn.commit()

    # probably obsolete
    def prepare_model_for_write(self):
        """
        Transform the TreeListModel to a data structure that can be parsed
        by the yaml dumper for writing to file.
        """
        list_store = self.ob_list_store_model
        connections = self.prepare_sub_tree(list_store)
        self.default_handler.connections = connections

    def drop_item(self, tree_node, folder):
        """
        Callback for drag and drop.

        :param node: The node to add to the model
        :type node: ObTreeNode
        :param folder: The folder node where the new node will be appended to
        :type folder: ObTreeNode
        """
        node = self.db_handler.get_item_data(node_uuid=tree_node.uuid)

        if folder.uuid == '00000000-0000-0000-0000-000000000000':
            self.ob_list_store_model.append(tree_node)
            node.parent_uuid = None
            self.db_handler.save_node_to_db(node)
        else:
            node.parent_uuid = folder.uuid
            self.db_handler.save_node_to_db(node)

    def add_item(self, node, auth):
        """
        Add a node and auth object to the database.

        :param node: The node to add to the model
        :type node: ObTreeNode
        :param folder: The folder node where the new node will be appended to
        :type folder: ObTreeNode
        """

        self.db_handler.conn.execute("BEGIN TRANSACTION;")
        self.db_handler.save_node_to_db(node)
        self.db_handler.save_auth_to_db(auth)

        try:
            self.db_handler.conn.commit()
        except sqlite3.Error as e:
            print("Could not save node and auth:", e)
            self.db_handler.conn.rollback()


    def remove_item(self, tree_node):
        """
        Pass an ObTreeNode which should be removed from the config.
        If the TreeNode is a folder, all child items are removed as well.

        :param node: The node that should be removed from the model.
        :type node: ObTreeNode
        """
        cursor = self.db_handler.conn.cursor()

        node = self.db_handler.get_item_data(tree_node.uuid)

        self.db_handler.conn.execute("BEGIN TRANSACTION;")
        cursor.execute('DELETE FROM connections WHERE uuid = ?', (node.uuid,))
        cursor.execute('DELETE FROM authentication WHERE auth_uuid = ?', (node.auth_uuid,))

        try:
            self.db_handler.conn.commit()
        except sqlite3.Error as e:
            print("Could not remove node and auth:", e)
            self.db_handler.conn.rollback()

    def clone_item(self, tree_node):
        """
        Callback for <Ctrl>c shortcut
        """
        pass

    def recursive_copy_func(self, old_parent_uuid='', new_parent_uuid=''):
        """
        Iterates over all nodes which are children of the copied folder.
        Creates a copy of all children and linked auth objects.

        :param old_parent_uuid: The uuid of the copied node
        :type old_parent_uuid: str
        :param new_parent_uuid: The uuid of the newly created node
        :type new_parent_uuid: str
        """
        con_list = self.db_handler.get_child_items(old_parent_uuid)

        for child in con_list:
            old_node_uuid = child[0]
            node = Node(
                uuid=child[0],
                parent_uuid=new_parent_uuid,
                name=child[2],
                is_folder=child[3],
                address=child[4],
                port=child[5],
                use_parent_auth=child[7],
                auth_uuid=child[8],
                is_jumphost=child[9],
                use_jumphost=child[10],
                use_parent_jumphost=child[11]
            )

            auth = self.db_handler.get_auth_data(node.auth_uuid)
            auth.auth_uuid = str(uuid4())
            self.db_handler.save_auth_to_db(auth)

            # alter data of copied node
            node.name = f'{node.name} - copy'
            node.uuid = str(uuid4())

            self.db_handler.save_node_to_db(node)

            if node.is_folder:
                self.__recursive_copy_func(old_parent_uuid=old_node_uuid, new_parent_uuid=node.uuid)

    def get_node_by_uuid(self, uuid:str = None):
        """
        Get an item by its UUID.
        The item may be an ObTreeNode.

        :param uuid: The UUID of the item
        :type uuid: str
        :return: The item or None
        :rtype: ObTreeNode, ObListStore or None
        """
        cursor = self.db_handler.conn.cursor()
        result = None

        if uuid is not None:
            cursor.execute(
                'SELECT name, is_folder, parent_uuid, auth_uuid FROM connections WHERE uuid IS ?',
                (uuid,)
            )
            result = cursor.fetchone()

        if result is not None:
            node = ObTreeNode(
                uuid=uuid,
                name=result[0],
                is_folder=bool(result[1]),
                parent_uuid=result[2],
                auth_uuid=result[3]
                )
            return node
        else:
            return None

    def get_folder_by_child_uuid(self, uuid):
        """
        Get a folder by a child's UUID.
        This helps get parent folders.

        :param uuid: The UUID of the folder
        :type uuid: str
        :return: The ObListStore or None
        :rtype: ObListStore or None
        """
        cursor = self.db_handler.conn.cursor()
        parent_uuid = self.get_folder_uuid_by_child_uuid(uuid)
        result = None

        if parent_uuid is not None:
            cursor.execute(
                'SELECT name FROM connections WHERE uuid IS ?',
                (parent_uuid)
            )
            result = cursor.fetchone()

        if result is not None:
            store = ObListStore(
                name=result[0],
                uuid=parent_uuid
            )
            return store
        else:
            return None


    def get_folder_uuid_by_child_uuid(self, uuid):
        """
        Get a folder's UUID by a child's UUID.
        This helps identify parent folders.

        :param uuid: The UUID of the folder
        :type uuid: str
        :return: The ObListStore or None
        :rtype: ObListStore or None
        """
        cursor = self.db_handler.conn.cursor()
        result = None

        if uuid is not None:
            cursor.execute(
                'SELECT parent_uuid FROM connections WHERE uuid IS ?',
                (uuid,)
            )
            result = cursor.fetchone()

        if result is not None:
            return result[0]
        else:
            return None

    # probably obsolete
    def run_tests(self):
        """
        Runs some test cases, to verify if lookup methods for the model work correctly.
        Pretty ugly and hacky.
        """
        # These are tests and will be removed once the datamodel functions properly
        # Tests if a ObTreeNode can be accessed via its UUID
        # Should return item server-3
        print('===== Test 1 =====')
        print('Test Case: Node Lookup')
        uuid_1 = '4283d28d-f301-4935-9112-e42f3819d53e'
        print(f'Node UUID: {uuid_1}, Expected Result: {uuid_1}')
        test_node_1 = self.get_node_by_uuid(uuid_1)
        print(f'Result Node: {test_node_1.name} with UUID: {test_node_1.uuid}')

        # Tests if a ObListStore can be accessed via a child nodes UUID
        # Should return folder us-east-3a, child uuid is of item router-us-east-3a
        print('===== Test 2 =====')
        print('Test Case: Folder by Child UUID Lookup')
        uuid_2 = '4283d28d-f301-4935-9112-e42f3819d53e'
        print(f'Node UUID: {uuid_2}, Expected Result: us-east-3a - 3e8639e7-abc6-4012-8500-32a8c61eb42f')
        test_list_store_2 = self.get_folder_by_child_uuid(uuid_2)
        print(f'Result Folder: {test_list_store_2.name} with UUID {test_list_store_2.uuid}')

        # Tests if a ObListStores UUID can be resolved from a child nodes UUID
        # Should return folder us-east-3, child uuid is of folder us-east-3a
        print('===== Test 3 =====')
        print('Test Case: Folder UUID by Child UUID Lookup')
        uuid_3 = '3e8639e7-abc6-4012-8500-32a8c61eb42f'
        print(f'Node UUID: {uuid_3}, Expected Result: be50f325-4cd0-4f6c-bbc6-2ae43dd90eb5')
        test_list_store_uuid = self.get_folder_uuid_by_child_uuid(uuid_3)
        print(f'Result: Folder UUID {test_list_store_uuid}')

        print('===== Test 4 =====')
        print('Test Case: Folder by Child UUID Lookup, Folder should be config file representer')
        uuid_4 = '0b7fd8c4-1bdd-456e-960f-5838b56d215b'
        print(f'Node UUID: {uuid_4}, Expected Result: {os.path.basename(self.filename)}')
        test_list_store_4 = self.get_folder_by_child_uuid(uuid_4)
        print(f'Result Folder: {test_list_store_4.name} with UUID {test_list_store_4.uuid}')

        print('===== Test 5 =====')
        print('Test Case: Folder by Child Folder UUID Lookup')
        uuid_5 = '3e8639e7-abc6-4012-8500-32a8c61eb42f'
        print(f'Node UUID: {uuid_5}, Expected Result: be50f325-4cd0-4f6c-bbc6-2ae43dd90eb5')
        test_list_store_5 = self.get_folder_by_child_uuid(uuid_5)
        print(f'Result Folder: {test_list_store_5.name} with UUID {test_list_store_5.uuid}')

    def initialize_config_path(self):
        home_dir = Path.home()
        ob_conf_dir = f"{home_dir}/.config/obelisk"
        if not Path(ob_conf_dir).exists():
            Path.mkdir(ob_conf_dir)
