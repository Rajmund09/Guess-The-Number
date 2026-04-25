from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import webbrowser


HOST = "127.0.0.1"
PORT = 8000


def main() -> None:
    url = f"http://{HOST}:{PORT}/index.html"
    print(f"Serving Guess The Number at {url}")
    print("Press Ctrl+C to stop the server.")

    try:
        webbrowser.open(url)
    except Exception:
        pass

    server = ThreadingHTTPServer((HOST, PORT), SimpleHTTPRequestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
