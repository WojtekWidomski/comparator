# preferences_window.py
#
# Copyright 2022 Wojtek Widomski
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from gi.repository import Gtk, Adw
from .settings import Settings

@Gtk.Template(resource_path='/io/github/WojtekWidomski/comparator/ui/preferences_window.ui')
class PreferencesWindow(Adw.PreferencesWindow):
    __gtype_name__ = "PreferencesWindow"

    remove_spaces_switch = Gtk.Template.Child()
    dark_mode_switch = Gtk.Template.Child()
    ui_preferences_group = Gtk.Template.Child()
    auto_refresh_spin_button = Gtk.Template.Child()

    def __init__(self, settings, servers_manager, **kwargs):
        super().__init__(**kwargs)

        self.settings = settings
        self.servers_manager = servers_manager

        self.remove_spaces_switch.set_state(
            self.settings.load("remove-spaces"))

        self.auto_refresh_spin_button.set_value(
            self.settings.gsettings.get_int("auto-refresh-time")
        )

        style_manager = Adw.StyleManager.get_default()
        style_manager.connect("notify::system-supports-color-schemes",
                              self.notify_system_supports_color_schemes)
        self.notify_system_supports_color_schemes(style_manager, None)

    def notify_system_supports_color_schemes(self, style_manager, supports):
        # ui_preferences_group contains only dark_mode_switch for now, so we
        # need to hide entire group
        if style_manager.get_system_supports_color_schemes():
            self.ui_preferences_group.set_visible(False)
        else:
            self.ui_preferences_group.set_visible(True)
            self.dark_mode_switch.set_state(
                self.settings.load("dark-mode"))

    @Gtk.Template.Callback()
    def switch_remove_spaces(self, switch, state):
        self.settings.save_bool("remove-spaces", state)
        self.servers_manager.set_remove_spaces(state)

    @Gtk.Template.Callback()
    def switch_dark_mode(self, switch, state):
        style_manager = Adw.StyleManager.get_default()
        if state:
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)
        else:
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)
        self.settings.save_bool("dark-mode", state)

    @Gtk.Template.Callback()
    def auto_refresh_value_changed(self, spin_button):
        time = spin_button.get_value()
        self.servers_manager.auto_refresh_time = time
        self.servers_manager.add_autorefresh_timeout()
        self.settings.gsettings.set_int("auto-refresh-time", time)
