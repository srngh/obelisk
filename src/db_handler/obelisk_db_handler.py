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

# from .generic_item import Item
# from ..widgets.ob_list_store import ObListStore
# from ..widgets.ob_tree_node import ObTreeNode


class ObeliskDBHandler:

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = self.init_db()
        # print(self.db_path)

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

    def save_nodes_to_db(self, conn, node_list):
        cursor = conn.cursor()
        data_insert = [(node.id, node.name, int(node.is_folder)) for node in node_list]

        cursor.executemany(
            """
            INSERT INTO connections (id, name, is_folder)
            VALUES (?, ?, ?)
            """,
            data_insert,
        )
        conn.commit()

    def get_nodes_chunk(self, limit=100, offset=0):
        cursor = self.conn.cursor()

        cursor.execute(
            """
            SELECT id, name, is_folder
            FROM connections
            ORDER BY name ASC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        )

        # rows = cursor.fetchall()
        pass
        # return [Item(name=row[1], is_folder=row[2], uuid=row[3]) for row in rows]
    
    def test(self):
        cursor = self.conn.cursor()
        
        cursor.execute('SELECT id, name, is_folder FROM connections WHERE parent_id IS NULL')
        



