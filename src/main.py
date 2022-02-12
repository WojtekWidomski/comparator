# main.py
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

import sys
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Gio, Adw

from .window import ComparatorWindow


class Application(Adw.Application):
    def __init__(self):
        super().__init__(application_id='io.github.WojtekWidomski.comparator',
                         flags=Gio.ApplicationFlags.FLAGS_NONE)

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = ComparatorWindow(application=self)
        self.create_action("about", self.show_about_dialog)
        win.present()

    def create_action(self, name, function):
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", function)
        self.add_action(action)

    def show_about_dialog(self, widget, param):
        dialog_builder = Gtk.Builder.new_from_resource('/io/github/WojtekWidomski/comparator/ui/about_dialog.ui')
        about_dialog = dialog_builder.get_object("AboutDialog")
        about_dialog.set_transient_for(self.props.active_window)
        about_dialog.present()


def main(version):
    app = Application()
    return app.run(sys.argv)
