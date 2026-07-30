# window.py
#
# Copyright 2026 simhof
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

from gi.repository import Adw
from gi.repository import GLib, Gio, Gtk

from .ob_db_list_view import ObDBListView
from .widgets.ob_term import ObTerm
from .widgets.theme_switcher import ThemeSwitcher


@Gtk.Template(resource_path='/io/github/srngh/obelisk/window.ui')
class ObWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'ObWindow'

    # Template Elements
    ob_paned = Gtk.Template.Child()
    show_search_btn = Gtk.Template.Child()
    search_entry = Gtk.Template.Child()

    menu_btn = Gtk.Template.Child()
    tab_view = Gtk.Template.Child()
    add_tab_btn = Gtk.Template.Child()
    save_btn = Gtk.Template.Child()

    # Sidebar related Widgets
    toggle_sidebar_btn = Gtk.Template.Child()
    obelisk_sidebar = Gtk.Template.Child()
    obelisk_sidebar_viewstack = Gtk.Template.Child()


    # GSettings
    _settings = Gio.Settings(schema_id='io.github.srngh.obelisk')

    def __init__(self, config=None, **kwargs):
        super().__init__(**kwargs)

        self.config = config

        # Sidebar dimensions
        self.obelisk_sidebar.set_size_request(230, -1)
        self.ob_paned.set_shrink_start_child(False)
        self.ob_paned.set_resize_start_child(False)
        self.MAX_SIDEBAR_WIDTH = 350
        self.ob_paned.set_position(230)

        self.ob_paned.connect('notify::position', self.on_paned_position_changed)
        self._saved_sidebar_width = self.ob_paned.get_position()
        self.toggle_sidebar_btn.connect('toggled', self.on_toggle_sidebar_clicked)

        self.search_entry.connect('search-changed', self.on_search_changed)

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

        # Wrapping the ListView in a Bin makes the ContextMenu a better size
        ob_list_view_bin = Adw.Bin()
        scrolled_window = Gtk.ScrolledWindow.new()
        ob_list_view_bin.set_child(scrolled_window)
        self.obelisk_list_view = ObDBListView(config=self.config, parent=ob_list_view_bin)
        self.obelisk_list_view.connect('activate', self.on_sidebar_item_activated)
        scrolled_window.set_child(self.obelisk_list_view)

        self.obelisk_sidebar_viewstack.add_named(ob_list_view_bin, "tree")

        self.search_list_box = Gtk.ListBox.new()
        ob_search_list_box_bin = Adw.Bin()
        ob_search_list_box_bin.set_child(Gtk.ScrolledWindow.new())
        ob_search_list_box_bin.get_child().set_child(self.search_list_box)

        self.obelisk_sidebar_viewstack.add_named(ob_search_list_box_bin, "search")

        self.obelisk_sidebar_viewstack.set_visible_child_name("tree")

        # Connecting the last couple signals
        self.add_tab_btn.connect('clicked', self.on_add_tab_btn_clicked)
        self.save_btn.connect('clicked', self.on_save_btn_clicked)

        # Search related
        self._search_timeout_id = None
        self.search_list_box.connect("row-activated", self.on_row_activated)

        # Shortcut Things
        self.shortcut_controller = Gtk.ShortcutController.new()
        self.shortcut_controller.set_scope(Gtk.ShortcutScope.GLOBAL)
        self.add_controller(self.shortcut_controller)

        self._setup_keybinds()

    def _setup_keybinds(self):
        """
        Helper Method for adding all global keyboard shortcuts.
        """
        self._add_shortcut("<Ctrl>f", self.__on_shortcut_focus_search)

    def _add_shortcut(self, accel_string, callback):
        """
        Create a shortcut and add it to the window's shortcut controller.
        """
        trigger = Gtk.ShortcutTrigger.parse_string(accel_string)
        action = Gtk.CallbackAction.new(callback)
        shortcut = Gtk.Shortcut.new(trigger, action)

        self.shortcut_controller.add_shortcut(shortcut)

    def __on_shortcut_focus_search(self, widget, args):
        """
        Callback for <Ctrl>f shortcut. Toggles the show_search_btns active state.
        The SearchBars search-mode-enabled is bound to the show_search_btns active state.
        """
        active = self.show_search_btn.get_active()
        self.show_search_btn.set_active(not active)
        return True


    def on_search_changed(self, entry):
        if self._search_timeout_id:
            GLib.source_remove(self._search_timeout_id)

        self._search_timeout_id = GLib.timeout_add(
            250, self._perform_search, entry.get_text().strip()
        )

    def _perform_search(self, query):
        """
        Query database for matching names
        """
        self._search_timeout_id = None

        if not query:
            self._clear_list_box()
            self.obelisk_sidebar_viewstack.set_visible_child_name("tree")
            return False

        self.obelisk_sidebar_viewstack.set_visible_child_name("search")
        self._clear_list_box()

        # TODO: Perform consecutive searches, when there are more the x=100 results
        cursor = self.config.db_handler.conn.cursor()
        cursor.execute(
            "SELECT uuid, name, is_folder FROM connections WHERE name LIKE ?", (f"%{query}%",)
        )
        results = cursor.fetchall()

        for uuid, name, is_folder in results:
            row = self._create_result_row(uuid, name, is_folder)
            self.search_list_box.append(row)

    def _create_result_row(self, uuid, name, is_folder):
        """
        Creates a ListBoxRow for the Search ListBox.
        """
        row = Gtk.ListBoxRow()
        box = Gtk.Box.new(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        row.set_child(box)

        row.uuid = uuid
        row.is_folder = is_folder

        if not is_folder:
            image = Gtk.Image.new_from_icon_name('org.gnome.Terminal-symbolic')
        else:
            image = Gtk.Image.new_from_icon_name('folder-closed-symbolic')
            image.add_css_class("folder")

        box.append(image)

        label = Gtk.Label(label=name, xalign=0)

        box.append(label)
        return row

    def _clear_list_box(self):
        """
        Remove all rows from the Search ListBox.
        """
        while True:
            row = self.search_list_box.get_row_at_index(0)
            if row is None:
                break
            self.search_list_box.remove(row)

    def on_row_activated(self, list_box, row):
        """
        Callback for the row-activated Signal of the search ListBox.
        """
        if row and not row.is_folder:
            node = self.config.get_node_by_uuid(row.uuid)
            term = ObTerm(db_handler=self.config.db_handler)
            term.spawn_go_ssh_session(node, self.tab_view)
            term.grab_focus()


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
            term = ObTerm(db_handler=self.config.db_handler)
            term.spawn_go_ssh_session(node, self.tab_view)
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
            term = ObTerm(db_handler=self.config.db_handler)
            term.spawn_go_ssh_session(item, self.tab_view)
            term.grab_focus()
        else:
            row = self.config.tree_list_model.get_row(index)
            expanded_state = row.get_expanded()
            row.set_expanded(not expanded_state)


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

        term = ObTerm(db_handler=self.config.db_handler)

        term.spawn_sh(self.tab_view)
        term.grab_focus()

