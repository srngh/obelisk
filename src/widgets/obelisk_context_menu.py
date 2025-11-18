# obelisk_context_menu.py
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

#from gi.repository import Adw
from gi.repository import Gtk, Gio, Gdk

@Gtk.Template(resource_path='/org/gnome/obelisk/gtk/context-menu.ui')
class ObeliskContextMenu(Gtk.PopoverMenu):
    __gtype_name__ = 'ObeliskContextMenu'
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        menu_model = Gio.Menu()

        menu_model.insert(0, "New Item")
        menu_model.insert(1, "Clone Item")
        menu_model.insert(2, "Delete Item")
        menu_model.insert(3, "Connect")
        #self.set_menu_model(menu_model)
        #self.set_position(1)

    def popup_at(self, x, y):
        r = Gdk.Rectangle()
        r.x, r.y = (x, y)
        r.width = r.height = 0
        self.set_pointing_to(r)
        self.popup()
        print(self)
