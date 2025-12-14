# obelisk_tree_list_view.py
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

# from pprint import pprint

from gi.repository import Gdk, Gio, Gtk

from .widgets.ob_context_menu import ObContextMenu
from .widgets.ob_tree_expander import ObTreeExpander


class ObListView(Gtk.ListView):

    __gtype_name__ = 'ObeliskListView'

    model = Gtk.SingleSelection()

    def __init__(self, selection_model, **kwargs):
        super().__init__(**kwargs)

        factory = Gtk.SignalListItemFactory()
        factory.connect('setup', self.on_setup)
        factory.connect('bind', self.on_bind)
        self.set_factory(factory)

        gesture = Gtk.GestureClick(button=Gdk.BUTTON_SECONDARY)
        gesture.connect('released', self.__on_button_press)
        self.add_controller(gesture)
        self.set_model(selection_model)

    def __on_button_press(self, gesture, npress, x, y):
        # print(gesture, npress, x, y)
        expander = self.__get_tree_expander(x, y)

        if expander is None or npress != 1:
            return False

        # Select row at x,y
        list_row = expander.get_list_row()
        self.model.set_selected(list_row.get_position())

        menu = ObContextMenu()
        menu.set_parent(self)
        menu.popup_at(x, y)
        print(f'Popup created at {expander.props.item.uuid}')
        menu.set_reference(expander.props.item.uuid)
        return True

    def __get_tree_expander(self, x, y):
        pick = self.pick(x, y, Gtk.PickFlags.DEFAULT)

        if pick is None:
            return None

        if isinstance(pick, Gtk.TreeExpander):
            return pick

        child = pick.get_first_child()

        if child and isinstance(child, Gtk.TreeExpander):
            return child

        parent = pick.props.parent
        if parent and isinstance(parent, Gtk.TreeExpander):
            return parent

        return None

    def on_setup(self, factory, list_item):
        list_item.set_child(ObTreeExpander())

    def on_bind(self, factory, list_item):
        list_row = list_item.get_item()
        expander = list_item.get_child()
        expander.set_list_row(list_row)
        expander.update_bind()

