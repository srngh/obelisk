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

from pprint import pprint

from gi.repository import GObject, Gtk, Gio, Gdk

from .widgets.obelisk_tree_widget import ObeliskTreeWidget2
from .widgets.obelisk_context_menu import ObeliskContextMenu


class ObeliskListView(Gtk.ListView):
    __gtype_name__ = "ObeliskListView"

    model = Gtk.SingleSelection()

    def __init__(self, items, **kwargs):

        self.items = items
        # print(self.items)
        super().__init__(**kwargs)

        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", self.on_setup)
        factory.connect("bind", self.on_bind_2)
        # factory.connect("pressed", )
        self.set_factory(factory)

        gesture = Gtk.GestureClick(button=Gdk.BUTTON_SECONDARY)
        gesture.connect("pressed", self.__on_button_press)
        self.add_controller(gesture)

        tree_model = parse_items(self.items)
        tree_list_model = Gtk.TreeListModel.new(
            tree_model, False, True, self.__tree_model_create_func
        )
        selection_model = Gtk.SingleSelection(model=tree_list_model)
        # self.selection_model.connect("notify::selected-item", self.__on_selected_item_notify)
        self.set_model(selection_model)

    def __tree_model_create_func(self, item):
        if item.children == []:
            return None
        child_model = Gio.ListStore.new(ObeliskTreeNode)
        for child in item.children:
            child_model.append(child)
        return child_model

    def __on_button_press(self, gesture, npress, x, y):
        # This feels impractical
        print(gesture, npress, x, y)
        expander = self.__get_tree_expander(x, y)

        if expander is None or npress != 1:
            return False

        # Select row at x,y
        list_row = expander.get_list_row()
        self.model.set_selected(list_row.get_position())

        menu = ObeliskContextMenu()
        # self.set_child(menu)
        menu.set_parent(self)
        menu.popup_at(x, y)
        print(self)
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
        list_item.set_child(ObeliskTreeWidget2())

    def on_bind(self, factory, list_item):
        list_row = list_item.get_item()
        widget = list_item.get_child()
        item = list_row.get_item()

        match item.item_type:
            case "connection":
                widget.icon.set_from_icon_name("ssh-symbolic")
            case "folder":
                widget.remove(widget.icon)

        widget.expander.set_list_row(list_row)
        widget.label.set_label(item.title)

    def on_bind_2(self, factory, list_item):
        list_row = list_item.get_item()
        expander = list_item.get_child()
        expander.set_list_row(list_row)
        expander.update_bind()


def parse_items(connections: dict):
    tree_model = Gio.ListStore.new(ObeliskTreeNode)
    for item in connections:
        match connections[item]["item_type"]:
            case "connection":
                node = create_tree_node(connections[item])
                tree_model.append(node)
            case "folder":
                node = create_folder_node(connections[item])
                tree_model.append(node)
    return tree_model


def create_tree_node(connection: dict):
    node = ObeliskTreeNode(connection["item_title"])
    node.ip4_address = connection["ip4_address"]
    node.item_type = connection["item_type"]
    node.user = connection["user"]
    node.user = connection["item_description"]
    node.protocol = connection["protocol"]
    node.auth = connection["auth"]
    return node


def create_folder_node(folder: dict):
    children = []
    for item in folder["connections"]:
        match folder["connections"][item]["item_type"]:
            case "connection":
                node = create_tree_node(folder["connections"][item])
                children.append(node)
            case "folder":
                node = create_folder_node(folder["connections"][item])
                children.append(node)
    node = ObeliskTreeNode(folder["item_title"], _children=children)
    node.item_type = "folder"
    return node


class ObeliskTreeNode(GObject.GObject):
    def __init__(self, _title, _children=None):
        super().__init__()
        self.children = _children or []
        self.title = _title

    def get_item_title(self):
        return self.title


"""
# @Gtk.Template(resource_path='/io/github/srngh/obelisk/gtk/context-menu.ui')
class ObeliskContextMenu(Gtk.PopoverMenu):
    __gtype_name__ = 'ObeliskContextMenu'
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        menu_model = Gio.Menu()

        menu_model.insert(0, "New Item")
        menu_model.insert(1, "Clone Item")
        menu_model.insert(2, "Delete Item")
        menu_model.insert(3, "Connect")
        self.set_menu_model(menu_model)
        self.set_position(1)

    def popup_at(self, x, y):
        r = Gdk.Rectangle()
        r.x, r.y = (x, y)
        r.width = r.height = 0
        self.set_pointing_to(r)
        self.popup()
        print(self)
"""
