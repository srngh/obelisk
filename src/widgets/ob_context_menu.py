# ob_context_menu.py
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

# from gi.repository import Adw
from gi.repository import GLib, Gdk, Gio, Gtk


class ObContextMenu(Gtk.PopoverMenu):
    __gtype_name__ = 'ObContextMenu'

    def __init__(self, folder_uuid, node_uuid='', **kwargs):
        super().__init__(**kwargs)
        self.folder_uuid: str = folder_uuid
        self.node_uuid = node_uuid

        # TO DO: Improve logic for when Actions should connect, and when they shouldn't

        model = Gio.Menu.new()

        section_1 = Gio.Menu.new()
        menu_new_item = Gio.MenuItem.new('_New Connection', 'list_view.new_item')
        menu_new_item.set_action_and_target_value('list_view.new_item', GLib.Variant.new_strv(['item', self.folder_uuid]))
        section_1.append_item(menu_new_item)

        menu_new_folder = Gio.MenuItem.new('_New Folder', 'list_view.new_item')
        menu_new_folder.set_action_and_target_value('list_view.new_item', GLib.Variant.new_strv(['folder', self.folder_uuid]))
        section_1.append_item(menu_new_folder)
        model.append_section(None, section_1)

        section_2 = Gio.Menu.new()
        menu_edit_item = Gio.MenuItem.new('_Edit Item', 'list_view.edit_item')
        menu_edit_item.set_action_and_target_value('list_view.edit_item', GLib.Variant.new_strv([self.folder_uuid, self.node_uuid]))
        section_2.append_item(menu_edit_item)

        menu_clone_item = Gio.MenuItem.new('_Clone Item', 'list_view.clone_item')
        menu_clone_item.set_action_and_target_value('list_view.clone_item', GLib.Variant.new_strv([self.folder_uuid, self.node_uuid]))
        section_2.append_item(menu_clone_item)

        if self.folder_uuid != '00000000-0000-0000-0000-000000000000' or self.node_uuid != '':
            menu_rename_item = Gio.MenuItem.new('_Rename', 'list_view.rename_item')
            menu_rename_item.set_action_and_target_value('list_view.rename_item', GLib.Variant.new_string(self.node_uuid))
        else:
            menu_rename_item = Gio.MenuItem.new('_Rename', 'list_view.empty')
        section_2.append_item(menu_rename_item)

        menu_remove_item = Gio.MenuItem.new('_Remove Item', 'list_view.remove_item')
        menu_remove_item.set_action_and_target_value('list_view.remove_item', GLib.Variant.new_string(self.node_uuid))
        section_2.append_item(menu_remove_item)

        model.append_section(None, section_2)

        section_3 = Gio.Menu.new()
        connect_item = Gio.MenuItem.new('_Connect', 'win.connect')
        connect_item.set_action_and_target_value('win.connect', GLib.Variant.new_string(self.node_uuid))
        section_3.append_item(connect_item)
        model.append_section(None, section_3)

        self.set_menu_model(model)
        self.set_position(1)

    def popup_at(self, x, y):
        r = Gdk.Rectangle()
        r.x, r.y = (x, y)
        r.width = r.height = 0
        self.set_pointing_to(r)
        self.popup()

    def unparent(self, a):
        super().unparent()

