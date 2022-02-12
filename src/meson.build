pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'comparator')


python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', join_paths(get_option('prefix'), get_option('localedir')))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'comparator.in',
  output: 'comparator',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir')
)

comparator_sources = [
  '__init__.py',
  'main.py',
  'window.py',
  'server_listbox_row.py',
  'settings.py',
  'server_manager.py',
  'infopage.py',
  'text_formatting.py',
  'server.py',
  'preferences_window.py'
]

install_data(comparator_sources, install_dir: moduledir)
