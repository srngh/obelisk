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

from .widgets.sidebar_item import SidebarItem
from .widgets.theme_switcher import ThemeSwitcher

from .widgets.obelisk_term import ObeliskTerm

from .config_loaders.config_loader import ConfigLoaderFactory
# from .obeliskSSH import ObeliskSSHClient, open_shell

from .obelisk_list_view import ObeliskListView

@Gtk.Template(resource_path='/org/gnome/obelisk/window.ui')
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

    #GSettings
    _settings = Gio.Settings(schema_id="org.gnome.obelisk")
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

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
        defaultLoader = ConfigLoaderFactory().create_loader("obelisk")
        defaultLoader.load_connections("/home/soeren/.config/obelisk/obelisk_nested.yaml")

        self.items = defaultLoader.to_str()

        # self.connections = Gio.ListStore()

        '''
        for i in self.items:
            self.connections.append
        '''

        # pprint(self.items)
        """
        self.items = {
            "1234-00": {
                "item_title": "server-1",
                "item_type": "connection",
                "item_description": "server 1",
                "icon_name": "package-x-generic-symbolic",
            },
            "1234-02": {
                "item_title": "server-2",
                "item_type": "connection",
                "item_description": "server 2",
                "icon_name": "package-x-generic-symbolic",
            },
        }
        """
        obelisk_list_view = ObeliskListView(items=self.items)
        #obelisk_list_view.set_config(config=self.config)
        self.obelisk_sidebar.set_content(obelisk_list_view)

        # Populate sidebar

        """
        for i in self.items:
            self.sidebar.append(SidebarItem(
                item_uuid=self.items[i],
                item_title=self.items[i]["item_title"],
                item_type=self.items[i]["item_type"],
                item_description=self.items[i]["item_description"],
                icon_name=self.items[i]["icon_name"])
            )

        self.sidebar.connect('row-activated', self.on_sidebar_item_activated)
        """
    # Spawn a Terminal
    def on_sidebar_item_activated(self, sidebar, sidebar_item):
        print(f"activated {sidebar_item.get_item_title()}")
        term = ObeliskTerm()

        sel_page = self.tab_view.add_page(term).set_title(sidebar_item.get_item_title())
        term.spawn_ssh()

        #con = ObeliskSSHClient()
        #con.load_system_host_keys()
        # IP =
        # user =
        # pw =
        #con.connect(IP, username=user, password=pw)
        #term.spawn_ssh(open_shell(con))


    @Gtk.Template.Callback()
    def on_tab_add_btn_clicked(self, Button):
        """
        This is a testing button, which spawns a shell inside the flatpak.
        Mostly for testing and debugging.
        """
        print("clicked tab add button")
        term = ObeliskTerm()
        sel_page = self.tab_view.add_page(term).set_title("local shell")
        term.spawn_sh()
        term.watch_child()

