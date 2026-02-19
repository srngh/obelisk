# ob_tree_widget.py
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

from gi.repository import Gtk


class ObTreeExpander(Gtk.TreeExpander):
    __gtype_name__ = 'ObTreeExpander'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.expander = Gtk.TreeExpander.new()
        self.label = Gtk.Inscription(hexpand=True)
        self.icon = Gtk.Image()

        self.set_child(self.label)

    def update_bind(self):
        item = self.props.item

        # Handle label
        self.__update_label(item)

    def __update_label(self, item):
        self.label.set_markup(item.name)

