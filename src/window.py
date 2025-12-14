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
from .widgets.ob_new_item_dialog import ObNewItemDialog
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

    # Sidebar related Widgets
    toggle_sidebar_btn = Gtk.Template.Child()
    obelisk_sidebar = Gtk.Template.Child()

    # print(f'obelisk_sidebar is at {obelisk_sidebar} and of type {type(obelisk_sidebar)}')

    def _new_item(self, *args):
        print('creating new item')
        new_item_dialog = ObNewItemDialog()
        new_item_dialog.present()

    def _clone_item(self, *args):
        print('cloning item')

    def _delete_item(self, *args):
        print('deleting item')

    def _connect(self, *args):
        print('establishing ssh connection')

    _actions = {
        ('new_item', _new_item),
        ('clone_item', _clone_item),
        ('delete_item', _delete_item),
        ('connect', _connect),
        ('add_item', ObConfig.add_item)
    }

    # GSettings
    _settings = Gio.Settings(schema_id='io.github.srngh.obelisk')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_action_entries(self._actions, self)

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
        self.config = ObConfig(filename=f'{home_dir}/.config/obelisk/obelisk_nested.yaml')

        obelisk_list_view = ObListView(selection_model=self.config.selection_model)

        self.obelisk_sidebar.set_content(obelisk_list_view)
        obelisk_list_view.connect('activate', self.on_sidebar_item_activated)

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
        Creates a new new in the sidebar
        Mostly for testing and debugging.
        """
        print('clicked item add button')
        list_store = self.config.selection_model.get_model().get_model()
        node = ObTreeNode('testconnection', uuid = uuid.uuid4())
        node.item_type = 'connection'
        node.username = 'bob'
        node.ip4_address = '10.1.1.1'
        node.item_description = 'added via the debug button'
        node.port = 22
        node.protocol = 'SSH'
        node.auth = 'pubkey'

        parent = self.config.get_item_parent_by_uuid('563840e6-5a1d-49b8-a530-32311034967f')
        self.config.add_item(node, parent)


    def on_new_item_action(self):
        new_item_dialog = ObNewItemDialog()
        new_item_dialog.present()
