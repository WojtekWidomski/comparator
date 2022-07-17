from mcstatus import JavaServer
from socket import timeout, gaierror

def server_status(address: str):
    try:
        server = JavaServer.lookup(address)
        server_status = server.status()

        description = server_status.description
        version = server_status.version.name

        # Icon
        if server_status.favicon != '' and server_status.favicon:
            icon_b64 = (server_status.favicon.split(",")[1]).replace("\n", "")
        else:
            icon_b64 = None

        # Players (using status)
        players_status = []
        try:
            for player in server_status.players.sample:
                players_status.append(player.name)
        except TypeError:
            players_status = None

        players_count = server_status.players.online
        players_max = server_status.players.max
        
        status = {
            "description": description,
            "port": server.address.port,
            "version": version,
            "icon_b64": icon_b64,
            "players_status": players_status,
            "players_count": players_count,
            "players_max": players_max
        }

        return status

    except (timeout, gaierror, OSError, ValueError):
        return None

def query_players(address: str):
    server = JavaServer.lookup(address)
    players_query = []
    try:
        query = server.query()
        players_query = query.players.names
    except (timeout, OSError):
        players_query = None
    return players_query