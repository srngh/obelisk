# obelisk_file_handler.py
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


# from pathlib import Path

import yaml
# To Do:
# Demote this to a ObeliskConfigFileHandler


class ObeliskFileHandler:
    # def __init__(self):
    # home_dir = Path.home()
    # self.filename = filename or (f"{home_dir}/.config/obelisk/obelisk_nested.yaml")

    def load_connections(self, filename):
        with open(filename) as file:
            self.connections = yaml.safe_load(file)

    def to_str(self):
        return self.connections

    def to_disk(self):
        try:
            pass

        except:
            pass

# To Do:
# write changes to file

