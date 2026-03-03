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

from gi.repository import GObject, Gdk, Gtk

from .widgets.ob_context_menu import ObContextMenu
from .widgets.ob_tree_expander import ObTreeExpander
from .widgets.ob_tree_node import ObTreeNode
from .widgets.ob_list_store import ObListStore


class ObListView(Gtk.ListView):

    __gtype_name__ = 'ObeliskListView'

    model = Gtk.SingleSelection()

    def __init__(self, config, **kwargs):
    #def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config = config

        factory = Gtk.SignalListItemFactory()
        factory.connect('setup', self.on_setup)
        factory.connect('bind', self.on_bind)
        factory.connect('unbind', self.on_unbind)
        self.set_factory(factory)

        gesture = Gtk.GestureClick(button=Gdk.BUTTON_SECONDARY)
        gesture.connect('released', self.__on_button_press)
        self.add_controller(gesture)
        self.set_model(config.selection_model)

    def __on_button_press(self, gesture, npress, x, y):
        # print(gesture, npress, x, y)
        expander = self.__get_tree_expander(x, y)
        if npress != 1:
            return False
        elif expander is None:
            """
            When clicking on any empty part of the ListView
            """
            context_menu = ObContextMenu('00000000-0000-0000-0000-000000000000')
            context_menu.set_parent(self)
            context_menu.popup_at(x, y)
            # self.context_menu.set_reference('00000000-0000-0000-0000-000000000000')
            # print('Popup created at 00000000-0000-0000-0000-000000000000')
            return True
        else:
            """
            When clicking on an item of the ListView
            """
            item = expander.props.item
            parent_folder = None
            if isinstance(item, ObTreeNode):
                parent_folder = self.config.get_liststore_by_node_uuid(item.uuid)
            elif isinstance(item, ObListStore):
                parent_folder = item

            if parent_folder is not None:
                """
                print(f'clicked on {item.name}')
                if parent_folder.uuid == item.uuid:
                    print(f'this is a folder')
                else:
                    print(f'resolved parent to {parent_folder.name}')
                """
                context_menu = ObContextMenu(parent_folder.uuid)
                context_menu.set_parent(self)
                list_row = expander.get_list_row()
                self.model.set_selected(list_row.get_position())

                context_menu.popup_at(x, y)
                # print(f'Popup created at {expander.props.item.uuid}')
                # self.context_menu.set_reference(expander.props.item.uuid)
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

    def on_unbind(self, factory, list_item):
        expander = list_item.get_child()
        expander.clear_bind()

