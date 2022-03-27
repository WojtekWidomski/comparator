# window.py
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

from gi.repository import Gtk, Adw, GObject, GLib, Gio, Gdk
from urllib.parse import urlparse
from .settings import Settings
from .server_manager import ServerManager
from .infopage import ServerInfoPage
from .preferences_window import PreferencesWindow

@Gtk.Template(resource_path='/io/github/WojtekWidomski/comparator/ui/window.ui')
class ComparatorWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'ComparatorWindow'

    viewswitcher_top = Gtk.Template.Child()
    viewswitcher_bottom = Gtk.Template.Child()
    servers_listbox = Gtk.Template.Child()
    servers_localhost_listbox = Gtk.Template.Child()
    lan_listbox = Gtk.Template.Child()
    servers_stack = Gtk.Template.Child()

    header_bar_stack = Gtk.Template.Child()

    servers_leaflet = Gtk.Template.Child()
    infopage_clamp = Gtk.Template.Child()

    notification_revealer = Gtk.Template.Child()
    notification_label = Gtk.Template.Child()
    notification_button = Gtk.Template.Child()
    notification_close_button = Gtk.Template.Child()
    notification_button_signal_id = None
    notification_close_signal_id = None

    add_server_button = Gtk.Template.Child()
    refresh_button = Gtk.Template.Child()
    infopage_refresh_button = Gtk.Template.Child()
    infopage_menubutton = Gtk.Template.Child()

    lan_games_label = Gtk.Template.Child()
    servers_list_label = Gtk.Template.Child()

    servers_list = []
    servers_localhost_list = []

    edit_mode = False
    drag_row_before = None
    drag_row_after = None

    removing = False

    last_network_state = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.settings = Settings()
        self.settings.gsettings.bind("window-width", self, "default-width", Gio.SettingsBindFlags.DEFAULT)
        self.settings.gsettings.bind("window-height", self, "default-height", Gio.SettingsBindFlags.DEFAULT)
        self.infopage = ServerInfoPage()
        self.infopage_clamp.set_child(self.infopage)
        self.viewswitcher_top.bind_property("title-visible", self.viewswitcher_bottom,
                                              "reveal", GObject.BindingFlags.SYNC_CREATE)
        self.refresh_button.bind_property("sensitive",
                                        self.infopage_refresh_button,
                                        "sensitive", GObject.BindingFlags.SYNC_CREATE)
        self.servers_manager = ServerManager(self.servers_listbox,
                                            self.servers_localhost_listbox,
                                            self.lan_listbox,
                                            self.servers_leaflet,
                                            self.infopage,
                                            self.refresh_button,
                                            self.localhost_server_removed,
                                            self.servers_list,
                                            self.servers_localhost_list,
                                            self.lan_games_label,
                                            self.list_changed)
        loaded_servers_count = self.servers_manager.load_servers()
        if loaded_servers_count == 0:
            self.servers_stack.set_visible_child_name("empty")
            self.servers_list_set_visible(False)

        style_manager = Adw.StyleManager.get_default()
        dark_mode = self.settings.load("dark-mode")
        if dark_mode:
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)
        else:
            style_manager.set_color_scheme(Adw.ColorScheme.PREFER_LIGHT)

        self.create_action("edit_list", self.edit_list)
        self.create_action("edit_server", self.edit_clicked)
        self.create_action("edit", self.edit)
        self.create_action("add_server", self.add_clicked)
        self.create_action("remove_server", self.remove_clicked)
        self.create_action("settings", self.settings_clicked)
        self.create_action("refresh", self.refresh)

        network_monitor = Gio.NetworkMonitor.get_default()
        network_monitor.connect("network-changed", self.network_changed)

    def network_changed(self, monitor, available):
        if available != self.last_network_state:
            if available:
                self.servers_stack.set_visible_child_name("servers")
                self.add_server_button.set_visible(True)
                self.refresh_button.set_visible(True)
                self.lookup_action("edit_list").set_enabled(True)
                self.servers_manager.refresh_all()
            else:
                self.servers_stack.set_visible_child_name("no_network")
                self.add_server_button.set_visible(False)
                self.refresh_button.set_visible(False)
                self.lookup_action("edit_list").set_enabled(False)
                if self.servers_leaflet.get_visible_child_name() == "server_info":
                    self.back_clicked(None)
                if self.edit_mode:
                    self.exit_edit_mode(None)
            self.last_network_state = available

    def create_action(self, name, function):
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", function)
        self.add_action(action)

    def edit(self, action, parameter):
        if self.servers_leaflet.get_visible_child_name() == "server_info":
            self.edit_clicked(None, None)
        else:
            if self.edit_mode:
                self.exit_edit_mode(None)
            else:
                self.edit_list(None, None)

    def add_clicked(self, action, parameter):
        self.show_dialog(self.add_server)

    def edit_clicked(self, action, parameter):
        self.show_dialog(self.save_edit, _("Save"), _("Edit server"),
                          self.clicked_server.name_label.get_label(),
                          self.clicked_server.address)

    def show_dialog(self, function, button_label=_("Add"), title=_("Add server"),
                     name="", address=""):
        dialog_builder = Gtk.Builder.new_from_resource(
            "/io/github/WojtekWidomski/comparator/ui/add_server_dialog.ui")
        dialog = dialog_builder.get_object("AddServerDialog")
        dialog.set_title(title)
        name_entry = dialog_builder.get_object("name_entry")
        address_entry = dialog_builder.get_object("address_entry")
        error_revealer = dialog_builder.get_object("error_revealer")
        name_entry.set_text(name)
        address_entry.set_text(address)
        cancel_button = dialog_builder.get_object("cancel_button")
        add_button = dialog_builder.get_object("add_button")
        add_button.set_label(button_label)
        cancel_button.connect("clicked", self.close_add_server_dialog, dialog)
        add_button.connect("clicked", function, dialog,
                               name_entry, address_entry)
        add_button.set_sensitive(False)
        self.correct_data = False
        name_entry.connect("activate", self.focus_address_entry, address_entry)
        address_entry.connect("activate", function, dialog, name_entry,
                           address_entry)
        name_entry.connect("changed", self.dialog_text_changed,
                           address_entry, add_button, error_revealer)
        address_entry.connect("changed", self.dialog_text_changed,
                           name_entry, add_button, error_revealer)
        dialog.set_transient_for(self)
        dialog.present()
        self.dialog_text_changed(address_entry, name_entry, add_button, error_revealer)

    def dialog_text_changed(self, entry1, entry2, button, error_revealer):
        if entry1.get_name() == "address_entry":
            try:
                if urlparse("//" + entry1.get_text()).hostname != None or entry1.get_text() == "":
                    self.address_invalid = False
                else:
                    self.address_invalid = True
            except ValueError:
                self.address_invalid = True
            # Display or hide error
            if self.address_invalid:
                error_revealer.set_reveal_child(True)
            else:
                error_revealer.set_reveal_child(False)

        if entry1.get_text() != "" and entry2.get_text() != "" and not self.address_invalid:
            self.correct_data = True
            button.set_sensitive(True)
        else:
            self.correct_data = False
            button.set_sensitive(False)

    def focus_address_entry(self, entry, address_entry):
        address_entry.grab_focus()

    def close_add_server_dialog(self, button, dialog):
        dialog.destroy()

    def add_server(self, button, dialog, name_entry, address_entry):
        if self.correct_data:
            name = name_entry.get_text()
            address = address_entry.get_text()
            self.servers_manager.add(name, address)
            dialog.destroy()
            self.servers_list_set_visible(True)
            self.servers_stack.set_visible_child_name("servers")

    def save_edit(self, button, dialog, name_entry, address_entry):
        if self.correct_data:
            name = name_entry.get_text()
            address = address_entry.get_text()
            self.servers_manager.edit_server(self.clicked_server, name, address)
            dialog.destroy()

    @Gtk.Template.Callback()
    def back_clicked(self, button):
        self.servers_leaflet.set_visible_child_name("servers_list")
        self.clicked_server.infopage_displaying = False
        self.width_changed(None, None)

    @Gtk.Template.Callback()
    def window_closed(self, win):
        self.servers_manager.lan_games_loading = False
        if self.removing:
            self.servers_manager.remove_server(self.removed_server.get_index())

    @Gtk.Template.Callback()
    def server_clicked(self, listbox, listboxrow):
        if not self.edit_mode:
            self.clicked_server = listboxrow
            listboxrow.infopage_displaying = True
            listboxrow.clicked()
            if listboxrow.edit:
                self.infopage_menubutton.set_visible(True)
            else:
                self.infopage_menubutton.set_visible(False)

    def remove_clicked(self, action, parameter):
        if self.removing:
            self.close_notification(None, self.remove_server)

        self.removed_server = self.clicked_server

        name = self.removed_server.name_label.get_label()
        self.show_notification(_("{} removed").format(name), self.undo_remove,
                                 button_text=_("Undo"),
                                 timeout_function=self.remove_server)

        self.removing = True
        self.removed_server.set_visible(False)

        self.servers_leaflet.set_visible_child_name("servers_list")

        if len(self.servers_list) == 1:
            self.servers_list_set_visible(False)
            self.list_changed()

    def show_notification(self, text, clicked_function, button_text="",
                            time=5, timeout_function=None):
        """Show in app notification with text and button with button_text and
        call clicked_function, when button clicked. When clicked_function is
        None button is hidden."""
        self.notification_label.set_label(text)

        if clicked_function != None:
            self.notification_button.set_label(button_text)
            if self.notification_button_signal_id != None:
                self.notification_button.disconnect(
                    self.notification_button_signal_id)
            self.notification_button_signal_id = (
                self.notification_button.connect("clicked", clicked_function))
            self.notification_button.set_visible(True)
        else:
            self.notification_button.set_visible(False)

        if self.notification_close_signal_id != None:
            self.notification_close_button.disconnect(
                self.notification_close_signal_id)
        self.notification_close_signal_id = self.notification_close_button.connect(
            "clicked", self.close_notification, timeout_function)

        self.notification_revealer.set_reveal_child(True)

        self.notification_timeout = GLib.timeout_add(time*1000,
                         self.close_notification, None, timeout_function)

    def remove_server(self):
        self.servers_manager.remove_server(self.removed_server.get_index())
        self.removing = False

    def undo_remove(self, button):
        GLib.source_remove(self.notification_timeout)
        self.removed_server.set_visible(True)
        self.notification_revealer.set_reveal_child(False)
        self.removing = False
        self.servers_list_set_visible(True)
        self.servers_stack.set_visible_child_name("servers")

    def close_notification(self, button, function):
        GLib.source_remove(self.notification_timeout)
        self.notification_revealer.set_reveal_child(False)
        if function != None:
            function()

    def refresh(self, action, parameter):
        if self.servers_leaflet.get_visible_child_name() == "server_info":
            self.refresh_server(None)
        else:
            self.refresh_all(None)

    @Gtk.Template.Callback()
    def refresh_all(self, button):
        self.servers_manager.refresh_all()

    @Gtk.Template.Callback()
    def refresh_server(self, button):
        self.clicked_server.refresh()

    def localhost_server_removed(self, row):
        self.servers_localhost_list.remove(row)
        list_elements = self.servers_localhost_list
        self.list_changed()
        if len(list_elements) == 1:
            self.servers_localhost_listbox.get_row_at_index(0).name_label.set_label(_("This computer"))
        elif len(list_elements) == 0:
            self.servers_localhost_listbox.set_visible(False)
            self.servers_localhost_listbox.set_margin_bottom(0)

    def edit_list(self, action, parameter):
        self.edit_mode = True
        self.header_bar_stack.set_visible_child_name("edit_headerbar")
        self.droptarget = Gtk.DropTarget.new(GObject.TYPE_STRING,
                                        Gdk.DragAction.MOVE)
        self.servers_listbox.add_controller(self.droptarget)
        self.servers_manager.set_edit_mode(True)
        self.droptarget.connect("drop", self.drag_drop)
        self.droptarget.connect("motion", self.drag_motion)
        self.droptarget.connect("leave", self.drag_leave)

    @Gtk.Template.Callback()
    def exit_edit_mode(self, button):
        self.edit_mode = False
        self.header_bar_stack.set_visible_child_name("main_headerbar")
        self.servers_listbox.remove_controller(self.droptarget)
        self.servers_manager.set_edit_mode(False)

    def list_changed(self):
        if (len(self.servers_list) == 0 or (self.removing and len(self.servers_list) == 1)) and len(self.servers_localhost_list) == 0:
            self.servers_list_set_visible(False)
            if len(self.servers_manager.lan_games) == 0:
                self.servers_stack.set_visible_child_name("empty")
            else:
                self.servers_stack.set_visible_child_name("servers")
        else:
            self.servers_list_set_visible(True)
            self.servers_stack.set_visible_child_name("servers")

    def servers_list_set_visible(self, visible):
        self.servers_list_label.set_visible(visible)
        if len(self.servers_list) != 0 and visible and not (self.removing and len(self.servers_list) == 1):
            self.servers_listbox.set_visible(True)
            self.servers_localhost_listbox.set_margin_bottom(12)
        else:
            self.servers_listbox.set_visible(False)
            self.servers_localhost_listbox.set_margin_bottom(0)
        if visible:
            self.lan_games_label.set_margin_top(18)
        else:
            self.lan_games_label.set_margin_top(0)

    def drag_drop(self, target, data, x, y):
        moved = self.servers_listbox.get_row_at_index(int(data))

        self.disable_drag_highlight()

        if moved != self.drag_row_after:
            self.servers_list.remove(moved)
            self.servers_listbox.remove(moved)
            if self.drag_row_after:
                self.servers_list.append(moved)
                self.servers_listbox.insert(moved,
                                    self.drag_row_after.get_index())
                self.servers_manager.move(int(data),
                                     self.drag_row_after.get_index())
            elif self.drag_row_before:
                self.servers_list.append(moved)
                self.servers_listbox.insert(moved,
                                    self.drag_row_before.get_index()+1)
                self.servers_manager.move(int(data),
                                     self.drag_row_before.get_index()+1)
        return True


    def drag_motion(self, target, x, y):
        row = self.servers_listbox.get_row_at_y(y)

        self.disable_drag_highlight()

        if row:
            row_alloc = row.get_allocation()

            if y > row_alloc.y + row_alloc.height / 2:
                self.drag_row_before = row
                self.drag_row_after = self.servers_listbox.get_row_at_index(
                    row.get_index()+1)
            else:
                self.drag_row_before = self.servers_listbox.get_row_at_index(
                    row.get_index()-1)
                self.drag_row_after = row

        if not self.drag_row_before:
            self.drag_row_after.add_css_class(
                "drag-first")
        elif not self.drag_row_after:
            self.drag_row_before.add_css_class(
                "drag-last")
        else:
            self.drag_row_before.add_css_class(
                "drag-previous")
            self.drag_row_after.add_css_class(
                "drag-next")

        return Gdk.DragAction.MOVE

    def drag_leave(self, target):
        self.disable_drag_highlight()

    def disable_drag_highlight(self):
        if self.drag_row_before:
            self.drag_row_before.remove_css_class(
                "drag-previous")
            self.drag_row_before.remove_css_class(
                "drag-last")
        if self.drag_row_after:
            self.drag_row_after.remove_css_class(
                "drag-next")
            self.drag_row_after.remove_css_class(
                "drag-first")

    def settings_clicked(self, action, parameter):
        preferences_window = PreferencesWindow(self.settings, self.servers_manager)
        preferences_window.present()
        preferences_window.set_transient_for(self)

    @Gtk.Template.Callback()
    def width_changed(self, widget, param):

        width = self.get_default_size().width
        for row in self.servers_listbox:
            row.size_changed(width)

        for row in self.servers_localhost_listbox:
            row.size_changed(width)

        for row in self.lan_listbox:
            row.size_changed(width)
