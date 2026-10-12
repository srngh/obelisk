# preferences.py
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

from gi.repository import Adw
from gi.repository import Gtk
from gi.repository import Gio


@Gtk.Template(resource_path='/io/github/srngh/obelisk/gtk/preferences.ui')
class Preferences(Adw.PreferencesDialog):
    __gtype_name__ = 'PreferencesDialog'
    general_settings_page = Gtk.Template.Child()
    ssh_settings_page = Gtk.Template.Child()
    regex_settings_page = Gtk.Template.Child()
    term_scrollback_lines = Gtk.Template.Child()
    term_font_size = Gtk.Template.Child()

    _settings = Gio.Settings(schema_id='io.github.srngh.obelisk')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


        self._settings.bind(
            "terminal-scrollback-lines",
            self.term_scrollback_lines,
            "value",
            Gio.SettingsBindFlags.DEFAULT
        )

        self._settings.bind(
            "terminal-font-size",
            self.term_font_size,
            "value",
            Gio.SettingsBindFlags.DEFAULT
        )



