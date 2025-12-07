# obelisk_config.py
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

from gi.repository import GObject, Gio, Gdk, Gtk

from .config_file_handlers.config_file_handler import ConfigFileHandlerFactory

from .widgets.ob_tree_expander import ObTreeExpander

class ObConfig(GObject.Object, Gio.ListModel):
    __gtype_name__ = "ObConfig"
    "This class holds the configuration of a loaded config file."

    '''
    __gsignals__ = {
        "changed": (GObject.SignalFlags.RUN_FIRST, None, ()) <<<<---- what it do?
        "": asdf
    }
    '''
    def __init__(self, filename=None, **kwargs):
        super().__init__(**kwargs)
        self.autosave = False
        self.filename = filename
        self.config_type = 'obelisk'
        print(self.filename)
        default_handler = ConfigFileHandlerFactory().create_handler("obelisk")
        default_handler.load_connections(self.filename)
        self.items = default_handler.to_str()

        tree_model = parse_items(self.items)
        tree_list_model = Gtk.TreeListModel.new(
            tree_model, False, True, self.__tree_model_create_func
        )
        self.selection_model = Gtk.SingleSelection(model=tree_list_model)

    def __tree_model_create_func(self, item):
        if item.children == []:
            return None
        child_model = Gio.ListStore.new(ObTreeNode)
        for child in item.children:
            child_model.append(child)
        return child_model

def parse_items(connections: dict):
    tree_model = Gio.ListStore.new(ObTreeNode)
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
    node = ObTreeNode(connection["item_title"])
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
    node = ObTreeNode(folder["item_title"], _children=children)
    node.item_type = "folder"
    return node

class ObTreeNode(GObject.GObject):
    def __init__(self, _title, _children=None):
        super().__init__()
        self.children = _children or []
        self.title = _title

    def get_item_title(self):
        return self.title
