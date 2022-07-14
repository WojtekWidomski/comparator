// application.rs
//
// Copyright 2022 Wojtek Widomski
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.

use glib::clone;
use gtk::prelude::*;
use gtk::subclass::prelude::*;
use gtk::{gio, glib};
use adw::subclass::prelude::*;

use crate::config::VERSION;
use crate::ComparatorWindow;

mod imp {
    use super::*;

    #[derive(Debug, Default)]
    pub struct ComparatorApplication {}

    #[glib::object_subclass]
    impl ObjectSubclass for ComparatorApplication {
        const NAME: &'static str = "ComparatorApplication";
        type Type = super::ComparatorApplication;
        type ParentType = adw::Application;
    }

    impl ObjectImpl for ComparatorApplication {
        fn constructed(&self, obj: &Self::Type) {
            self.parent_constructed(obj);

            // obj.setup_gactions();
            // obj.set_accels_for_action("app.quit", &["<primary>q"]);
        }
    }

    impl ApplicationImpl for ComparatorApplication {
        // We connect to the activate callback to create a window when the application
        // has been launched. Additionally, this callback notifies us when the user
        // tries to launch a "second instance" of the application. When they try
        // to do that, we'll just present any existing window.
        fn activate(&self, application: &Self::Type) {
            // Get the current window or create one if necessary
            let window = if let Some(window) = application.active_window() {
                window
            } else {
                let window = ComparatorWindow::new(application);
                window.upcast()
            };

            // Ask the window manager/compositor to present the window
            window.present();
        }
    }

    impl GtkApplicationImpl for ComparatorApplication {}
    impl AdwApplicationImpl for ComparatorApplication {}
}

glib::wrapper! {
    pub struct ComparatorApplication(ObjectSubclass<imp::ComparatorApplication>)
        @extends gio::Application, gtk::Application, adw::Application,
        @implements gio::ActionGroup, gio::ActionMap;
}

impl ComparatorApplication {
    pub fn new(application_id: &str, flags: &gio::ApplicationFlags) -> Self {
        glib::Object::new(&[("application-id", &application_id), ("flags", flags)])
            .expect("Failed to create ComparatorApplication")
    }

    // fn setup_gactions(&self) {
    //     let quit_action = gio::SimpleAction::new("quit", None);
    //     quit_action.connect_activate(clone!(@weak self as app => move |_, _| {
    //         app.quit();
    //     }));
    //     self.add_action(&quit_action);

    //     let about_action = gio::SimpleAction::new("about", None);
    //     about_action.connect_activate(clone!(@weak self as app => move |_, _| {
    //         app.show_about();
    //     }));
    //     self.add_action(&about_action);
    // }
}
