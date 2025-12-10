# ob_config.py
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

from gi.repository import GObject, Gio, Gtk

from .config_file_handlers.config_file_handler import ConfigFileHandlerFactory
from .widgets.ob_tree_node import ObTreeNode


class ObConfig(GObject.Object, Gio.ListModel):
    __gtype_name__ = 'ObConfig'
    'This class holds the configuration of a loaded config file.'

    """
    __gsignals__ = {
        'changed': (GObject.SignalFlags.RUN_FIRST, None, ()) <<<<---- what it do?
        '': asdf
    }
    """
    def __init__(self, filename=None, **kwargs):
        super().__init__(**kwargs)
        self.autosave = False
        self.filename = filename
        self.config_type = 'obelisk'
        print(self.filename)
        default_handler = ConfigFileHandlerFactory().create_handler('obelisk')
        default_handler.load_connections(self.filename)
        self.items = default_handler.to_str()

        ob_list_store_model = parse_items(self.items)
        tree_list_model = Gtk.TreeListModel.new(
            ob_list_store_model, False, True, self.__tree_model_create_func
        )
        self.selection_model = Gtk.SingleSelection(model=tree_list_model)

        # self.__tree_model_debug_func()

    def __tree_model_create_func_old(self, item):
        """
        Old
        """
        if item.children == []:
            return None
        child_model = Gio.ListStore.new(ObTreeNode)
        for child in item.children:
            child_model.append(child)
        return child_model

    def __tree_model_create_func(self, item):
        """
        This builds the Gtk.TreeListModel.
        This feels like doing the work of parse_items() all over again.
        """
        if hasattr(item, 'children') and item.children == []:
            return None
        else:
            child_model = ObListStore(ObTreeNode, uuid=item.uuid, item_title=item.title)
            for index in range(item.get_n_items()):
                child_model.append(item.get_item(index))
            return child_model

    def __tree_model_debug_func(self):
        """
        For viewing the TreeModel
        """
        list_store = self.selection_model.get_model().get_model()
        debug_ob_store(list_store)


def debug_ob_store(store):
    """
    The recursive part of viewing the TreeModel
    """
    for index in range(store.get_n_items()):
        child = store.get_item(index)
        print(f'Object {child.title} has {index} items, has uuid {child.uuid} and is type {child.item_type}')
        if child.item_type == 'folder':
            debug_ob_store(child)


def parse_items(connections: dict):
    """
    Create a ObListStore, each containing either more ObListStores or ObTreeNodes.
    Only ObListStores can contain ObTreeNodes.
    ObTreeNodes will never have child objects.
    ObTreeNodes may be empty.
    """
    ob_list_store_model = ObListStore(ObTreeNode, uuid='00000000-0000-0000-0000-000000000000', item_title='root')
    for uuid in connections:
        match connections[uuid]['item_type']:
            case 'connection':
                node = create_tree_node(uuid, connections[uuid])
                ob_list_store_model.append(node)
            case 'folder':
                substore = create_folder_store(uuid, connections[uuid]['item_title'], connections[uuid])
                ob_list_store_model.append(substore)
    return ob_list_store_model


def create_tree_node(uuid, connection: dict):
    """
    Create a single ObTreeNode, containing all neccessary data
    """
    node = ObTreeNode(connection['item_title'])
    node.uuid = uuid
    node.ip4_address = connection['ip4_address']
    node.item_type = connection['item_type']
    node.username = connection['username']
    node.description = connection['item_description']
    node.protocol = connection['protocol']
    node.port = connection['port']
    node.auth = connection['auth']
    return node


def create_folder_node(uuid, folder: dict):
    """
    Old
    """
    children = []
    for uuid in folder['connections']:
        match folder['connections'][uuid]['item_type']:
            case 'connection':
                node = create_tree_node(uuid, folder['connections'][uuid])
                children.append(node)
            case 'folder':
                node = create_folder_node(uuid, folder['connections'][uuid])
                children.append(node)
    node = ObTreeNode(folder['item_title'], _children=children)
    node.item_type = 'folder'
    node.uuid = uuid
    return node


def create_folder_store(uuid, item_title, folder: dict):
    """
    Create a single ObListStore, creating all child ObListStores and ObTreeNodes
    """
    store = ObListStore(ObTreeNode, uuid=uuid, item_title=item_title)
    for uuid in folder['connections']:
        match folder['connections'][uuid]['item_type']:
            case 'connection':
                node = create_tree_node(uuid, folder['connections'][uuid])
                store.append(node)
            case 'folder':
                substore = create_folder_store(uuid,\
                folder['connections'][uuid]['item_title'],\
                folder['connections'][uuid])
                store.append(substore)
    return store


class ObListStore(Gio.ListStore):
    __gtype_name__ = 'ObListStore'

    """
    A ListStore for organizing the TreeListStore
    """

    def __init__(self, item_type, **kwargs):
        self.item_type = 'folder'
        self.title = kwargs['item_title']
        self.uuid = kwargs['uuid']

        super().__init__()



