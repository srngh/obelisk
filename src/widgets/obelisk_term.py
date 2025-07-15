# obelisk_term.py
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


from gi.repository import Gtk, Vte, GLib, Gio
import os

class ObeliskTerm(Vte.Terminal):
    __gtype_name__ = "ObeliskTerm"

    #term = Vte.Terminal()
    #pty = Vte.Pty.new_sync(Vte.PtyFlags.DEFAULT)
    #term.set_pty(pty)


    def __init__(self, **kwargs):
        super().__init__(**kwargs)


    def spawn_bash(self):
        self.spawn_async(
            Vte.PtyFlags.DEFAULT,
            os.environ['HOME'],
            ["/app/bin/host-spawn", "bash"],
            None,
            GLib.SpawnFlags.DO_NOT_REAP_CHILD,
            None,
            None,
            -1,
            None,
            None,
            None
        )

    def spawn_sh(self):
        self.spawn_async(
            Vte.PtyFlags.DEFAULT,
            os.environ['HOME'],
            ["/bin/sh"],
            None,
            GLib.SpawnFlags.DO_NOT_REAP_CHILD,
            None,
            None,
            -1,
            None,
            None,
            None
        )

    def spawn_ssh(self, func):
        self.spawn_async(
            Vte.PtyFlags.DEFAULT,
            os.environ['HOME'],
            [func],
            None,
            GLib.SpawnFlags.DO_NOT_REAP_CHILD,
            None,
            None,
            -1,
            None,
            None,
            None
        )
