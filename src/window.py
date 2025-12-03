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

from pprint import pprint

from gi.repository import Adw
from gi.repository import Gtk, Gio, Vte

from .widgets.theme_switcher import ThemeSwitcher

from .widgets.obelisk_term import ObeliskTerm

from .config_file_handlers.config_file_handler import ConfigFileHandlerFactory

from .obelisk_list_view import ObeliskListView

from .widgets.obelisk_new_item_dialog import ObeliskNewItemDialog

@Gtk.Template(resource_path='/io/github/srngh/obelisk/window.ui')
class ObeliskWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'ObeliskWindow'

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

    def _new_item(self, *args):
        print("creating new item")
        new_item_dialog = ObeliskNewItemDialog()
        new_item_dialog.present()


    def _clone_item(self, *args):
        print("cloning item")

    def _delete_item(self, *args):
        print("deleting item")

    def _connect(self, *args):
        print("establishing ssh connection")

    _actions = {
        ("new_item", _new_item),
        ("clone_item", _clone_item),
        ("delete_item", _delete_item),
        ("connect", _connect)
    }

    #GSettings
    _settings = Gio.Settings(schema_id="io.github.srngh.obelisk")
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_action_entries(self._actions, self)

        # Theme (Adapted from https://gitlab.gnome.org/tijder/blueprintgtk/)
        self.menu_btn.get_popover().add_child(ThemeSwitcher(), "themeswitcher")

        # Restore last state
        self._settings.bind("window-width", self,
                            "default-width", Gio.SettingsBindFlags.DEFAULT)
        self._settings.bind("window-height", self,
                            "default-height", Gio.SettingsBindFlags.DEFAULT)
        self._settings.bind("window-maximized", self,
                            "maximized", Gio.SettingsBindFlags.DEFAULT)

        # Load a sample config
        default_handler = ConfigFileHandlerFactory().create_handler("obelisk")
        default_handler.load_connections("/home/soeren/.config/obelisk/obelisk_nested.yaml")

        self.items = default_handler.to_str()

        obelisk_list_view = ObeliskListView(items=self.items)
        self.obelisk_sidebar.set_content(obelisk_list_view)
        obelisk_list_view.connect('activate', self.on_sidebar_item_activated)



    def on_sidebar_item_activated(self, list_view, index):
        """
        Spawn a SSH Connection
        """
        print(f"activated {index}")
        print(f"sidebar: {list_view}")
        model = list_view.get_model()
        item = list_view.get_model()[index].get_item()
        term = ObeliskTerm()

        sel_page = self.tab_view.add_page(term).set_title(item.get_item_title())
        term.spawn_ssh()


    @Gtk.Template.Callback()
    def on_tab_add_btn_clicked(self, Button):
        """
        Spawns a shell inside the flatpak.
        Mostly for testing and debugging.
        """
        print("clicked tab add button")
        term = ObeliskTerm()
        sel_page = self.tab_view.add_page(term).set_title("local shell")
        term.spawn_sh()
        #term.watch_child()

    def on_new_item_action(self):
        new_item_dialog = ObeliskNewItemDialog()
        new_item_dialog.present()
