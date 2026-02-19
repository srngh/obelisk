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
from .config_file_handlers.connection_types.folder import Folder
from .config_file_handlers.connection_types.item import Item
from .widgets.ob_list_store import ObListStore
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
        # print(self.filename)

        default_handler = ConfigFileHandlerFactory().create_handler('obelisk', self.filename)

        default_handler.load_config()

        print(default_handler.connections)
        self.ob_list_store_model = merge_configs(default_handler.connections)
        default_handler.print_config()

        tree_list_model = Gtk.TreeListModel.new(
            self.ob_list_store_model, False, True, self.__tree_model_create_func
        )
        self.selection_model = Gtk.SingleSelection(model=tree_list_model)

        # These are tests and will be removed once the datamodel functions properly
        # Tests if a ObTreeNode can be accessed via its UUID
        # test_node_1 = self.__get_node_by_uuid('9f7bfcbc-93e0-47cc-ad56-28a59de8927e')
        # print(f'{test_node_1} has UUID {test_node_1.uuid}')

        # Tests if a ObListStore can be accessed via its UUID
        # test_list_store_1 = self.__get_liststore_by_uuid('3bf1a021-0e72-47d8-bac1-6ceafd64ab3b')
        # print(f'{test_list_store_1} has UUID {test_list_store_1.uuid}')

        # Tests if a ObListStore can be accessed via a child nodes UUID
        # test_list_store_2 = self.__get_liststore_by_node_uuid('563840e6-5a1d-49b8-a530-32311034967f')
        # print(f'{test_list_store_2} has UUID {test_list_store_2.uuid}')

        # Tests if a ObListStores UUID can be resolved from a child nodes UUID
        # test_uuid = '3bf1a021-0e72-47d8-bac1-6ceafd64ab3b'
        # test_list_store_uuid = self.__get_liststore_uuid_by_child_uuid(test_uuid)
        # print(f'{test_uuid} has parent UUID {test_list_store_uuid}')

    def __tree_model_create_func(self, item):
        """
        This builds the Gtk.TreeListModel.
        """
        if isinstance(item, ObTreeNode):
            return None
        else:
            child_model = ObListStore(name=item.name, uuid=item.uuid)
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
            {list_store.get_item(index).get_item().name}\
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

    def __get_liststore_uuid_by_child_uuid(self, uuid):
        list_store = self.ob_list_store_model
        return get_liststore_uuid_by_child_uuid(list_store, uuid)


def get_node_by_uuid(store, uuid):
    """
    The recursive part of resolving the index of a connection items by uuid
    This will return either a ObTreeNode or ObListStore.
    """
    for index in range(store.get_n_items()):
        child = store.get_item(index)
        if child.uuid == uuid:
            return child
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


def get_liststore_uuid_by_child_uuid(list_store, uuid):
    """
    Returns the parent ObListStore UUID by a child ObTreeNodes or ObListStores UUID
    """
    for index in range(list_store.get_n_items()):
        child = list_store.get_item(index)
        if child.uuid == uuid:
            return list_store.uuid
        elif isinstance(child, ObListStore):
            return get_liststore_uuid_by_child_uuid(child, uuid)


def debug_ob_store(store):
    """
    This is a debugging / testing method.
    The recursive part of parent_list_storeviewing the TreeModel.
    """
    for index in range(store.get_n_items()):
        child = store.get_item(index)
        print(f'Object {child.name} has {index} items, has uuid {child.uuid} and is type {child.item_type}')
        if isinstance(child, ObListStore):
            debug_ob_store(child)


def merge_configs(connections):
    """
    Create a ObListStore, each containing either more ObListStores or ObTreeNodes.
    Only ObListStores can contain ObTreeNodes.
    ObTreeNodes will never have child objects.
    """
    ob_list_store_model = ObListStore(
        'root',
        '00000000-0000-0000-0000-000000000000'
    )
    # print(connections)
    for item in connections:
        if isinstance(item, Item):
            node = create_tree_node(item)
            ob_list_store_model.append(node)
        if isinstance(item, Folder):
            substore = create_folder_store(
                item)
            ob_list_store_model.append(substore)
    return ob_list_store_model


def create_tree_node(item: Item):
    """
    Create a single ObTreeNode, containing all neccessary data
    """
    node = ObTreeNode(
        name=item.name,
        uuid=item.uuid,
        ip4_address=item.ip4_address,
        username=item.username,
        description=item.description,
        protocol=item.protocol,
        port=item.port,
        auth=item.auth
    )
    return node


def create_folder_store(folder: Folder):
    """
    Create a single ObListStore, creating all child ObListStores and ObTreeNodes
    """
    store = ObListStore(name=folder.name, uuid=folder.uuid)
    for item in folder.connections:
        if isinstance(item, Item):
            node = create_tree_node_new(item)
            store.append(node)
        if isinstance(item, Folder):
            substore = create_folder_store_new(
                item)
            store.append(substore)
    return store

