# server.py
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

from mcstatus import MinecraftServer
from socket import timeout, gaierror
import threading
import base64
from gi.repository import GdkPixbuf, GLib
from .text_formatting import Formatting

class Server:
    """
    This class allows downloading server information without blocking GUI.
    In most methods, as argument, function to call, when data is downloaded
    should be passed. It will be called with downloaded data as argument."""

    icon_pixbuf = None
    information = None
    players = []

    def __init__(self, address):
        self.address = address

    def _load_status(self, function):
        try:
            self.server = MinecraftServer.lookup(self.address)
            self.status = self.server.status()
            if self.status.favicon != '' and self.status.favicon != None:
                icon_base64 = ((self.status.favicon).split(",")[1]).replace('\n','')
                icon_data = base64.b64decode(icon_base64, validate=True)
                loader = GdkPixbuf.PixbufLoader.new_with_type("png")
                loader.set_size(64, 64)
                loader.write(icon_data)
                self.icon_pixbuf = loader.get_pixbuf()
                loader.close()
        except (timeout, gaierror, OSError, ValueError):
            self.status = None

        if function != None:
            GLib.idle_add(function, self)

        if self.status != None:
            self._load_players()

    def _load_players(self):
        players_status = []
        players_query = []

        # Try using status
        try:
            for player in self.status.players.sample:
                players_status.append(player.name)
        except TypeError:
            players_status = None

        if players_status != None:
            if "§" in players_status[0]:
                self.information = ""
                for player in players_status:
                    self.information += "\n" + Formatting().auto(player,
                                                            wrap=False)
                # [1:] removes newline at begining
                self.information = self.information[1:]
            else:
                self.players = players_status

        # Try using query
        try:
            query = self.server.query()
            players_query = query.players.names
        except (timeout, OSError):
            players_query = None

        if players_query != None:
            self.players = players_query



    def load(self, function=None):
        thread = threading.Thread(target=self._load_status, args=[function])
        thread.start()
