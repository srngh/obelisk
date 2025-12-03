# Copyright (C) 2025 simhof
#
# SPDX-License-Identifier: GPL-3.0-or-later

pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
widgetsdir = join_paths(pkgdatadir, 'obelisk/widgets')

sources = [
  '__init__.py',
  'interactive_shell.py',
  'ob_context_menu.py',
  'ob_new_item_dialog.py',
  'ob_term.py',
  'ob_tree_expander.py',
  'preferences.py',
  'shell.py',
  'theme_switcher.py',
]

install_data(sources, install_dir: widgetsdir)