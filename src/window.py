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
            'new_item',
            'remove_item',
            'connect',
            'rename',
        ]:
            gaction = Gio.SimpleAction.new(action, GLib.VariantType.new('s'))
            gaction.connect('activate', getattr(self, f'_on_{action}_activate'))
            self.actions[action] = gaction
            self.add_action(gaction)

        for action in [
            'edit_item',
            'clone_item',
        ]:
            gaction = Gio.SimpleAction.new(action, GLib.VariantType.new('as'))
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
        self.obelisk_list_view = ObListView(config=self.config)

        # Wrapping the ListView in a Bin makes the ContextMenu a better size
        adw_bin = Adw.Bin()
        adw_bin.set_child(self.obelisk_list_view)
        self.obelisk_sidebar.set_content(adw_bin)
        self.obelisk_list_view.connect('activate', self.on_sidebar_item_activated)
        
        # Connecting the last couple signals
        self.add_tab_btn.connect('clicked', self.on_add_tab_btn_clicked)
        self.save_btn.connect('clicked', self.on_save_btn_clicked)
        self.add_item_btn.connect('clicked', self.on_add_item_btn_clicked)

    def _on_new_item_activate(self, action, folder_uuid):
        """
        Callback for the win.new_item action.
        Folder Lookup has been performed in ObListView already.

        :param folder_uuid: UUID of the target folder in the sidebar
        :type folder_uuid: GVariant
        """
        try:
            self.obelisk_list_view.derefence_context_menu()
        except AttributeError:
            pass

        if folder_uuid is not None:
            # TO DO: probably faster to just pass the Object directly
            # TO DO: don't use the root list store anymore
            uuid = folder_uuid.get_string()
            if uuid != '00000000-0000-0000-0000-000000000000':
                folder = self.config.get_node_by_uuid(uuid)
            else:
                folder = ObTreeNode(name='root', uuid=uuid)

            if folder is not None:
                self.item_dialog = ObEditItemDialog(folder=folder, dialog_mode='new_node')
                self.item_dialog.connect('node_submitted', self.__on_new_item_create)
                self.item_dialog.present(self)

    def __on_new_item_create(self, dialog, node, folder):
        """
        Callback for the node_submitted Signal from ObEditItemDialog.

        :param dialog: Dialog which sends the signal
        :type dialog: ObEditItemDialog
        :param node: Node returned by the Dialog
        :type node: ObTreeNode
        :param folder: Parent Folder / ListStore of the new Node
        :type folder: ObListStore
        """
        del dialog
        self.config.add_item(node, folder)

    def _on_edit_item_activate(self, action, uuid_array):
        """
        Callback for the win.edit_item action.
        Folder Lookup has been performed in ObListView already.

        :param uuid_array: Array containing folder_uuid and node_uuid
        :type uuid_array: GLib.VariantType('as')
        """
        try:
            self.obelisk_list_view.derefence_context_menu()
        except AttributeError:
            pass

        folder = None
        node = None
        if uuid_array is not None:
            string_list = uuid_array.get_strv()
            folder_uuid = string_list[0]
            node_uuid = string_list[1]

        if folder_uuid != '00000000-0000-0000-0000-000000000000':
            folder = self.config.get_node_by_uuid(folder_uuid)
        else:
            folder = ObTreeNode(name='root', uuid=uuid)

        if node_uuid != '':
            node = self.config.get_node_by_uuid(node_uuid)

        # Folders are not editable for now, until inheritance of parameters is implemented
        if folder is not None and node is not None and not node.is_folder:
            self.item_dialog = ObEditItemDialog(folder=folder, node=node, dialog_mode='edit_node')
            # self.item_dialog.connect('node_submitted', self.__on_new_item_create)
            self.item_dialog.present(self)

    def _on_clone_item_activate(self, action, uuid_array):
        """
        Callback for the win.clone_item action.
        Folder Lookup has been performed in ObListView already.

        :param uuid_array: Array containing folder_uuid and node_uuid
        :type uuid_array: GLib.VariantType('as')
        """
        try:
            self.obelisk_list_view.derefence_context_menu()
        except AttributeError:
            pass

        folder = None
        node = None
        if uuid_array is not None:
            string_list = uuid_array.get_strv()
            folder_uuid = string_list[0]
            node_uuid = string_list[1]

        if folder_uuid != '00000000-0000-0000-0000-000000000000':
            folder = self.config.get_node_by_uuid(folder_uuid)
        else:
            folder = ObTreeNode(name='root', uuid=uuid)

        if node_uuid != '':
            node = self.config.get_node_by_uuid(node_uuid)

        # Folders are not editable for now, until inheritance of parameters is implemented
        if folder is not None and node is not None and not node.is_folder:
            self.item_dialog = ObEditItemDialog(folder=folder, node=node, dialog_mode='clone_node')
            self.item_dialog.connect('node_submitted', self.__on_new_item_create)
            self.item_dialog.present(self)

    def _on_rename_activate(self, action, node_uuid):
        """
        Callback for the win.rename_item action.

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
        dialog = ObRenameItemDialog(self, node)

        dialog.connect('renamed', self._on_item_renamed)

        dialog.present()

        print('renaming item')

    def _on_item_renamed(self, dialog, node, name):
        """
        Convenience function for renaming an item from a dialog.

        :param dialog: The dialog calling this method.
        :type dialog: Gtk.Dialog
        :param node: The node to be renamed
        :type node: ObTreeNode
        :param name: New name for the node
        :type name: str
        """
        dialog.destroy()
        node.name = name

    def _on_remove_item_activate(self, action, node_uuid):
        """
        Callback for the win.delete_item action.

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
        self.config.remove_item(node)

    def _on_connect_activate(self, action, *args):
        print('establishing ssh connection')
        print(args)

    def on_sidebar_item_activated(self, list_view, index):
        """
        Spawn a SSH Connection

        TO DO: Clean up this mess
        """
        # print(f'activated {index}')
        # print(f'sidebar: {list_view}')
        item = list_view.get_model()[index].get_item()
        term = ObTerm()

        page = self.tab_view.add_page(term)
        page.set_title(item.name)

        ssh_command = ['/usr/bin/ssh', f'{item.username}@{item.ip4_address}', '-p', f'{item.port}']

        term._page = page

        term.spawn_async(
            Vte.PtyFlags.DEFAULT,
            None,
            ssh_command,
            None,
            GLib.SpawnFlags.DO_NOT_REAP_CHILD,
            None,
            None,
            -1,
            None,
            self.on_terminal_spawn,
            None
        )

    def on_terminal_spawn(self, terminal, pid, error, *args):
        """
        Triggered on Terminal spawn.
        """
        if error:
            print(f'error: {error.message}')
        else:
            terminal.watch_child(pid)
            terminal.connect('child-exited', self.on_command_exited)
            # terminal.connect('selection-changed', self.on_selection_changed)

    def on_command_exited(self, terminal, status):
        print(status)
        print(f'ssh exited')
        self.tab_view.close_page(terminal._page)


    def on_sidebar_item_activated_old(self, list_view, index):
        """
        Spawn a SSH Connection

        TO DO: Clean up this mess
        """
        print(f'activated {index}')
        print(f'sidebar: {list_view}')
        # model = list_view.get_model()
        item = list_view.get_model()[index].get_item()
        term = ObTerm()

        sel_page = self.tab_view.add_page(term).set_title(item.name)
        term.spawn_ssh()


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

        sel_page = self.tab_view.add_page(term).set_title('local shell')
        term.spawn_sh()
        term.grab_focus()

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

