pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir)


python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').path())
conf.set_quoted('VERSION', meson.project_version())
conf.set_quoted('GETTEXT_PACKAGE', 'comparator')
conf.set_quoted('LOCALEDIR', join_paths(get_option('prefix'), get_option('localedir')))
conf.set_quoted('PKGDATADIR', pkgdatadir)

configure_file(
  input: 'config.rs.in',
  output: 'config.rs',
  configuration: conf
)

# Copy the config.rs output to the source directory.
run_command(
  'cp',
  join_paths(meson.project_build_root(), 'src', 'config.rs'),
  join_paths(meson.project_source_root(), 'src', 'config.rs'),
  check: true
)

rust_sources = files(
  'application.rs',
  'config.rs',
  'main.rs',
  'window.rs',
)

sources = [cargo_sources, rust_sources]

cargo_script = find_program(join_paths(meson.project_source_root(), 'build-aux/cargo.sh'))
cargo_release = custom_target(
  'cargo-build',
  build_by_default: true,
  input: sources,
  output: meson.project_name(),
  console: true,
  install: true,
  install_dir: get_option('bindir'),
  command: [
    cargo_script,
    meson.project_build_root(),
    meson.project_source_root(),
    '@OUTPUT@',
    get_option('buildtype'),
    meson.project_name(),
  ]
)

# comparator_sources = [
#   '__init__.py',
#   'main.py',
#   'window.py',
#   'server_listbox_row.py',
#   'settings.py',
#   'server_manager.py',
#   'infopage.py',
#   'text_formatting.py',
#   'server.py',
#   'preferences_window.py'
# ]

# install_data(comparator_sources, install_dir: moduledir)
