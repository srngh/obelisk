# obelisk_term.py
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

import os
import json
import tempfile

import gi

gi.require_version('Vte', '3.91')

from gi.repository import Adw, GLib, Gdk, Gtk, Vte


class ObTerm(Vte.Terminal):
    __gtype_name__ = 'ObTerm'

    def __init__(self, db_handler=None, **kwargs):
        super().__init__(**kwargs)
        self.db_handler = db_handler
        # print(self.db_handler.db_path)
        self.style_manager = Adw.StyleManager.get_default()
        self._theme_signal_id = self.style_manager.connect('notify::dark', self.__on_theme_changed)
        self.update_colors()
        self.connect('destroy', self.__on_destroy)

        key_controller = Gtk.EventControllerKey.new()
        key_controller.connect('key-pressed', self._on_key_press)
        self.add_controller(key_controller)

    def __on_theme_changed(self, manager, param):
        self.update_colors()

    def update_colors(self):
        is_dark = self.style_manager.get_dark()
        if is_dark:
            bg = self._hex_to_rgba('#1d1d20')
            fg = self._hex_to_rgba('#ffffff')
            palette = [
                '#241f31', '#c01c28', '#2ec27e', '#f5c211',
                '#51a1ff', '#9841bb', '#0ab9dc', '#c0bfbc',
                '#5e5c64', '#ed333b', '#57e389', '#f8e45c',
                '#51a1ff', '#c061cb', '#4fd2fd', '#f6f5f4'
            ]
        else:
            bg = self._hex_to_rgba('#ffffff')
            fg = self._hex_to_rgba('#171421')
            palette = [
                '#241f31', '#c01c28', '#2ec27e', '#e8b504',
                '#1e78e4', '#9841bb', '#0ab9dc', '#c0bfbc',
                '#5e5c64', '#ed333b', '#4ad67c', '#d2be36',
                '#51a1ff', '#c061cb', '#4fd2fd', '#f6f5f4'
            ]
        palette_rgba = [self._hex_to_rgba(hex_color) for hex_color in palette]
        self.set_colors(foreground=fg, background=bg, palette=palette_rgba)

    def __on_destroy(self, widget):
        if self.style_manager and self._theme_signal_id:
            self.style_manager.disconnect(self._theme_signal_id)

    def _hex_to_rgba(self, hex_color):
        rgba = Gdk.RGBA()
        rgba.parse(hex_color)
        return rgba

    def _on_key_press(self, controller, keyval, keycode, state):
        has_ctrl = state & Gdk.ModifierType.CONTROL_MASK
        has_shift = state & Gdk.ModifierType.SHIFT_MASK

        if has_ctrl and has_shift and keyval in [Gdk.KEY_V, Gdk.KEY_v,]:
            self.paste_clipboard()
            return True
        return False

    def spawn_bash(self, tab_view):
        """
        Spawn a bash shell outside the Flatpak Sandbox

        :param tab_view: The TabView, where the terminal is spawned in
        :type tab_view: Adw.TabView
        """
        page = tab_view.add_page(self)
        page.set_title('local shell')
        self._page = page
        self._tab_view = tab_view

        self.spawn_async(
            Vte.PtyFlags.DEFAULT,
            os.environ['HOME'],
            ['/app/bin/host-spawn', 'bash'],
            None,
            GLib.SpawnFlags.DO_NOT_REAP_CHILD,
            None,
            None,
            -1,
            None,
            self.on_terminal_spawn,
            None
        )

    def spawn_sh(self, tab_view):
        """
        Spawn a shell inside the Flatpak Sandbox

        :param tab_view: The TabView, where the terminal is spawned in
        :type tab_view: Adw.TabView
        """
        page = tab_view.add_page(self)
        page.set_title('local shell')
        self._page = page
        self._tab_view = tab_view

        self.spawn_async(
            Vte.PtyFlags.DEFAULT,
            os.environ['HOME'],
            ['/bin/sh'],
            None,
            GLib.SpawnFlags.DO_NOT_REAP_CHILD,
            None,
            None,
            -1,
            None,
            self.on_terminal_spawn,
            None
        )

    def spawn_go_ssh_session(self, item, tab_view):
        """
        Spawn a SSH Session with the obelisk SSH Client.

        :param item: The connection item
        :type item: ObTreeNode
        :param tab_view: The TabView, where the terminal is spawned in
        :type tab_view: Adw.TabView
        """
        node = self.db_handler.get_item_data(item.uuid)
        #auth = self.db_handler.get_auth_data(node.auth_uuid)
        auth = self.db_handler.get_matching_auth_data(node.uuid)
        print(auth)
        page = tab_view.add_page(self)
        page.set_title(item.name)
        self._page = page
        self._tab_view = tab_view

        config = {
            "username": auth.username,
            "address": f"{node.address}:{str(node.port)}",
            "password": auth.password,
            "private_key_path": auth.priv_key_file,
            "jump_hosts": None
        }
        config_bytes = json.dumps(config).encode('utf-8')

        # Create a temporary file in the runtime dir
        runtime_dir = os.environ.get("XDG_RUNTIME_DIR", "/tmp")
        # print(runtime_dir)
        fd, temp_path = tempfile.mkstemp(dir=runtime_dir, prefix="ssh_cfg_")
        
        with os.fdopen(fd, 'w') as f:
            json.dump(config, f)

        env = GLib.get_environ()
        env.append(f"SSH_CONFIG_PATH={temp_path}")

        combined_flags = GLib.SpawnFlags.DO_NOT_REAP_CHILD 

        self.spawn_async(
            Vte.PtyFlags.DEFAULT,
            None,
            ['/app/bin/ssh-client'],
            env,
            combined_flags,
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
        print(pid)
        if error:
            print(f'error: {error.message}')
        else:
            terminal.connect('child-exited', self.on_command_exited)

    def on_command_exited(self, terminal, status):
        self._tab_view.close_page(self._page)
