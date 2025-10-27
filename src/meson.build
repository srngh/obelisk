pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / 'obelisk'
gnome = import('gnome')

blueprints = custom_target('blueprints',
  input: files(
    'window.blp',
    'gtk/help-overlay.blp',
    'gtk/preferences.blp',
    'gtk/theme_switcher.blp',
  ),
  output: '.',
  command: [find_program('blueprint-compiler'), 'batch-compile', '@OUTPUT@', '@CURRENT_SOURCE_DIR@', '@INPUT@'],
)

gnome.compile_resources('obelisk',
  'obelisk.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
  dependencies: blueprints,
)

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').full_path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', get_option('prefix') / get_option('localedir'))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'obelisk.in',
  output: 'obelisk',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'r-xr-xr-x'
)

subdir('widgets')
subdir('config_loaders')

obelisk_sources = [
  '__init__.py',
  'main.py',
  'window.py',
  'config.yaml',
  'obelisk_list_view.py',
]

install_data(obelisk_sources, install_dir: moduledir)
