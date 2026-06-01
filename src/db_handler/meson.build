# Copyright (C) 2026 simhof
#
# SPDX-License-Identifier: GPL-3.0-or-later

pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
connection_types_dir = join_paths(pkgdatadir, 'obelisk/db_handler')

subdir('migrations')

sources = [
  '__init__.py',
  'generic_node.py',
  'generic_auth.py',
  'obelisk_db_handler.py',
]

install_data(sources, install_dir: connection_types_dir)