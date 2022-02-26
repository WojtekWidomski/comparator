# server_listbox_row.py
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

from gi.repository import Gtk, Adw, GdkPixbuf, GLib, Gio, Gdk, GObject
from .server import Server
from .text_formatting import Formatting

@Gtk.Template(resource_path='/io/github/WojtekWidomski/comparator/ui/server_listbox_row.ui')
class ServerListboxRow(Gtk.ListBoxRow):
    __gtype_name__ = 'ServerListboxRow'


    #GtkLabel
    name_label = Gtk.Template.Child()
    description_label = Gtk.Template.Child()
    players_number = Gtk.Template.Child()
    players_number_small = Gtk.Template.Child()

    #GtkStack
    icon_stack = Gtk.Template.Child()

    #GtkRevealer
    icon_revealer = Gtk.Template.Child()
    players_number_revealer = Gtk.Template.Child()
    players_number_small_revealer = Gtk.Template.Child()

    #GtkImage
    icon = Gtk.Template.Child()

    box = Gtk.Template.Child()

    infopage_displaying = False
    obfuscated_text = False
    obfuscated_timeout = None


    # server_address is string or Server
    def __init__(self, name, server_address, leaflet, infopage,
                 change_loading_number, edit=True, dragicon=False,
                 remove_spaces=True, description="", removed_function=None, **kwargs):
        super().__init__(**kwargs)

        gdk_display = Gdk.Display.get_default()
        css_provider = Gtk.CssProvider()
        css_provider.load_from_resource(
            "/io/github/WojtekWidomski/comparator/ui/server_listbox_row.css")
        Gtk.StyleContext.add_provider_for_display(gdk_display, css_provider,
                                     Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self.icon_revealer.bind_property("reveal-child",
                                          self.players_number_revealer,
                                          "reveal-child",
                                          GObject.BindingFlags.SYNC_CREATE)

        if not dragicon:
            self.change_loading_number = change_loading_number

            self.edit = edit

            self.remove_spaces = remove_spaces

            self.description = description

            self.leaflet = leaflet
            self.infopage = infopage

            self.removed_function = removed_function

            self.set_server(name, server_address)


    def set_server(self, name, server_address):
        if type(server_address) == str:
            self.server = Server(server_address)
            self.address = server_address
        elif type(server_address) == Server:
            self.server = server_address
            self.address = server_address.address
        self.description_label.set_label(_("Connecting...") + "\n")
        self.refresh()
        self.name_markup = Formatting().auto(name, wrap=False)
        self.name_label.set_markup(self.name_markup)

    def set_data(self, server):
        status = server.status
        self.loading_data = False
        self.change_loading_number(-1)
        if status != None:
            if self.infopage_displaying:
                self.infopage.set_visible_child_name("information")
                self.infopage.set_information(self.name_markup,
                                                        self.server,
                                                        self.description)
            if self.description == "":
                self.description_unformatted = status.description
            else:
                self.description_unformatted = self.description
            self.format_description()

            if self.server.icon_pixbuf != None:
                self.icon.set_from_pixbuf(self.server.icon_pixbuf.scale_simple(
                    48, 48, GdkPixbuf.InterpType.BILINEAR))

            self.players = (status.players.online, status.players.max)
            self.players_number.set_text(str(status.players.online)
                                         + " " + _("players"))
            self.players_number_small.set_text(str(status.players.online))
            self.players_number.set_visible(True)
            self.players_number_small_revealer.set_visible(True)
        elif self.edit:
            if self.infopage_displaying:
                self.display_error()
            if self.obfuscated_timeout != None:
                GLib.source_remove(self.obfuscated_timeout)
                self.obfuscated_timeout = None
            self.description_label.set_label(_("Can not connect to server") + "\n")
            # \n at end of the error is to keep correct height of row
            self.icon.set_from_icon_name("network-error-symbolic")
            self.players_number.set_visible(False)
            self.players_number_small_revealer.set_visible(False)
        else:
            if self.removed_function != None:
                self.removed_function(self)
            self.get_parent().remove(self)
            return

        self.icon_stack.set_visible_child_name("icon")

    def update_obfuscated_text(self):
        self.description_label.set_markup(
            Formatting().obfuscated_text(self.description_markup))
        self.name_label.set_markup(Formatting().obfuscated_text(self.name_markup))
        return True

    def format_description(self):
        self.description_markup = Formatting().auto(self.description_unformatted,
                                            remove_spaces=self.remove_spaces)
        self.enable_obfuscated()

    def enable_obfuscated(self):
        if not self.obfuscated_text:
            if "§" in self.description_markup or "§" in self.name_markup:
                self.obfuscated_timeout = GLib.timeout_add(
                                            20, self.update_obfuscated_text)
                self.obfuscated_text = True
            else:
                self.description_label.set_markup(self.description_markup)

    def set_remove_spaces(self, remove_spaces):
        self.remove_spaces = remove_spaces
        self.format_description()

    def refresh(self, display_spinner=True):
        if display_spinner:
            self.icon_stack.set_visible_child_name("spinner")
        self.loading_data = True
        self.change_loading_number(1)
        self.server.load(self.set_data)

    def clicked(self):
        if not self.loading_data:
            if self.server.status != None:
                self.infopage.set_information(self.name_markup,
                                                        self.server,
                                                        self.description)
                self.infopage.set_visible_child_name("information")
            else:
                self.display_error()
        else:
            self.infopage.set_visible_child_name("spinner")
        self.leaflet.set_visible_child_name("server_info")

    def display_error(self):
        self.infopage.players_list_remove_all()
        self.infopage.additional_info_box.set_visible(False)
        self.infopage.set_visible_child_name("error")
        self.infopage.error_status_page.set_description(_("Make sure address <b>") +
                                                   self.address +
                                                    _("</b> is correct"))

    def set_edit_mode(self, edit_mode):
        if edit_mode:
            self.dragsource = Gtk.DragSource.new()
            self.dragsource.set_actions(Gdk.DragAction.MOVE)
            self.add_controller(self.dragsource)
            self.dragsource.connect("drag-begin", self.display_dragicon)
            self.dragsource.connect("drag-end", self.drag_end)
            self.dragsource.connect("prepare", self.drag_prepare)
        else:
            self.remove_controller(self.dragsource)

    def display_dragicon(self, source, drag):
        self.add_css_class("dragicon-row")

        dragicon_listboxrow = ServerListboxRow(None, None, None, None, None,
                                               dragicon=True)
        dragicon_listboxrow.set_size_request(self.get_allocated_width(), -1)

        if self.icon.get_paintable():
            dragicon_listboxrow.icon.set_from_paintable(self.icon.get_paintable())
        dragicon_listboxrow.name_label.set_label(self.name_label.get_label())
        dragicon_listboxrow.description_label.set_markup(self.description_label.get_label())
        dragicon_listboxrow.players_number.set_label(self.players_number.get_label())

        dragicon_listbox = Gtk.ListBox()
        dragicon_listbox.add_css_class("boxed-list")
        dragicon_listbox.append(dragicon_listboxrow)

        drag.set_hotspot(self.drag_x, self.drag_y)
        dragicon = Gtk.DragIcon.get_for_drag(drag)
        dragicon.set_child(dragicon_listbox)


    def drag_prepare(self, source, x, y):
        self.drag_x = x
        self.drag_y = y
        return Gdk.ContentProvider.new_for_value(str(self.get_index()))

    def drag_end(self, source, drag, delete_data):
        self.remove_css_class("dragicon-row")

    def size_changed(self, width):
        if width < 400 and width > 50:
            self.icon_revealer.set_reveal_child(False)
            self.players_number_small_revealer.set_reveal_child(True)
            self.box.add_css_class("server-row-small")
        else:
            self.icon_revealer.set_reveal_child(True)
            self.players_number_small_revealer.set_reveal_child(False)
            self.box.remove_css_class("server-row-small")
