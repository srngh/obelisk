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

import yml

class Session:
    def __init__(self, id: str):
        self.id = id


class ConfigLoader():
    def __init__(self, file_name: str):
        self.file_name = None
    
    def __call__(self, config_type: str):
        case config_type:
            match "obelisk":
                pass
            match "asbru-cm":
                pass
            match "royal-ts":
                pass
            match "moba-xterm":
                pass
            match "remote-desktop-manager":
                pass
    
    def load_obelisk_config(self, file_name: str):
        try:
            #opening the file
            # with open(file_name) as file:
            #   parse_obelisk_config(file)
            pass
        except:
            pass
            ##
        pass
    
    def parse_obelisk_config(self, config):
        # yaml syntax
        pass


