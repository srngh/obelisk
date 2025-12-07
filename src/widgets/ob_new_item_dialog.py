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

from gi.repository import Adw
from gi.repository import Gtk

import netaddr

from .ob_tree_node import ObTreeNode


@Gtk.Template(resource_path='/io/github/srngh/obelisk/gtk/ob_new_item_dialog.ui')
class ObNewItemDialog(Adw.PreferencesDialog):
    __gtype_name__ = 'ObNewItemDialog'

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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.port_input.set_value(22)

        self.confirm_button.connect('clicked', self.on_confirm)
        self.cancel_button.connect('clicked', self.on_cancel)

    def on_confirm(self, user_data):
        # self.set_can_close(False) # Lock the Dialog before the minimum input is correct

        """
        Validate
        - is hostname_input a valid IPv4 or IPv6 address
        - is username set, else use current users name
        - auth is kbd_interactive by default
        - jump host can be empty (ignored for now)
        - proxy can be empty (ignored for now)
        - if connection title is empty, use ip address as title
        - port is 22 by default
        """
        try:
            ip = netaddr.IPAddress(self.hostname_input.get_text())
            port = self.port_input.get_value()
            title = self.connection_name_input.get_text() or ip
            username = self.username_input.get_text() or os.getlogin()
            # print(self.auth_method.get_text())

            print(f'User Input {ip} is an IPv{ip.version} Address')
            print(f'Title: {title}\
            IP: {ip}\
            Port: {int(port)}\
            Username: {username}')

            self.set_can_close(True)
            node = ObTreeNode(title)
            if ip.version == 4:
                node.ip4_address = str(ip)
            elif ip.version == 6:
                node.ip6_address = str(ip)
            node.username = username
            node.protocol = 'SSH'
            node.port = port
            node.auth = 'pubkey'
            # return node
            print(node)
            self.close()
        except netaddr.AddrFormatError as e:
            print(e)

    def on_cancel(self, user_data):
        self.close()

    # print(f"connection_name_input is activatable: {self.connection_name_input.activatable()}")
    # print(f"{self.__dict__}")
