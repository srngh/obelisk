# obelisk_db_handler.py
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

import sqlite3

from .generic_node import Node
# from ..widgets.ob_list_store import ObListStore
# from ..widgets.ob_tree_node import ObTreeNode


class ObeliskDBHandler:

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS connections (
                id TEXT PRIMARY KEY,
                parent_id TEXT,
                name TEXT NOT NULL,
                is_folder INTEGER NOT NULL,
                address TEXT,
                port INTEGER,
                username TEXT,
                protocol TEXT,
                auth_type TEXT,
                public_key TEXT
            )
        """)
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_name ON connections(name)')
        conn.commit()
        return conn

    def save_nodes_to_db(self, node):
        cursor = self.conn.cursor()
        data_insert = [(node.id, node.name, int(node.is_folder)) for node in node_list]

        cursor.executemany(
            """
            INSERT INTO connections (id, name, is_folder)
            VALUES (?, ?, ?)
            """,
            data_insert,
        )
        conn.commit()

    def save_node_to_db(self, node: Node) -> bool:
        """
        Write a single connection node to the database, or update a node if it exists.

        :param node: A node representing a connection item
        :type node: Node
        """
        cursor = self.conn.cursor()

        cursor.execute('SELECT name FROM connections WHERE id is ?', (node.uuid,))
        result = cursor.fetchone()


        try:
            if result is None:
                # Item does not exist
                cursor.execute(
                    'INSERT INTO connections VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                    (
                        node.uuid,
                        node.name,
                        int(node.is_folder),
                        node.parent_uuid,
                        node.address,
                        node.port,
                        node.username,
                        node.password,
                    )

                )
                return True
            else:
                cursor.execute(
                    'UPDATE connections SET name = ?, is_folder = ?, address = ?, username = ?, password = ? WHERE id = ?',
                    (node.name, int(node.is_folder), node.address, node.username, node.password, node.uuid)
                )
                return True
        except sqlite3.DataError as e:
            print(f'Encountered Error when trying to write data to database')
            print(e)
        except sqlite3.Error as e:
            print(f'Encountered Sqlite Error')
            print(e)

    def get_item_data(self, node_uuid: str) -> Node:
        """
        Get a connection node data from the database.

        :param node_uuid: The uuid of the node to look up
        :type node_uuid: str
        """
        cursor = self.conn.cursor()

        if node_uuid is not None:
            cursor.execute(
                'SELECT name, is_folder, parent_id, address, port, username, password FROM connections WHERE id IS ?',
                (node_uuid,)
            )
            result = cursor.fetchone()

        try:
            if result is not None:
                node = Node(
                    uuid=node_uuid,
                    name=result[0],
                    is_folder=bool(result[1]),
                    parent_uuid=result[2],
                    address=result[3],
                    port=result[4],
                    username=result[5],
                    password=result[6]
                )
                return node
            else:
                # If the connection doesn't exist, return a bare Node
                return Node(uuid=node_uuid)
        except sqlite3.Error as e:
            print(f'Encountered Sqlite Error')
            print(e)
    
    def rename_item(self, node_uuid: str, new_name: str) -> bool:
        """
        """
        cursor = self.conn.cursor()
        
        if node_uuid is not None and new_name is not None:
            cursor.execute(
                'UPATEDE connections SET name = ? WHERE id = ?',
                (new_name, node_uuid)
            )
            return True
        else:
            return False

    def test(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, name, is_folder FROM connections WHERE parent_id IS NULL')



