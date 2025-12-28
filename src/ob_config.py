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
    """
    This class holds the configuration of a loaded config file.
    """

    __gsignals__ = {
        'item-added': (GObject.SignalFlags.RUN_FIRST, None, (ObTreeNode,)),
    }

    def __init__(self, filename=None, **kwargs):
        super().__init__(**kwargs)
        self.autosave = False
        self.filename = filename
        self.config_type = 'obelisk'
        print(self.filename)
        default_handler = ConfigFileHandlerFactory().create_handler('obelisk')
        default_handler.load_connections(self.filename)
        self.items = default_handler.to_str()

        self.ob_list_store_model = parse_items(self.items)

        tree_list_model = Gtk.TreeListModel.new(
            self.ob_list_store_model, False, True, self.__tree_model_create_func
        )
        self.selection_model = Gtk.SingleSelection(model=tree_list_model)

        # self.__tree_model_debug_func()
        list_store = get_liststore_uuid_by_node_uuid(self.selection_model.get_model().get_model(), 'be50f325-4cd0-4f6c-bbc6-2ae43dd90eb5')
        print(f'{list_store} has UUID {list_store.uuid}')

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
        """
        if isinstance(item, ObTreeNode):
            return None
        else:
            child_model = ObListStore(title=item.title, uuid=item.uuid)
            for index in range(item.get_n_items()):
                child_model.append(item.get_item(index))
            return child_model

    def __tree_model_debug_func(self):
        """
        This is a debugging / testing method.
        For viewing the TreeModel.
        """
        list_store = self.selection_model.get_model().get_model()
        debug_ob_store(list_store)

    def get_tree_row_index_by_uuid(self, uuid):
        """
        This is a debugging / testing method.
        Probably a hack.
        """
        list_store = self.selection_model.get_model()  # Just plain ugly
        for index in range(list_store.get_n_items()):
            print(f'Index {index}\
            {list_store.get_item(index).get_item().title}\
            {list_store.get_item(index).get_item().uuid}')

    def add_item(self, node, parent_uuid):
        """
        Pass an ObTreeNode and the parents UUID
        """
        list_store = self.__get_liststore_by_uuid(parent_uuid)
        list_store.append(node)

    def __get_node_by_uuid(self, uuid):
        list_store = self.ob_list_store_model
        return get_node_by_uuid(list_store, uuid)

    def __get_liststore_by_uuid(self, uuid):
        list_store = self.ob_list_store_model
        return get_liststore_by_uuid(list_store, uuid)

    def __get_liststore_by_node_uuid(self, uuid):
        list_store = self.ob_list_store_model
        return get_liststore_by_node_uuid(list_store, uuid)

    def __get_liststore_uuid_by_node_uuid(self, uuid):
        list_store = self.ob_list_store_model
        return get_liststore_uuid_by_node_uuid(list_store, uuid)


def get_node_by_uuid(store, uuid):
    """
    The recursive part of resolving the index of a connection items by uuid
    """
    for index in range(store.get_n_items()):
        child = store.get_item(index)
        if child.uuid == uuid:
            return index
        elif isinstance(child, ObListStore):
            return get_node_by_uuid(child, uuid)


def get_liststore_by_uuid(list_store, uuid):
    """
    Returns an ObListStore by its UUID
    """
    if list_store.uuid == uuid:
        return list_store
    else:
        for index in range(list_store.get_n_items()):
            child = list_store.get_item(index)
            if isinstance(child, ObListStore) and child.uuid == uuid:
                return child
            elif isinstance(child, ObListStore):
                return get_liststore_by_uuid(child, uuid)


def get_liststore_by_node_uuid(list_store, uuid):
    """
    Returns the parent ObListStore by a child ObTreeNodes UUID
    """
    for index in range(list_store.get_n_items()):
        child = list_store.get_item(index)
        if child.uuid == uuid:
            return list_store
        elif isinstance(child, ObListStore):
            return get_liststore_by_node_uuid(child, uuid)


def get_liststore_uuid_by_node_uuid(list_store, uuid):
    """
    Returns the parent ObListStore UUID by a child ObTreeNodes UUID
    """
    for index in range(list_store.get_n_items()):
        child = list_store.get_item(index)
        if child.uuid == uuid:
            return list_store.uuid()
        elif isinstance(child, ObListStore):
            return get_liststore_uuid_by_node_uuid(child, uuid)


def debug_ob_store(store):
    """
    This is a debugging / testing method.
    The recursive part of parent_list_storeviewing the TreeModel.
    """
    for index in range(store.get_n_items()):
        child = store.get_item(index)
        print(f'Object {child.title} has {index} items, has uuid {child.uuid} and is type {child.item_type}')
        if isinstance(child, ObListStore):
            debug_ob_store(child)


def parse_items(connections: dict):
    """
    Create a ObListStore, each containing either more ObListStores or ObTreeNodes.
    Only ObListStores can contain ObTreeNodes.
    ObTreeNodes will never have child objects.
    ObTreeNodes may be empty.
    """
    ob_list_store_model = ObListStore(
        'root',
        '00000000-0000-0000-0000-000000000000'
    )
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
    node = ObTreeNode(connection['item_title'], uuid)
    node.ip4_address = connection['ip4_address']
    node.item_type = connection['item_type']
    node.username = connection['username']
    node.description = connection['item_description']
    node.protocol = connection['protocol']
    node.port = connection['port']
    node.auth = connection['auth']
    return node


def create_folder_store(uuid, item_title, folder: dict):
    """
    Create a single ObListStore, creating all child ObListStores and ObTreeNodes
    """
    store = ObListStore(title=item_title, uuid=uuid)
    for uuid in folder['connections']:
        match folder['connections'][uuid]['item_type']:
            case 'connection':
                node = create_tree_node(uuid, folder['connections'][uuid])
                store.append(node)
            case 'folder':
                substore = create_folder_store(
                    uuid,
                    folder['connections'][uuid]['item_title'],
                    folder['connections'][uuid])
                store.append(substore)
    return store


class ObListStore(Gio.ListStore):
    __gtype_name__ = 'ObListStore'

    """
    A ListStore for organizing the TreeListStore
    """

    def __init__(self, title: str, uuid: str):
        self.item_type = ObTreeNode
        self._title = title
        self._uuid = uuid

        super().__init__()

    @GObject.Property(type=str)
    def title(self) -> str:
        return self._title

    @GObject.Property(type=str)
    def uuid(self) -> str:
        return self._uuid

