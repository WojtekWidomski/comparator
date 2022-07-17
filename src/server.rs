use base64;
use gtk::gdk_pixbuf;
use gtk::gdk_pixbuf::prelude::*;
use pyo3::prelude::*;

pub struct ServerStatus {
    address: String,
    port: u32,
    description: String,
    icon: Option<gdk_pixbuf::Pixbuf>,
    players_count: u32,
    players_max: u32,
    version: String,
}

pub struct ServerPlayersList {
    players: Vec<String>,
    information: Option<String>,
}

enum DownloadState<T> {
    Unset,
    NotAvailable,
    Data(T),
}

pub struct Server {
    address: String,
    last_status: Option<ServerStatus>,
    last_players_status: DownloadState<Vec<String>>,
}

impl Server {
    pub fn new(address: String) -> Server {
        Server {
            address,
            last_status: None,
            last_players_status: DownloadState::Unset,
        }
    }

    pub fn load_status_thread(&self) {}

    pub fn load_status(&mut self) -> Result<ServerStatus, ()> {
        Python::with_gil(|py| {
            // Import api python module
            let api = PyModule::import(py, "api").expect("`api` Python module importing error.");

            // Download status
            // `server_status` python function returns dict or None.
            let status_downloaded: &PyAny = api
                .getattr("server_status")
                .unwrap()
                .call1((&self.address,))
                .expect("Can't call server_status Python function");

            if !status_downloaded.is_none() {
                // Get String and int values from status python dict
                let description: String = status_downloaded
                    .get_item("description")
                    .unwrap()
                    .extract()
                    .unwrap();

                let version: String = status_downloaded
                    .get_item("version")
                    .unwrap()
                    .extract()
                    .unwrap();

                let players_count: u32 = status_downloaded
                    .get_item("players_count")
                    .unwrap()
                    .extract()
                    .unwrap();

                let players_max: u32 = status_downloaded
                    .get_item("players_max")
                    .unwrap()
                    .extract()
                    .unwrap();

                let port: u32 = status_downloaded
                    .get_item("port")
                    .unwrap()
                    .extract()
                    .unwrap();

                // Get icon base64 string and convert it to GdkPixbuf
                let icon = status_downloaded.get_item("icon_b64").unwrap();

                // Icon can be None
                let icon: Option<String> = if icon.is_none() {
                    None
                } else {
                    icon.extract().unwrap()
                };

                let icon: Option<gdk_pixbuf::Pixbuf> = match icon {
                    Some(i) => {
                        let icon_data = base64::decode(i);

                        match icon_data {
                            Ok(data) => {
                                let loader = gdk_pixbuf::PixbufLoader::with_type("png")
                                    .expect("Can not create PixbufLoader");

                                loader.set_size(64, 64);
                                let write_result = loader.write(data.as_slice());

                                let icon = match write_result {
                                    Ok(_) => {
                                        let icon_pixbuf = loader.pixbuf().unwrap();
                                        loader.close().expect("Can not close PixbufLoader");

                                        Some(icon_pixbuf)
                                    }
                                    Err(_) => None,
                                };

                                icon
                            }
                            Err(_) => None,
                        }
                    }
                    None => None,
                };

                // Get players using status protocol
                let players_status = status_downloaded.get_item("players_status").unwrap();

                if players_status.is_none() {
                    self.last_players_status = DownloadState::NotAvailable;
                } else {
                    self.last_players_status =
                        DownloadState::Data(players_status.extract().unwrap());
                }

                Ok(ServerStatus {
                    address: self.address.clone(),
                    port,
                    description,
                    icon,
                    players_count,
                    players_max,
                    version,
                })
            } else {
                Err(())
            }
        })
    }

    pub fn load_players(&self) -> ServerPlayersList {
        Python::with_gil(|py| {
            let api = PyModule::import(py, "api").expect("`api` Python module importing error.");

            let mut players: Vec<String> = vec![];
            let mut information: Option<String> = None;

            let players_query = api
                .getattr("query_players")
                .unwrap()
                .call1((&self.address,))
                .expect("Can't call query_players Python function");

            if let DownloadState::Data(players_status) = &self.last_players_status {
                if players_status.iter().any(|p| p.contains("§")) {
                    let mut information_string = String::from("");
                    for player in players_status {
                        information_string.push_str(format!("\n{}", player).as_str());
                        // TODO: Add formatting
                    }
                    information = Some(information_string[1..].to_string());
                } else {
                    information = None;
                    players = players_status.clone();
                }
            }

            if !players_query.is_none() {
                players = players_query.extract().unwrap();
            }

            ServerPlayersList {
                players, information
            }
        })
    }
}
