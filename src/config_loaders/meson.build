# Copyright (C) 2025 simhof
#
# SPDX-License-Identifier: GPL-3.0-or-later

pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
loadersdir = join_paths(pkgdatadir, 'obelisk/config_loaders')

sources = [
  '__init__.py',
  'config_loader.py',
  'obelisk_loader.py',
  'asbru_loader.py',
]

install_data(sources, install_dir: loadersdir)