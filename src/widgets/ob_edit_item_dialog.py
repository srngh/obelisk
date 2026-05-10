# new_item_dialog.py
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

import os
from uuid import uuid4
from dataclasses import dataclass

from gi.repository import Adw, GObject, Gtk

import netaddr

from .ob_tree_node import ObTreeNode


@Gtk.Template(resource_path='/io/github/srngh/obelisk/gtk/ob_new_item_dialog.ui')
class ObEditItemDialog(Adw.PreferencesDialog):
    """
    A Dialog to create and edit Items.
    A Folder must be passed, so it is clear where to insert a new Item later on.
    An Item may be passed, if it should be edited.

    :param folder: The folder where the returned item should be attached to
    :type folder: ObListStore
    :param item: The item that will be edited
    :type item: ObTreeNode
    """
    __gtype_name__ = 'ObNewItemDialog'

    __gsignals__ = {
        'node_submitted': (GObject.SignalFlags.RUN_LAST, None, (ObTreeNode, ObTreeNode)),
        'refresh_parent': (GObject.SignalFlags.RUN_LAST, None, (str,)),
    }

    # Template Elements
    hostname_input = Gtk.Template.Child()
    connection_name_input = Gtk.Template.Child()
    auth_method = Gtk.Template.Child()
    jumphost_input = Gtk.Template.Child()
    proxy_input = Gtk.Template.Child()
    connection_name_input = Gtk.Template.Child()
    port_input = Gtk.Template.Child()
    username_input = Gtk.Template.Child()

    cancel_button = Gtk.Template.Child()
    confirm_button = Gtk.Template.Child()

    def __init__(self, parent_uuid=None, node_uuid=None, conn=None, dialog_mode='new_node', **kwargs):
        super().__init__(**kwargs)
        self.dialog_mode = dialog_mode
        self.parent_uuid = parent_uuid
        self.node_uuid = node_uuid
        self.conn = conn

        if self.node_uuid is not None:
            self.node = self.fetch_item_data()
            self.load_data_into_dialog()
        else:
            self.close()

        self.port_input.set_value(22)

        self.confirm_button.connect('clicked', self.on_confirm)
        self.cancel_button.connect('clicked', self.on_cancel)

        if self.dialog_mode == 'new_folder':
            list_box = self.hostname_input.props.parent
            list_box.remove(self.hostname_input)
            list_box.remove(self.port_input)
            self.connection_name_input.set_title('Folder Name')
            super().set_title('Add a new Folder')

    def on_confirm(self, Button):
        """
        Create a new item or raise a toast (soon) informing the user which input is missing / wrong.

        :param Button: The Button which is connected to this function.
        :type Button: Gtk.Button
        """
        match self.dialog_mode:
            case 'new_item':
                try:
                    self.__edit_node()
                    self.emit('refresh_parent', self.parent_uuid)
                finally:
                    self.close()
            case 'edit_node':
                try:
                    if self.node.is_folder:
                        self.__edit_folder()
                    else:
                        self.__edit_node()
                finally:
                    self.emit('refresh_parent', self.parent_uuid)
                    self.close()
            case 'clone_node':
                try:
                    self.__clone_node()
                    self.emit('refresh_parent', self.parent_uuid)
                finally:
                    self.close()
            case 'new_folder':
                try:
                    self.__edit_folder()
                    self.emit('refresh_parent', self.parent_uuid)
                finally:
                    self.close()

    def on_cancel(self, Button):
        """
        Close the Dialog.

        :param Button: The Button which is connected to this function.
        :type Button: Gtk.Button
        """
        self.close()

    def load_node_into_dialog(self, is_folder):
        """
        Load an Items content into the dialog.
        """
        if not is_folder:
            self.hostname_input.set_text(self.node.ip4_address)
            self.connection_name_input.set_text(self.node.name)
            self.username_input.set_text(self.node.username)
        else:
            self.connection_name_input.set_text(self.node.name)
            list_box = self.hostname_input.props.parent
            list_box.remove(self.hostname_input)
            list_box.remove(self.port_input)
        pass

    def fetch_item_data(self):
        """
        Perform a database lookup of the items data and load everything into the dialog.
        """
        node_uuid = self.node_uuid
        cursor = self.conn.cursor()

        # get all data of the item from the db
        if node_uuid is not None:
            cursor.execute(
                'SELECT name, is_folder, parent_id, address, port, username, password FROM connections WHERE id IS ?',
                (node_uuid,)
            )
            result = cursor.fetchone()

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
            return Node(uuid=node_uuid)

    def write_data_to_db(self):
        """
        Write config parameters to the database.
        """
        node = self.node
        cursor = self.conn.cursor()

        cursor.execute('SELECT name FROM connections WHERE id is ?', (node.uuid,))
        result = cursor.fetchone()

        # Item does not exist yet
        if result is None:
            cursor.execute(
                'INSERT INTO connections VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                (
                    self.node.uuid,
                    self.node.name,
                    int(self.node.is_folder),
                    self.parent_uuid,
                    self.node.address,
                    self.node.port,
                    self.node.username,
                    self.node.password,
                )

            )
        else:
            cursor.execute(
                'UPDATE connections SET name = ?, is_folder = ?, address = ?, username = ?, password = ? WHERE id = ?',
                (node.name, int(node.is_folder), node.address, node.username, node.password, node.uuid)
            )

    def load_data_into_dialog(self):
        """
        Perform a database lookup of the items data and load everything into the dialog.
        """

        if hasattr(self, 'node'):
            node = self.node
            self.connection_name_input.set_text(node.name or '')
            self.username_input.set_text(node.username or '')
            if not self.node.is_folder:
                self.hostname_input.set_text(node.address or '')
            else:
                list_box = self.hostname_input.props.parent
                list_box.remove(self.hostname_input)
                list_box.remove(self.port_input)

    def __edit_node(self):
        try:
            node = self.node

            ip = netaddr.IPAddress(self.hostname_input.get_text())
            if ip.version == 4 or ip.version == 6:
                node.address = ip.format()

            port = int(self.port_input.get_value())
            node.port = port

            node. name = self.connection_name_input.get_text() or node.address
            username = self.username_input.get_text()

            node.parent_uuid = self.parent_uuid

            username = self.username_input.get_text()
            if username != '':
                node.username = username
            else:
                node.username = None

            node.protocol = 'ssh'

            self.write_data_to_db()

        except netaddr.AddrFormatError as e:
            print(e)

    def __edit_folder(self):
        node = self.node
        node.name = self.connection_name_input.get_text()
        username = self.username_input.get_text()
        if username != '':
            node.username = username
        else:
            node.username = None

        self.write_data_to_db()

    def __clone_node(self):
        """
        Sets a new uuid to the node and calls the appropriate edit method.
        """
        node = self.node
        node.uuid = str(uuid4())

        if node.is_folder:
            # TO DO: recursively clone all children of the folder as well
            self.__edit_folder()
        else:
            print('henlo')
            self.__edit_node()

@dataclass
class Node():
    """This class only holds data in the context of the dialog is discarded imediately"""
    uuid: str
    name: str = None
    is_folder: bool = False
    parent_uuid: str = None
    address: str = None
    port: int = None
    username: str = None
    password: str = None

