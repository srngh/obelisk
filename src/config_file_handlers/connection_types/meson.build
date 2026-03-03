# Copyright (C) 2025 simhof
#
# SPDX-License-Identifier: GPL-3.0-or-later

pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
connection_types_dir = join_paths(pkgdatadir, 'obelisk/config_file_handlers/connection_types')

sources = [
  '__init__.py',
  'item.py',
  'folder.py',
]

install_data(sources, install_dir: connection_types_dir)