# ob_context_menu.py
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

# from gi.repository import Adw
from gi.repository import Gdk, Gio, GLib, Gtk


# @Gtk.Template(resource_path='/io/github/srngh/obelisk/gtk/ob_context_menu.ui')
class ObContextMenu(Gtk.PopoverMenu):
    __gtype_name__ = 'ObContextMenu'

    def __init__(self, uuid, **kwargs):
        super().__init__(**kwargs)
        self.referenced_node_uuid: str = uuid

        model = Gio.Menu.new()

        section_1 = Gio.Menu.new()

        item_1 = Gio.MenuItem.new('_New Item', 'win.new_item')
        item_1.set_action_and_target_value('win.new_item', GLib.Variant.new_string(self.referenced_node_uuid))
        section_1.append_item(item_1)
        section_1.append('_Duplicate Item', 'win.clone_item')
        section_1.append('_Remove Item', 'win.delete_item')
        model.append_section(None, section_1)

        section_2 = Gio.Menu.new()
        section_2.append('_Edit Item', 'win.edit_item')
        section_2.append('_Connect', 'win.connect')
        section_2.append('_Rename', 'win.rename')
        model.append_section(None, section_2)

        self.set_menu_model(model)
        self.set_position(1)

    def popup_at(self, x, y):
        print(self.referenced_node_uuid)
        r = Gdk.Rectangle()
        r.x, r.y = (x, y)
        r.width = r.height = 0
        self.set_pointing_to(r)
        print(self.get_menu_model())
        # model = self.get_menu_model()
        # for index in range(model.get_n_items()):
        #     print(index, range(model.get_n_items()))
        #     print(model.get_item(index))
        self.popup()

