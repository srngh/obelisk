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

from gi.repository import Adw
from gi.repository import Gtk, Gio

@Gtk.Template(resource_path='/io/github/srngh/obelisk/gtk/ob_new_item_dialog.ui')
class ObNewItemDialog(Adw.PreferencesDialog):
    __gtype_name__ = 'ObNewItemDialog'
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Template Elements
        address_input = Gtk.Template.Child()
        connection_name_input = Gtk.Template.Child()
        auth_input = Gtk.Template.Child()
        jumphost_input = Gtk.Template.Child()
        proxy_input = Gtk.Template.Child()
        connection_name_input = Gtk.Template.Child()

        cancel_button = Gtk.Template.Child()
        confirm_button = Gtk.Template.Child()

        def on_confirm(self):
            # Do a bunch of user input validation first




        #print(f"connection_name_input is activatable: {self.connection_name_input.activatable()}")
        print(f"{self.__dict__}")
