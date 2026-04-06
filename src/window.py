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

import os
import uuid
from pathlib import Path

from gi.repository import Adw
from gi.repository import GLib, Gio, Gtk, Vte

from .ob_config import ObConfig
from .ob_list_view import ObListView
from .widgets.ob_edit_item_dialog import ObEditItemDialog
from .widgets.ob_term import ObTerm
from .widgets.ob_tree_node import ObTreeNode
from .widgets.ob_rename_item_dialog import ObRenameItemDialog
from .widgets.theme_switcher import ThemeSwitcher


@Gtk.Template(resource_path='/io/github/srngh/obelisk/window.ui')
class ObWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'ObWindow'

    # Template Elements
    # split_view = Gtk.Template.Child()
    ob_paned = Gtk.Template.Child()
    # show_search_btn = Gtk.Template.Child() # needed?
    # fav_btn = Gtk.Template.Child() # needed?
    fav_stack = Gtk.Template.Child() 
    search_bar = Gtk.Template.Child()

    menu_btn = Gtk.Template.Child()
    tab_view = Gtk.Template.Child()
    add_tab_btn = Gtk.Template.Child()
    save_btn = Gtk.Template.Child()
    add_item_btn = Gtk.Template.Child()

    # Sidebar related Widgets
    toggle_sidebar_btn = Gtk.Template.Child()
    obelisk_sidebar = Gtk.Template.Child()


    # GSettings
    _settings = Gio.Settings(schema_id='io.github.srngh.obelisk')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Sidebar stuff
        self.obelisk_sidebar.set_size_request(230, -1)
        self.ob_paned.set_shrink_start_child(False)
        self.ob_paned.set_resize_start_child(False)
        self.MAX_SIDEBAR_WIDTH = 350
        self.ob_paned.set_position(230)
        
        self.ob_paned.connect('notify::position', self.on_paned_position_changed)
        self._saved_sidebar_width = self.ob_paned.get_position()
        self.toggle_sidebar_btn.connect('toggled', self.on_toggle_sidebar_clicked)
        
        # Actions
        self.actions = {}

        for action in [
            'connect',
        ]:
            gaction = Gio.SimpleAction.new(action, GLib.VariantType.new('s'))
            gaction.connect('activate', getattr(self, f'_on_{action}_activate'))
            self.actions[action] = gaction
            self.add_action(gaction)


        # Theme (Adapted from https://gitlab.gnome.org/tijder/blueprintgtk/)
        self.menu_btn.get_popover().add_child(ThemeSwitcher(), 'themeswitcher')

        # Restore last state
        self._settings.bind('window-width', self,
                            'default-width', Gio.SettingsBindFlags.DEFAULT)
        self._settings.bind('window-height', self,
                            'default-height', Gio.SettingsBindFlags.DEFAULT)
        self._settings.bind('window-maximized', self,
                            'maximized', Gio.SettingsBindFlags.DEFAULT)

        # Config loading logic, pretty bad atm
        home_dir = Path.home()
        self.config = ObConfig(filename=f'{home_dir}/.config/obelisk/config_write_test.yaml')

        # Wrapping the ListView in a Bin makes the ContextMenu a better size
        adw_bin = Adw.Bin()
        adw_bin.set_child(ObListView(config=self.config, parent=adw_bin))
        self.obelisk_list_view = adw_bin.get_child()
        self.obelisk_sidebar.set_content(adw_bin)
        self.obelisk_list_view.connect('activate', self.on_sidebar_item_activated)
        
        # Connecting the last couple signals
        self.add_tab_btn.connect('clicked', self.on_add_tab_btn_clicked)
        self.save_btn.connect('clicked', self.on_save_btn_clicked)
        self.add_item_btn.connect('clicked', self.on_add_item_btn_clicked)


    def _on_connect_activate(self, action, node_uuid):
        """
        Callback for the win.connect Signal action. Spawns a simple SSH Session.

        :param action: The action calling this method.
        :type action: Gio.SimpleAction(GLib.VariantType('s'))
        :param node_uuid: The UUID of the node.
        :type node_uuid: GLib.VariantType('s')
        """
        try:
            self.obelisk_list_view.derefence_context_menu()
        except AttributeError:
            pass

        node = self.config.get_node_by_uuid(node_uuid.get_string())

        if not node.is_folder:
            term = ObTerm()
            term.spawn_ssh_session(node, self.tab_view)
            term.grab_focus()

    def on_sidebar_item_activated(self, list_view, index):
        """
        Signal Callback for obelisk_list_view.activate.

        :param list_view: The ListView calling this method
        :type list_view: ObListView
        :param index: The index of the activated item
        :type index: int
        """
        item = list_view.get_model()[index].get_item()

        if not item.is_folder:
            term = ObTerm()
            term.spawn_ssh_session(item, self.tab_view)
            term.grab_focus()

    # Sidebar UI Callbacks

    def on_save_btn_clicked(self, Button):
        """
        Writes the current configuration to a yaml file

        :param Button: The Button from which this callback is invoked
        :type Button: Gtk.Button
        """
        self.config.save()

    def on_toggle_sidebar_clicked(self, button):
        if self.obelisk_sidebar.get_visible():
            self._saved_sidebar_width = self.ob_paned.get_position()
            self.obelisk_sidebar.set_visible(False)
        else:
            self.obelisk_sidebar.set_visible(True)
            self.ob_paned.set_position(self._saved_sidebar_width)

    def on_paned_position_changed(self, paned, param_spec):
        """
        Caps the maximum position of the draggable separator.
        """
        current_position = paned.get_position()

        if current_position > self.MAX_SIDEBAR_WIDTH:
            # If the user drags it too far right, force it back to the maximum
            paned.set_position(self.MAX_SIDEBAR_WIDTH)

    # Testing / Debugging

    def on_add_tab_btn_clicked(self, Button):
        """
        Spawns a shell inside the flatpak.
        Mostly for testing and debugging.
        """
        print('clicked tab add button')

        term = ObTerm()

        term.spawn_bash(self.tab_view)
        term.grab_focus()

    # remove this on next commit. item creation is stable enough already
    def on_add_item_btn_clicked(self, Button):
        """
        Creates a new item in the sidebar
        Mostly for testing and debugging, this is pretty hacky atm.
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

        parent = self.config.get_folder_by_child_uuid('563840e6-5a1d-49b8-a530-32311034967f')
        self.config.add_item(node, parent)
        print(node)

