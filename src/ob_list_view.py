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
    """
    ObListView Class, which presents a dynamic List of nested Items.
    A ObConfig must be passed, to retrieve the fully built Data Model to present.
    """
    __gtype_name__ = 'ObeliskListView'

    model = Gtk.SingleSelection()

    def __init__(self, config, **kwargs):
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
        self.set_model(self.config.selection_model)

    def __on_button_press(self, gesture, npress, x, y):
        """
        Opens a Context Menu pointing to the referenced Item in the ListView.
        If a folder is clicked, its' UUID will be passed to the context menu.
        If a node is clicked, the parent folders' UUID will be passed to the context menu.
        If the empty part is clicked, the parent is assumed to be the root of the ListView.

        :param gesture: The released gesture invoking this function
        :type gesture: Gtk.GestureClick
        :param npress: The amount of clicks
        :type npress: int
        :param x: X coordinate of the click
        :type x: float
        :param y: Y coordinate of the click
        :type y: float
        :rtype: bool
        """
        # TO DO: Pass the full item to the ConectMenu, so edit and clone methods can work with the same dialog
        expander = self.__get_tree_expander(x, y)
        if npress != 1:
            return False
        elif expander is None:
            # When clicking on any empty part of the ListView
            context_menu = ObContextMenu('00000000-0000-0000-0000-000000000000')
            context_menu.set_parent(self)
            context_menu.popup_at(x, y)
            return True
        else:
            # When clicking on any item or folder of the ListView
            item = expander.props.item
            folder = None
            if isinstance(item, ObTreeNode):
                folder = self.config.get_liststore_by_node_uuid(item.uuid)
            elif isinstance(item, ObListStore):
                folder = item

            if folder is not None:
                context_menu = ObContextMenu(folder.uuid)
                context_menu.set_parent(self)
                list_row = expander.get_list_row()
                self.model.set_selected(list_row.get_position())

                context_menu.popup_at(x, y)
                return True

    def __get_tree_expander(self, x, y):
        """
        Get the TreeExpander at X,Y coordinates.

        :param x: X coordinate
        :type x: float
        :param y: Y coordinate
        :type y: float
        :return: Clicked TreeExpander or None
        :rtype: Gtk.TreeExpander or None
        """
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

