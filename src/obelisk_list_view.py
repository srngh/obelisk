# obelisk_tree_expander.py
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

import yaml

from gi.repository import GObject, Gtk, Gio

from .widgets.obelisk_tree_widget import ObeliskTreeWidget

class ObeliskListView(Gtk.ListView):
    __gtype_name__ = "ObeliskListView"

    model = Gtk.SingleSelection()

    def __init__(self, items, **kwargs):

        self.items = items
        print(self.items)
        super().__init__(**kwargs)

        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", self.on_setup)
        factory.connect("bind", self.on_bind)
        self.set_factory(factory)

        '''
        tree_model = Gio.ListStore.new(ObeliskTreeNode)
        for item in self.items:
            print(f'{item} is of type {type(item)}')
            tree_model.append(ObeliskTreeNode(f'{self.items[item]["item_title"]}'))
            print(self.items[item]['item_title'])
        '''
        tree_model = parse_items(self.items)
        tree_list_model = Gtk.TreeListModel.new(tree_model, False, True, self.__tree_model_create_func)
        selection_model = Gtk.SingleSelection(model=tree_list_model)
        self.set_model(selection_model)


    def __tree_model_create_func(self, item):
        if item.children == []:
            return None
        child_model = Gio.ListStore.new(ObeliskTreeNode)
        for child in item.children:
            child_model.append(child)
        return child_model


    def on_setup(self, factory, list_item):
        list_item.set_child(ObeliskTreeWidget())


    def on_bind(self, factory, list_item):
        list_row = list_item.get_item()
        widget = list_item.get_child()
        item = list_row.get_item()

        widget.expander.set_list_row(list_row)
        widget.label.set_label(item.title)


def parse_items(connections: dict):
    tree_model = Gio.ListStore.new(ObeliskTreeNode)
    for item in connections:
        match connections[item]['item_type']:
            case 'connection':
                node = create_tree_node(connections[item])
                tree_model.append(node)
            case 'folder':
                node = create_folder_node(connections[item])
                tree_model.append(node)
    return tree_model


def create_tree_node(connection: dict):
    node = ObeliskTreeNode(connection['item_title'])
    node.ip4_address = connection['ip4_address']
    node.user = connection['user']
    node.user = connection['item_description']
    node.protocol = connection['protocol']
    node.auth = connection['auth']
    return node


def create_folder_node(folder: dict):
    children = []
    for item in folder['connections']:
        print(folder['connections'])
        match folder['connections'][item]['item_type']:
            case 'connection':
                node = create_tree_node(folder['connections'][item])
                children.append(node)
            case 'folder':
                node = create_folder_node(folder['connections'][item])
                children.append(node)
    node = ObeliskTreeNode(folder['item_title'], _children=children)
    return node


class ObeliskTreeNode(GObject.GObject):
    def __init__(self, _title, _children=None):
        super().__init__()
        self.children = _children or []
        self.title = _title
