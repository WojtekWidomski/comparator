# infopage.py
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

from gi.repository import Gtk, Adw, GdkPixbuf, GObject, GLib
from .text_formatting import Formatting

@Gtk.Template(resource_path="/io/github/WojtekWidomski/comparator/ui/server_info_page.ui")
class ServerInfoPage(Gtk.Stack):
    __gtype_name__ = 'ServerInfoPage'

    name_label = Gtk.Template.Child()
    description_label = Gtk.Template.Child()
    players_number = Gtk.Template.Child() #GtkLabel, "online/max players"
    levelbar = Gtk.Template.Child()
    icon = Gtk.Template.Child()
    additional_info_box = Gtk.Template.Child()
    additional_info = Gtk.Template.Child()
    listbox = Gtk.Template.Child()
    players_list_stack = Gtk.Template.Child()
    players_list_stack2 = Gtk.Template.Child()
    address = Gtk.Template.Child()
    port = Gtk.Template.Child()
    version = Gtk.Template.Child()

    players_error_title = Gtk.Template.Child()
    players_error_icon = Gtk.Template.Child()
    players_error_description = Gtk.Template.Child()

    error_status_page = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.players_list_stack.bind_property("visible-child-name",
                                              self.players_list_stack2,
                                              "visible-child-name",
                                              GObject.BindingFlags.SYNC_CREATE)

    def set_players_number(self, players):
        """players is tuple (online, max)"""
        self.players_number.set_label(str(players[0]) + "/" + str(players[1])
        # online/max players
                                    + " " + _("players"))
        self.levelbar.set_value(players[0]/players[1])

    def players_list_remove_all(self):
        players_to_delete = []
        for row in self.listbox:
            players_to_delete.append(row)
        for row in players_to_delete:
            row.get_parent().remove(row)

    def set_information(self, name, server, description):
        self.players_list_remove_all()

        # Description and name
        self.name_markup = name
        if description == "":
            self.description_markup = Formatting().auto(
                server.status.description)
        else:
            self.description_markup = Formatting().auto(description)

        if "§" in self.description_markup or "§" in self.name_markup:
            GLib.timeout_add(20, self.update_obfuscated_text)
        else:
            self.description_label.set_markup(self.description_markup)
            self.name_label.set_markup(self.name_markup)

        # Icon
        if server.icon_pixbuf != None:
            self.icon.set_from_pixbuf(server.icon_pixbuf.scale_simple(
                64, 64, GdkPixbuf.InterpType.BILINEAR))
        else:
            self.icon.set_from_icon_name("server-default")

        # Address, port and version
        self.address.set_text(_("Address") + ": " + server.address)
        self.port.set_text(_("Port") + ": " + str(server.server.port))
        self.version.set_markup(_("Version") + ": " + Formatting().auto(
            server.status.version.name, False))

        # Players
        self.set_players_number((server.status.players.online,
                                 server.status.players.max))

        # Adding players to players list
        if server.players != []:
            self.players_list_stack.set_visible_child_name("players")
            for player in server.players:
                row = Gtk.ListBoxRow()
                label=Gtk.Label(label=player)
                label.set_halign(Gtk.Align.START)
                row.set_child(label)
                self.listbox.insert(row, -1)
        else:
            self.players_list_stack.set_visible_child_name("error")
            if server.status.players.online == 0:
                self.players_error_title.set_label(_("No players"))
                self.players_error_description.set_label(
                    _("No one is playing on this server now."))
                self.players_error_icon.set_from_icon_name(
                    "system-users-symbolic")
            else:
                self.players_error_title.set_label(
                    _("Can not get players list"))
                self.players_error_description.set_label(
                    _("Players displaying is disabled on server."))
                self.players_error_icon.set_from_icon_name(
                    "dialog-warning-symbolic")

        # Additional information if available
        if server.information != None:
            self.additional_info.set_markup(server.information)
            self.additional_info_box.set_visible(True)
        else:
            self.additional_info_box.set_visible(False)


    def update_obfuscated_text(self):
        self.name_label.set_markup(
            Formatting().obfuscated_text(self.name_markup))
        self.description_label.set_markup(
            Formatting().obfuscated_text(self.description_markup))
        return True
