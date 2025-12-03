# obelisk_config.py
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

from gi.repository import GObject, Gio, Gdk

from config_file_handlers.config_file_handler import ConfigFileHandlerFactory

class ObConfig(GObject.Object, Gio.ListModel):
    __gtype_name__ = "ObConfig"
    "This class holds the configuration of a loaded config file."

    '''
    __gsignals__ = {
        "changed": (GObject.SignalFlags.RUN_FIRST, None, ()) <<<<---- what it do?
        "": asdf
    }
    '''
    def __init__(self, filename=None, **kwargs):
        super().__init__(**kwargs)
        self.autosave = False
        self.filename = filename
        self.config_type = 'obelisk'



