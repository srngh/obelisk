# sidebar_item.py
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

from gi.repository import Gtk, GObject, Pango

class SidebarItem(Gtk.ListBoxRow):
    __gtype_name__ = "SidebarItem"

    # Elements
    item_uuid = GObject.Property(type=str, default="")
    item_title = GObject.Property(type=str, default="")
    item_type = GObject.Property(type=str, default="")
    item_description = GObject.Property(type=str, default="")
    icon_name = GObject.Property(type=str, default="")
    tool_tip = GObject.Property(type=str, default="")
    # category = GObject.Property(type=str, default="")

    def __init__(self, item_uuid: str, item_title: str, item_type: str, item_description: str, icon_name: str, **kwargs):
        super().__init__(**kwargs)

        self.item_uuid = item_uuid
        self.item_title = item_title
        self.item_type = item_type
        self.item_description = item_description
        self.icon_name = icon_name

        grid = Gtk.Grid()
        grid.set_hexpand(True)
        grid.set_margin_top(4)
        grid.set_margin_bottom(4)
        grid.set_margin_start(6)
        grid.set_margin_end(2)
        grid.set_column_spacing(6)

        icon = Gtk.Image()
        icon.set_from_icon_name(self.icon_name)
        grid.attach(icon, 0, 0, 1, 1)
        grid.attach(Gtk.Label(
            label=self.item_title,
            xalign=0.0,
            lines=2,
            wrap=True,
            ellipsize=Pango.EllipsizeMode.END
        ), 1, 0, 1, 1)
        self.set_child(grid)
        self.set_tooltip_text(self.item_description)

        #self.connect('activate', self.on_sidebar_item_activated)

        #self.connect('clicked', self.on_sidebar_item_clicked)

    def get_item_uuid(self) -> str:
        return self.item_uuid

    def get_item_title(self) -> str:
        return self.item_title

    def get_icon_name(self) -> str:
        return self.icon_name

    def get_item_description(self) -> str:
        return self.item_description

    def get_item_type(self) -> str:
        return self.item_type

    #def on_sidebar_item_activated(self, ListBoxRow):
    #    print(f"activated {self.item_title}")

    #def on_sidebar_item_clicked(self, ListBoxRow):
    #    print(f"clicked on {self.item_title}")
