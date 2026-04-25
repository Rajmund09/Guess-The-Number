import contextlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import os
from pathlib import Path
import socket
import webbrowser


HOST = "127.0.0.1"
DEFAULT_PORT = 8000


class NoCacheHandler(SimpleHTTPRequestHandler):
    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()


def find_open_port(start_port: int) -> int:
    port = start_port
    while True:
        with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            if sock.connect_ex((HOST, port)) != 0:
                return port
        port += 1


def main() -> None:
    project_root = Path(__file__).resolve().parent
    os.chdir(project_root)

    port = find_open_port(DEFAULT_PORT)
    url = f"http://{HOST}:{port}/index.html"
    print(f"Serving Guess The Number at {url}")
    print("Press Ctrl+C to stop the server.")

    with contextlib.suppress(Exception):
        webbrowser.open(url)

    server = ThreadingHTTPServer((HOST, port), NoCacheHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
