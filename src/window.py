# window.py
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

import uuid
from pathlib import Path

from gi.repository import Adw
from gi.repository import Gio, Gtk

from .ob_config import ObConfig
from .ob_list_view import ObListView
from .widgets.ob_edit_item_dialog import ObEditItemDialog
from .widgets.ob_term import ObTerm
from .widgets.ob_tree_node import ObTreeNode
from .widgets.theme_switcher import ThemeSwitcher


@Gtk.Template(resource_path='/io/github/srngh/obelisk/window.ui')
class ObWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'ObWindow'

    # Template Elements
    split_view = Gtk.Template.Child()
    show_search_btn = Gtk.Template.Child()
    fav_btn = Gtk.Template.Child()
    fav_stack = Gtk.Template.Child()
    search_bar = Gtk.Template.Child()

    menu_btn = Gtk.Template.Child()
    tab_container = Gtk.Template.Child()
    tab_bar = Gtk.Template.Child()
    tab_view = Gtk.Template.Child()
    add_tab_btn = Gtk.Template.Child()
    save_btn = Gtk.Template.Child()

    # Sidebar related Widgets
    toggle_sidebar_btn = Gtk.Template.Child()
    obelisk_sidebar = Gtk.Template.Child()


    # GSettings
    _settings = Gio.Settings(schema_id='io.github.srngh.obelisk')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.actions = {}

        for action in [
            'new_item',
            'clone_item',
            'delete_item',
            'connect',

        ]:
            gaction = Gio.SimpleAction.new(action, None)
            gaction.connect('activate', getattr(self, f"_on_{action}_activate"))
            self.actions[action] = gaction
            self.add_action(gaction)

        # self.add_action_entries(self._actions)

        # Theme (Adapted from https://gitlab.gnome.org/tijder/blueprintgtk/)
        self.menu_btn.get_popover().add_child(ThemeSwitcher(), 'themeswitcher')

        # Restore last state
        self._settings.bind('window-width', self,
                            'default-width', Gio.SettingsBindFlags.DEFAULT)
        self._settings.bind('window-height', self,
                            'default-height', Gio.SettingsBindFlags.DEFAULT)
        self._settings.bind('window-maximized', self,
                            'maximized', Gio.SettingsBindFlags.DEFAULT)

        home_dir = Path.home()
        self.config = ObConfig(filename=f'{home_dir}/.config/obelisk/obelisk_3_write_test.yaml')

        obelisk_list_view = ObListView(selection_model=self.config.selection_model)

        self.obelisk_sidebar.set_content(obelisk_list_view)
        obelisk_list_view.connect('activate', self.on_sidebar_item_activated)

    def _on_new_item_activate(self, *args):
        self.item_dialog = ObEditItemDialog()
        self.item_dialog.connect('node_submitted', self.__on_new_item_create)
        self.item_dialog.present(self)

    def __on_new_item_create(self, dialog, node):
        del dialog
        parent = self.config.get_liststore_uuid_by_child_uuid('563840e6-5a1d-49b8-a530-32311034967f')
        self.config.add_item(node, parent)

    def _on_clone_item_activate(action, *args):
        print('cloning item')

    def _on_delete_item_activate(action, *args):
        print('deleting item')

    def _on_connect_activate(action, *args):
        print('establishing ssh connection')

    def on_sidebar_item_activated(self, list_view, index):
        """
        Spawn a SSH Connection
        """
        print(f'activated {index}')
        print(f'sidebar: {list_view}')
        # model = list_view.get_model()
        item = list_view.get_model()[index].get_item()
        term = ObTerm()

        sel_page = self.tab_view.add_page(term).set_title(item.get_item_title())
        term.spawn_ssh()

    @Gtk.Template.Callback()
    def on_add_tab_btn_clicked(self, Button):
        """
        Spawns a shell inside the flatpak.
        Mostly for testing and debugging.
        """
        print('clicked tab add button')
        term = ObTerm()
        sel_page = self.tab_view.add_page(term).set_title('local shell')
        term.spawn_sh()

    @Gtk.Template.Callback()
    def on_add_item_btn_clicked(self, Button):
        """
        Creates a new item in the sidebar
        Mostly for testing and debugging.
        """
        print('clicked item add button')
        # list_store = self.config.selection_model.get_model().get_model()
        node = ObTreeNode(name='testconnection', uuid=str(uuid.uuid4()))
        node.username = 'bob'
        node.ip4_address = '10.1.1.1'
        node.description = 'added via the debug button'
        node.port = 22
        node.protocol = 'ssh'
        node.auth = 'pubkey'

        parent = self.config.get_liststore_uuid_by_child_uuid('563840e6-5a1d-49b8-a530-32311034967f')
        self.config.add_item(node, parent)
        print(node)

        # self.config.save()

    @Gtk.Template.Callback()
    def on_save_btn_clicked(self, Button):
        """
        Writes the current configuration to a yaml file
        """
        self.config.save()

    def on_add(self, node):
        """
        Receives a newly created node and passes it to ObConfig to sort it into the tree
        """
        parent = self.config.get_liststore_uuid_by_child_uuid('563840e6-5a1d-49b8-a530-32311034967f')
        self.config.add_item(node, parent)


