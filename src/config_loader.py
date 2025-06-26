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

class ConfigLoader():
    def __init__(self, file_name: str, description: str):
        self.file_name = file_name
        self.description = description
    
    def set_uri(self, uri: str):
        self.uri = uri

    def set_port(sef, port: str):
        self.port = port
    
    def set_name(self, name: str):
        self.name = name
    
    def set_parent(self, parent)
