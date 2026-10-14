# ob_edit_item_dialog.py
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

# pylint: disable=E1101

import sqlite3
from uuid import uuid4

from gi.repository import Adw, GObject, Gio, Gtk

import netaddr
from fqdn import FQDN

from .ob_tree_node import ObTreeNode
from ..ob_config import ObDBConfig
from ..db_handler.obelisk_db_handler import ObeliskDBHandler
from ..db_handler.generic_node import Node


@Gtk.Template(resource_path="/io/github/srngh/obelisk/gtk/ob_edit_item_dialog.ui")
class ObEditItemDialog(Adw.Dialog):
    """
    A Dialog to create and edit Items.

    :param parent_uuid: Parent UUID of the item
    :type parent_uuid: str
    :param node_uuid: The item to edit
    :type node_uuid: str
    :param db_handler: The database handler which takes care of transactions
    :type db_handler: ObeliskDBHandler
    :param dialog_mode: The mode of this dialog, can be "new_node", "new_folder", "edit_node" or "clone_node"
    :type dialog_mode: str
    """

    __gtype_name__ = "ObEditItemDialog"

    __gsignals__ = {
        "refresh_folder": (GObject.SignalFlags.RUN_LAST, None, (str,)),
    }

    # Template Elements
    ## Connection Settings
    connection_name_input = Gtk.Template.Child()
    hostname_input = Gtk.Template.Child()
    port_input = Gtk.Template.Child()
    is_jumphost = Gtk.Template.Child()
    use_jumphost = Gtk.Template.Child()
    inherit_jumphost = Gtk.Template.Child()

    ## Authentication Settings
    use_parent_auth = Gtk.Template.Child()
    auth_method = Gtk.Template.Child()
    username_input = Gtk.Template.Child()
    password_input = Gtk.Template.Child()
    priv_key_input = Gtk.Template.Child()

    ## Buttons
    cancel_button = Gtk.Template.Child()
    confirm_button = Gtk.Template.Child()

    ##
    err_banner = Gtk.Template.Child()

    def __init__(
        self,
        parent_uuid: str,
        node_uuid: str,
        db_handler: ObeliskDBHandler,
        config: ObDBConfig,
        dialog_mode="new_node",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.dialog_mode = dialog_mode
        self.parent_uuid = parent_uuid
        self.node_uuid = node_uuid
        self.db_handler = db_handler
        self.config = config

        self.err_banner.connect("button-clicked", self.on_banner_clicked)

        if self.node_uuid is not None:
            self.node = self.db_handler.get_item_data(self.node_uuid)
            if hasattr(self.node, "auth_uuid"):
                self.auth = self.db_handler.get_auth_data(self.node.auth_uuid)
            self.load_data_into_dialog()
        else:
            self.close()

        self.confirm_button.connect("clicked", self.on_confirm)
        self.cancel_button.connect("clicked", self.on_cancel)

        match self.dialog_mode:
            case "new_folder":
                settings_box = self.hostname_input.props.parent
                settings_box.remove(self.hostname_input)
                settings_box.remove(self.port_input)

                jumphost_box = self.is_jumphost.props.parent
                jumphost_box.remove(self.is_jumphost)
                self.connection_name_input.set_title("Folder Name")
                super().set_title("Add a new Folder")
            case "edit_node":
                match self.node.is_folder:
                    case True:
                        super().set_title("Edit Folder")
                    case False:
                        super().set_title("Edit Connection")
            case "clone_node":
                match self.node.is_folder:
                    case True:
                        super().set_title("Clone Folder")
                    case False:
                        super().set_title("Clone Connection")

    def on_banner_clicked(self, Banner):
        self.err_banner.set_revealed(False)

    def on_confirm(self, Button):
        """
        Create a new item or raise a toast (soon) informing the user which input is missing / wrong.

        :param Button: The Button calling this function.
        :type Button: Gtk.Button
        """
        match self.dialog_mode:
            case "new_item":
                self.__edit_node()
            case "edit_node":
                if self.node.is_folder:
                    self.__edit_folder()
                else:
                    self.__edit_node()
            case "clone_node":
                self.__clone_node()
            case "new_folder":
                self.__edit_folder()

    def on_cancel(self, Button):
        """
        Close the Dialog.

        :param Button: The Button calling this function.
        :type Button: Gtk.Button
        """
        self.set_can_close(True)
        self.close()

    def load_data_into_dialog(self):
        """
        Perform a database lookup of the items data and load everything into the dialog.
        """

        if hasattr(self, "node"):
            node = self.node
            auth = self.auth

            # Connection Settings
            if self.dialog_mode == "clone_node":
                self.connection_name_input.set_text(f"{node.name or ''} - copy")
            else:
                self.connection_name_input.set_text(node.name or "")

            if not self.node.is_folder and self.node is not None:
                self.hostname_input.set_text(node.address or "")
                self.port_input.set_value(node.port or 22.0)
                self.is_jumphost.set_active(bool(node.is_jumphost))
            else:
                settings_box = self.hostname_input.props.parent
                settings_box.remove(self.hostname_input)
                settings_box.remove(self.port_input)

                jumphost_box = self.is_jumphost.props.parent
                jumphost_box.remove(self.is_jumphost)

            self.setup_jumphost_comborow()

            self.inherit_jumphost.set_active(bool(node.use_parent_jumphost))

            # Authentication Settings
            self.use_parent_auth.set_active(bool(node.use_parent_auth))

            # pref_method choose appropriate method from model

            self.username_input.set_text(auth.username or "")

            self.password_input.set_text(auth.password or "")

            self.priv_key_input.set_text(auth.priv_key_file or "")

    def setup_jumphost_comborow(self):
        """
        Setup function for the jumphost comborow.
        """
        j = self.db_handler.get_jumphosts()
        empty_jump = ObTreeNode(uuid=None, name="No Jumphost")
        store = Gio.ListStore()
        store.append(empty_jump)

        for row in j:
            node = ObTreeNode(uuid=row[0], name=row[1])
            store.append(node)

        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", self.on_comborow_setup)
        factory.connect("bind", self.on_comborow_bind)

        self.use_jumphost.set_model(store)
        self.use_jumphost.set_factory(factory)

        # Clear jumphost selection
        if self.node.jumphost_uuid is not None:
            jump_node = ObTreeNode(uuid=self.node.jumphost_uuid, name="")
        else:
            jump_node = empty_jump

        res = store.find_with_equal_func(jump_node, equal_func=self.eq_func)

        # res is a tuple like (True, index) or (False)
        if len(res) == 2:
            pos = res[1]
        else:
            # e.g. jumphost is referenced which no longer exists in list of jumphosts
            pos = 0

        self.use_jumphost.set_selected(pos)

    def on_comborow_setup(self, factory, list_item):
        """
        Setup function for the comborow factory.
        """
        label = Gtk.Label()
        list_item.set_child(label)

    def on_comborow_bind(self, factory, list_item):
        """
        Bind function for the comborow factory.
        """
        node = list_item.get_item()
        label = list_item.get_child()
        label.set_label(node.name)

    def eq_func(self, jump_node, tree_node) -> bool:
        """
        Custom equal function for comparing a selected jumphost to all available jumphosts.
        """
        if jump_node.uuid == tree_node.uuid:
            return True
        return False

    def __edit_node(self):
        """
        Take user input, validate and sanitize it and write it to the database.
        """
        try:
            # DB Lookup
            node = self.node
            auth = self.auth

            node.parent_uuid = self.parent_uuid
            node.auth_uuid = auth.auth_uuid

            if not node.is_folder:
                node.protocol = "ssh"
            else:
                node.protocol = None

            addr, err = self.__validate_address()

            if err is False:
                self.err_banner.set_revealed(True)
            else:
                node.address = addr

                node.name = self.connection_name_input.get_text() or node.address

                node.port = int(self.port_input.get_value())

                node.is_jumphost = self.is_jumphost.get_active()
                node.jumphost_uuid = self.__validate_use_jumphost()

                node.use_parent_jumphost = self.inherit_jumphost.get_active()

                # Authentication Settings
                node.use_parent_auth = self.use_parent_auth.get_active()

                auth.username = self.__validate_username()
                auth.password = self.__validate_password()
                auth.priv_key_file = self.__validate_priv_key()

                auth.ignost_host_key = True

                self.config.add_item(node=node, auth=auth)

                self.emit("refresh_folder", self.parent_uuid)
                self.close()

        except netaddr.AddrFormatError as e:
            print(e)

    def __edit_folder(self):
        """
        Take user input, validate and sanitize it and write it to the database.
        """
        node = self.node
        auth = self.auth

        node.parent_uuid = self.parent_uuid
        node.auth_uuid = auth.auth_uuid

        node.name = self.connection_name_input.get_text()
        node.is_folder = True
        node.is_jumphost = False
        node.jumphost_uuid = self.__validate_use_jumphost()
        node.use_parent_jumphost = self.inherit_jumphost.get_active()

        node.use_parent_auth = self.use_parent_auth.get_active()

        auth.username = self.__validate_username()
        auth.password = self.__validate_password()
        auth.priv_key_file = self.__validate_priv_key()

        auth.ignost_host_key = True

        self.config.add_item(node=node, auth=auth)

        self.emit("refresh_folder", self.parent_uuid)
        self.close()

    def __clone_node(self):
        """
        Sets a new uuid to the node and calls the appropriate edit method.
        """
        node = self.node
        auth = self.auth
        old_node_uuid = node.uuid
        node.uuid = str(uuid4())
        auth.auth_uuid = str(uuid4())
        node.auth_uuid = auth.auth_uuid

        if node.is_folder:
            self.__edit_folder()
            self.db_handler.conn.execute("BEGIN TRANSACTION;")
            self.config.recursive_copy_func(
                old_parent_uuid=old_node_uuid, new_parent_uuid=node.uuid
            )
            try:
                self.db_handler.conn.commit()
                self.emit("refresh_folder", self.parent_uuid)
                self.close()
            except sqlite3.Error as e:
                print("Could recursively populate copied folder:", e)
                self.db_handler.conn.rollback()
        else:
            self.__edit_node()

    def __validate_username(self) -> str:
        """
        Helper function to standardize types of input fields.
        """
        var = self.username_input.get_text()
        if var != "":
            return var
        else:
            return None

    def __validate_password(self) -> str:
        """
        Helper function to standardize types of input fields.
        """
        var = self.password_input.get_text()
        if var != "":
            return var
        else:
            return None

    def __validate_priv_key(self) -> str:
        """
        Helper function to standardize types of input fields.
        """
        var = self.priv_key_input.get_text()
        if var != "":
            return var
        else:
            return None

    def __validate_use_jumphost(self) -> str:
        """
        Helper function to standardize types of input fields.
        """
        item = self.use_jumphost.get_selected_item()
        return item.uuid

    def __validate_address(self) -> tuple[str, bool]:
        """
        Helper function to validate hostname_input.
        """
        address = self.hostname_input.get_text()

        address = address.strip()

        addr = FQDN(address)

        if addr.is_valid:
            try:
                ip = netaddr.IPAddress(address)
                if ip.is_unicast():
                    return address, True
            except netaddr.core.AddrFormatError:
                # don't really need to deal with the error
                pass
            return address, True
        elif address.lower() in ["localhost"]:
            return address, True
        return "", False
