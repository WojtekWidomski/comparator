// window.rs
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

use gtk::prelude::*;
use gtk::subclass::prelude::*;
use gtk::{gio, glib, CompositeTemplate};
use adw::prelude::*;
use adw::subclass::prelude::*;
use adw;

mod imp {
    use super::*;

    #[derive(Debug, Default, CompositeTemplate)]
    #[template(resource = "/io/github/WojtekWidomski/comparator/ui/window.ui")]
    pub struct ComparatorWindow {
        // Template widgets
    }

    #[glib::object_subclass]
    impl ObjectSubclass for ComparatorWindow {
        const NAME: &'static str = "ComparatorWindow";
        type Type = super::ComparatorWindow;
        type ParentType = adw::ApplicationWindow;

        fn class_init(klass: &mut Self::Class) {
            Self::bind_template(klass);
        }

        fn instance_init(obj: &glib::subclass::InitializingObject<Self>) {
            obj.init_template();
        }
    }

    impl ObjectImpl for ComparatorWindow {}
    impl WidgetImpl for ComparatorWindow {}
    impl WindowImpl for ComparatorWindow {}
    impl ApplicationWindowImpl for ComparatorWindow {}
    impl AdwApplicationWindowImpl for ComparatorWindow {}
}

glib::wrapper! {
    pub struct ComparatorWindow(ObjectSubclass<imp::ComparatorWindow>)
        @extends gtk::Widget, gtk::Window, gtk::ApplicationWindow, adw::ApplicationWindow,
        @implements gio::ActionGroup, gio::ActionMap;
}

impl ComparatorWindow {
    pub fn new<P: glib::IsA<adw::Application>>(application: &P) -> Self {
        glib::Object::new(&[("application", application)])
            .expect("Failed to create ComparatorWindow")
    }
}
