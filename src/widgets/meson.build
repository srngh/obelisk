# Copyright (C) 2025 simhof
#
# SPDX-License-Identifier: GPL-3.0-or-later

pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
widgetsdir = join_paths(pkgdatadir, 'obelisk/widgets')

sources = [
  '__init__.py',
  'preferences.py',
  'sidebar_item.py',
  'obelisk_term.py',
  'theme_switcher.py',
  'interactive_shell.py',
  'shell.py',
  'obelisk_tree_widget.py',
]

install_data(sources, install_dir: widgetsdir)