# Copyright (C) 2025 simhof
#
# SPDX-License-Identifier: GPL-3.0-or-later

pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
filehandlerdir = join_paths(pkgdatadir, 'obelisk/config_file_handlers')

sources = [
  '__init__.py',
  'config_file_handler.py',
  'obelisk_file_handler.py',
  'asbru_file_handler.py',
]

install_data(sources, install_dir: filehandlerdir)