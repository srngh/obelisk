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
from gi.repository import GLib, Gdk, Gio, Gtk


# @Gtk.Template(resource_path='/io/github/srngh/obelisk/gtk/ob_context_menu.ui')
class ObContextMenu(Gtk.PopoverMenu):
    __gtype_name__ = 'ObContextMenu'

    def __init__(self, folder_uuid, node_uuid='', **kwargs):
        super().__init__(**kwargs)
        self.folder_uuid: str = folder_uuid
        self.node_uuid = node_uuid

        model = Gio.Menu.new()

        section_1 = Gio.Menu.new()

        menu_new_item = Gio.MenuItem.new('_New Item', 'win.new_item')
        menu_new_item.set_action_and_target_value('win.new_item', GLib.Variant.new_string(self.folder_uuid))
        section_1.append_item(menu_new_item)
        model.append_section(None, section_1)

        section_2 = Gio.Menu.new()
        menu_edit_item = Gio.MenuItem.new('_Edit Item', 'win.edit_item')
        menu_edit_item.set_action_and_target_value('win.edit_item', GLib.Variant.new_strv([self.folder_uuid, self.node_uuid]))
        section_2.append_item(menu_edit_item)

        menu_clone_item = Gio.MenuItem.new('_Clone Item', 'win.clone_item')
        menu_clone_item.set_action_and_target_value('win.clone_item', GLib.Variant.new_strv([self.folder_uuid, self.node_uuid]))
        section_2.append_item(menu_clone_item)

        section_2.append('_Rename', 'win.rename')
        section_2.append('_Remove Item', 'win.delete_item')
        model.append_section(None, section_2)

        section_3 = Gio.Menu.new()
        section_3.append('_Connect', 'win.connect')
        model.append_section(None, section_3)

        self.set_menu_model(model)
        self.set_position(1)

    def popup_at(self, x, y):
        r = Gdk.Rectangle()
        r.x, r.y = (x, y)
        r.width = r.height = 0
        self.set_pointing_to(r)
        self.popup()

