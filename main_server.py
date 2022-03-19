import os as _os
from http.server import BaseHTTPRequestHandler as _BaseHTTPRequestHandler
from http.server import HTTPServer as _HTTPServer
from time import sleep as _sleep
from typing import NamedTuple as _NamedTuple

from polling_thread import PollingThread as _PollingThread


class ServerAddress(_NamedTuple):
    """This is a better notation of a tuple making easier to read."""

    host: str = "localhost"
    port: int = 9000


class IncidentsRequestHandler(_BaseHTTPRequestHandler):
    """This is the request handler in which we will read the contents of the incidents
    JSON file and return it in the response."""

    _INCIDENTS_FILENAME: str = "incidents.json"

    def _read_incidents_file_content(self) -> str:
        """Reads the content of the JSON file and returns it."""
        # If we are running the server for the first time, the incidents file might
        # not be created. We are going to wait for it to be created.
        while not _os.path.isfile(self._INCIDENTS_FILENAME):
            _sleep(1)
        with open(self._INCIDENTS_FILENAME, "r+") as f:
            return f.read()

    def do_GET(self) -> None:
        """Responds with a 200 - OK and the content of the JSON file"""
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        json_file_contents = self._read_incidents_file_content()
        self.wfile.write(json_file_contents.encode())


if __name__ == "__main__":
    print("Creating polling thread!")
    poll_thread = _PollingThread()
    poll_thread.start()

    server_address = ServerAddress()
    main_server = _HTTPServer(server_address, IncidentsRequestHandler)

    try:
        print(f"Server listening at {server_address.host}:{server_address.port}")
        main_server.serve_forever()
    except KeyboardInterrupt:
        pass

    print("Telling the polling thread to stop polling!")
    poll_thread.stop_polling()

    print("Joining the polling thread!")
    poll_thread.join()

    print("Stopping Server.")
    main_server.server_close()
