# settings.py
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

from gi.repository import Gio, GLib

class Settings:
    """Class to easy edit settings and adding and removing servers"""

    def __init__(self):
        self.gsettings = Gio.Settings.new("io.github.WojtekWidomski.comparator")

    def get_servers(self):
        return self.gsettings.get_value("servers")

    def add_server(self, name, address):
        servers = list(self.get_servers())
        servers.append((name, address))
        self.gsettings.set_value("servers", GLib.Variant("a(ss)", servers))

    def remove_server(self, number):
        servers = list(self.get_servers())
        servers.pop(number)
        self.gsettings.set_value("servers", GLib.Variant("a(ss)", servers))

    def edit_server(self, number, name, address):
        servers = list(self.get_servers())
        servers[number] = (name, address)
        self.gsettings.set_value("servers", GLib.Variant("a(ss)", servers))

    def move_server(self, old_position, new_position):
        servers = list(self.get_servers())
        moved = servers.pop(old_position)
        servers.insert(new_position - 1, moved)
        self.gsettings.set_value("servers", GLib.Variant("a(ss)", servers))

    def load(self, key):
        """Load other settings"""
        return self.gsettings.get_value(key)

    def save_bool(self, key, value):
        """Save other settings (only bool)"""
        self.gsettings.set_boolean(key, value)
