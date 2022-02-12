# server_manager.py
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

from gi.repository import Gtk, Adw, Gdk, GLib, GObject
import socket, struct, threading
from subprocess import check_output
from .server_listbox_row import ServerListboxRow
from .settings import Settings
from .server import Server

class ServerManager:
    """Class to add and remove servers from list"""

    loading_number = 0

    def __init__(self, servers_listbox, servers_localhost_listbox, lan_listbox,
                 servers_leaflet, infopage, refresh_button,
                 removed_localhost_server_function, servers_list,
                 servers_localhost_list, lan_games_label):
        self.servers_listbox = servers_listbox
        self.servers_localhost_listbox = servers_localhost_listbox
        self.lan_listbox = lan_listbox
        self.servers_leaflet = servers_leaflet
        self.infopage = infopage
        self.refresh_button = refresh_button
        self.removed_localhost_server_function = removed_localhost_server_function
        self.servers_list = servers_list
        self.servers_localhost_list = servers_localhost_list
        self.lan_games_label = lan_games_label

        self.lan_games = set()
        self.lan_games_timeouts = dict()
        self.lan_games_loading = True

        self.remove_spaces = Settings().load("remove-spaces")

    def load_localhost_servers(self):
        ports = []
        ss_output = check_output(['ss', '-lntuH']).decode().split("\n")
        for line in ss_output:
            if line != "":
                port = line.split()[4].split(":")[-1]
                if int(port) > 1024:
                    ports.append(port)
        ports = set(ports)
        servers = self.servers_localhost_list
        servers_addresses = []
        for listboxrow in servers:
            servers_addresses.append(listboxrow.address)
        for port in ports:
            if (not "localhost:"+port in servers_addresses) and (
                not (socket.gethostbyname(socket.gethostname()), port)
                                          in self.lan_games):
                server = Server("localhost:"+port)
                server.load(self.add_localhost)

    def add_localhost(self, server):
        if server.status != None:
            if len(self.servers_localhost_list) > 0:
                for listboxrow in self.servers_localhost_listbox:
                    listboxrow.name_label.set_label(_("This computer") + " (" +
                                               str(listboxrow.server.server.port) + ")")
                name = _("This computer") + " (" + str(server.server.port) + ")"
            else:
                name = _("This computer")
            row = ServerListboxRow(name, server,
                                    self.servers_leaflet,
                                    self.infopage,
                                    self.change_loading_number,
                                    False,
                                    remove_spaces=self.remove_spaces,
                                    removed_function=self.removed_localhost_server_function)
            self.servers_localhost_list.append(row)
            self.servers_localhost_listbox.insert(row, -1)
            # After removing servers, bottom margin is removed in ComparatorWindow
            self.servers_localhost_listbox.set_margin_bottom(12)
            self.servers_localhost_listbox.set_visible(True)

    def load_lan_games(self):
        # Minecraft sends multicasts, when hosting LAN world.
        # Address:224.0.2.60 Port:4445
        s = socket.socket(type=socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('', 4445))
        mreq = struct.pack("4si", socket.inet_aton("224.0.2.60"),
                           socket.INADDR_ANY)
        s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        s.settimeout(5)

        while self.lan_games_loading:
            try:
                data, address = s.recvfrom(1024)
                if not (data, address) in self.lan_games_timeouts:
                    description, port = data.decode().replace("[MOTD]", "").replace("[/AD]", "").split("[/MOTD][AD]")
                    admin, world = description.split(" - ", 1)
                    row = ServerListboxRow(world, address[0] + ":" + port,
                                              self.servers_leaflet,
                                              self.infopage,
                                              self.change_loading_number,
                                              edit=False,
                                              description=admin+"\n"+address[0])
                    GLib.idle_add(self.lan_listbox.append, row)
                    GLib.idle_add(self.lan_listbox.set_visible, True)
                    GLib.idle_add(self.lan_games_label.set_visible, True)
                    if address[0] == socket.gethostbyname(socket.gethostname()):
                        for localhostrow in self.servers_localhost_listbox:
                            if localhostrow.address == "localhost:" + port:
                                self.servers_localhost_list.remove(localhostrow)
                                self.servers_localhost_listbox.remove(localhostrow)

                else:
                    GLib.source_remove(self.lan_games_timeouts[(data, address)])
                    self.lan_games_timeouts.pop((data, address))
                self.lan_games_timeouts[(data, address)] = GLib.timeout_add(
                    5000, self.remove_lan_world, row, (data, address), port)
                self.lan_games.add((address[0], port))
            except (socket.timeout, ValueError):
                pass


    def remove_lan_world(self, row, world_data, port):
        self.lan_listbox.remove(row)
        self.lan_games.remove((world_data[1][0], port))
        self.lan_games_timeouts.pop(world_data)
        if len(self.lan_games) == 0:
            self.lan_listbox.set_visible(False)
            self.lan_games_label.set_visible(False)

    def load_servers(self):
        saved = Settings().get_servers()
        for s in saved:
            row = ServerListboxRow(s[0], s[1],
                                      self.servers_leaflet,
                                      self.infopage,
                                      self.change_loading_number,
                                      remove_spaces=self.remove_spaces)
            self.servers_list.append(row)
            self.servers_listbox.append(row)
        self.load_localhost_servers()
        lan_thread = threading.Thread(target=self.load_lan_games)
        lan_thread.start()
        return len(saved)

    def change_loading_number(self, number):
        self.loading_number += number
        if self.loading_number > 0:
            self.refresh_button.set_sensitive(False)
        else:
            self.refresh_button.set_sensitive(True)

    def refresh_all(self):
        for server in self.servers_listbox:
            server.refresh()
        for server in self.servers_localhost_listbox:
            server.refresh()
        self.load_localhost_servers()

    def add(self, name, address):
        row = ServerListboxRow(name, address,
                                  self.servers_leaflet,
                                  self.infopage,
                                  self.change_loading_number,
                                  remove_spaces=self.remove_spaces)
        self.servers_listbox.insert(row, -1)
        self.servers_list.append(row)
        Settings().add_server(name, address)

    def edit_server(self, listboxrow, name, address):
        listboxrow.set_server(name, address)
        Settings().edit_server(listboxrow.get_index(), name, address)

    def move(self, old_position, new_position):
        # Changing position in ListBox is implemented in ComparatorWindow
        Settings().move_server(old_position, new_position)

    def remove_server(self, number):
        row = self.servers_listbox.get_row_at_index(number)
        self.servers_list.remove(row)
        self.servers_listbox.remove(row)
        Settings().remove_server(number)

    def set_remove_spaces(self, remove_spaces):
        for server in self.servers_listbox:
            server.set_remove_spaces(remove_spaces)
        for server in self.servers_localhost_listbox:
            server.set_remove_spaces(remove_spaces)

    def set_edit_mode(self, edit_mode):
        for server in self.servers_listbox:
            server.set_edit_mode(edit_mode)
