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

import os
from pathlib import Path
import sqlite3
from uuid import uuid4
from cryptography.fernet import Fernet

from .generic_node import Node
from .generic_auth import Auth

MIGRATIONS_DIR = '/app/share/obelisk/obelisk/db_handler/migrations'

class ObeliskDBHandler:

    def __init__(self, db_path: str, secret_key: str):
        self.db_path = db_path
        self.conn = self.init_db()
        self.Fernet = Fernet(secret_key.encode())

        self.migrate()


    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS authentication (
                auth_uuid TEXT PRIMARY KEY,
                username TEXT,
                password TEXT,
                key_file TEXT
            )
        """)

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS connections (
                uuid TEXT PRIMARY KEY,
                parent_uuid TEXT,
                name TEXT NOT NULL,
                is_folder INTEGER NOT NULL,
                address TEXT,
                port INTEGER,
                protocol TEXT,
                use_parent_auth INTEGER NOT NULL,
                auth_uuid TEXT NOT NULL,
                FOREIGN KEY (auth_uuid) REFERENCES authentication (auth_uuid)
            )
        """)
        

        cursor.execute('CREATE INDEX IF NOT EXISTS idx_name ON connections(name)')
        conn.commit()
        return conn
    
    def get_applied_migrations(self):
        cursor = self.conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version TEXT PRIMARY KEY
            )
            """
        )

        versions = cursor.execute(
            'SELECT version FROM schema_migrations'
        )

        return {row[0] for row in cursor.fetchall()}

    def apply_migration(self, version, sql):
        conn = self.conn
        print(f'Applying migration {version}...')
        conn.executescript(sql)
        conn.execute('INSERT INTO schema_migrations (version) VALUES (?)', (version,))
        conn.commit()
        print(f'Migration {version} applied.')

    def load_migration_file(self, filename):
        with open(os.path.join(MIGRATIONS_DIR, filename), 'r') as f:
            return f.read()
    
    def migrate(self):
        applied = self.get_applied_migrations()
        migrations = sorted(f for f in os.listdir(MIGRATIONS_DIR) if f.endswith('.sql'))
        
        for migration_file in migrations:
            version = migration_file.split('_')[0]
            if version not in applied:
                sql = self.load_migration_file(migration_file)
                self.apply_migration(version, sql)
            else:
                print(f'Migration {version} already applied')


    def save_nodes_to_db(self, node_list):
        cursor = self.conn.cursor()
        data_insert = [(node.uuid, node.name, int(node.is_folder)) for node in node_list]

        cursor.executemany(
            """
            INSERT INTO connections (uuid, name, is_folder)
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

        cursor.execute('SELECT name FROM connections WHERE uuid is ?', (node.uuid,))
        result = cursor.fetchone()

        try:
            if result is None:
                # Item does not exist
                cursor.execute(
                    'INSERT INTO connections VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                    (
                        node.uuid,
                        node.parent_uuid,
                        node.name,
                        int(node.is_folder),
                        node.address,
                        node.port,
                        'ssh',
                        int(node.use_parent_auth),
                        node.auth_uuid,
                        int(node.is_jumphost),
                        node.use_jumphost
                    )

                )
                return True
            else:
                cursor.execute(
                    """
                    UPDATE connections
                    SET parent_uuid = ?,
                    name = ?,
                    is_folder = ?,
                    address = ?,
                    port = ?,
                    protocol = ?,
                    use_parent_auth = ?,
                    auth_uuid = ?,
                    is_jumphost = ?,
                    use_jumphost = ?
                    WHERE uuid = ?
                    """,
                    (node.parent_uuid,
                    node.name,
                    int(node.is_folder),
                    node.address,
                    node.port,
                    'ssh',
                    int(node.use_parent_auth),
                    node.auth_uuid,
                    int(node.is_jumphost),
                    node.use_jumphost,
                    node.uuid)
                )
                return True
        except sqlite3.DataError as e:
            print(f'Encountered Error when trying to write data to database')
            print(e)
        except sqlite3.Error as e:
            print(f'Encountered Sqlite Error')
            print(e)

    def save_auth_to_db(self, auth: Auth) -> bool:
        """
        Write a authentication strategy to the database, or update one if it exists.

        :param auth: An auth object representing an Authentication strategy
        :type auth: Auth
        """
        print(auth)
        cursor = self.conn.cursor()

        cursor.execute('SELECT username FROM authentication WHERE auth_uuid is ?', (auth.auth_uuid,))
        result = cursor.fetchone()

        try:
            if result is None:
                cursor.execute(
                    'INSERT INTO authentication VALUES (?, ?, ?, ?, ?, ?)',
                    (
                        auth.auth_uuid,
                        auth.username,
                        auth.password,
                        auth.priv_key_file,
                        auth.pref_method,
                        int(auth.ignost_host_key)
                    )
                )
                return True
            else:
                cursor.execute(
                    """
                    UPDATE authentication
                    SET username = ?,
                    password = ?,
                    priv_key_file = ?,
                    pref_method = ?,
                    ignore_host_key = ?
                    WHERE auth_uuid = ?
                    """,
                    (auth.username,
                    self.Fernet.encrypt(auth.password.encode()).decode(),
                    auth.priv_key_file,
                    auth.pref_method,
                    auth.ignost_host_key,
                    auth.auth_uuid)
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
        The returned data is wrapped as a dataclass for convenience.

        :param node_uuid: The uuid of the node to look up
        :type node_uuid: str
        """
        cursor = self.conn.cursor()

        if node_uuid is not None:
            cursor.execute(
                """
                SELECT name,
                is_folder,
                parent_uuid,
                address,
                port,
                auth_uuid,
                use_parent_auth,
                is_jumphost,
                use_jumphost
                FROM connections WHERE uuid IS ?
                """,
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
                    auth_uuid=result[5],
                    use_parent_auth=result[6],
                    is_jumphost=bool(result[7]),
                    use_jumphost=result[8]
                )
                return node
            else:
                # If the connection doesn't exist, return a bare Node
                return Node(uuid=node_uuid)
        except sqlite3.Error as e:
            print(f'Encountered Sqlite Error')
            print(e)
    
    def get_auth_data(self, auth_uuid: str) -> Auth:
        """
        Get parameters for an authentication Object by uuid.
        The returned data is wrapped as a dataclass for convenience.

        :param auth_uuid: The uuid to look up in the authentication table.
        :type auth_uuid: str
        """
        cursor = self.conn.cursor()

        if auth_uuid is not None:
            cursor.execute(
                """
                SELECT username,
                password,
                priv_key_file,
                pref_method,
                ignore_host_key
                FROM authentication WHERE auth_uuid IS ?
                """,
                (auth_uuid,)
            )
            result = cursor.fetchone()
        else:
            return Auth(auth_uuid=str(uuid4()))

        try:
            if result is not None:
                auth = Auth(
                    auth_uuid=auth_uuid,
                    username=result[0],
                    password=self.decrypt(result[1]),
                    priv_key_file=result[2],
                    pref_method=result[3],
                    ignost_host_key=result[4]
                )
                return auth

        except sqlite3.Error as e:
            print(f'Encountered Sqlite Error')
            print(e)
    
    def decrypt(self, field) -> str:
        """
        decrypt sensitice fields
        """
        if field is not None and type(field) is bytes:
            return self.Fernet.decrypt(field).decode()
        elif field is not None and type(field) is str:
            return self.Fernet.decrypt(field.encode()).decode()
        else:
            return None

    def rename_item(self, node_uuid: str, new_name: str) -> bool:
        """
        Update the name of a node in the database.
        :param node_uuid: UUID of the node
        :type node_uuid: str
        :param new_name: New name for the node
        :type new_name: str
        """
        cursor = self.conn.cursor()
        
        if node_uuid is not None and new_name is not None:
            cursor.execute(
                'UPDATE connections SET name = ? WHERE uuid = ?',
                (new_name, node_uuid)
            )
            return True
        else:
            return False

    def test_query(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT uuid, name, is_folder FROM connections WHERE parent_uuid IS NULL')
        
    def get_child_items(self, node_uuid) -> list:
        """
        Get all child items of a folder.
        There is no explicit check if the provided uuid belongs to a folder or item.
        A lookup of an item uuid simply returns an empty list.

        :param node_uuid: The uuid for which to look up child items.
        :type node_uuid: str 
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT * from connections WHERE parent_uuid = ?', (node_uuid,))
        res = cursor.fetchall()
        return res

