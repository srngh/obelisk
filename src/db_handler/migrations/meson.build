# Copyright (C) 2026 simhof
#
# SPDX-License-Identifier: GPL-3.0-or-later

pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
migrations_dir = join_paths(pkgdatadir, 'obelisk/db_handler/migrations')

sources = [
  '0001_add_col_is_jumhost_to_connections.sql',
  '0002_add_col_use_jumphost_to_connections.sql',
  '0003_add_col_pref_method_to_authentication.sql',
  '0004_add_col_ignore_host_key_to_authentication.sql',
  '0005_rename_col_key_file.sql',
  '0006_add_col_us_parent_jumphost_to_connections.sql',
  '0007_rename_use_jumohost_to_jumhost_uuid.sql',
]

install_data(sources, install_dir: migrations_dir)