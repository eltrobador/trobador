#!/usr/bin/env python3
"""
Local development API server.
Run this alongside `npm run dev` for full-stack local development.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from urllib.parse import parse_qs, urlparse

from aladi import find_library_code, search_author_at_library, get_all_libraries


class APIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        if path == "/api/search":
            self.handle_search(params)
        elif path == "/api/libraries":
            self.handle_libraries()
        else:
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

    def handle_search(self, params):
        author = params.get("author", [None])[0]
        library = params.get("library", [None])[0]

        if not author or not library:
            self.wfile.write(json.dumps({
                "error": "Missing required parameters: author, library"
            }).encode())
            return

        result = find_library_code(library)
        if not result:
            self.wfile.write(json.dumps({
                "error": f"Library not found: {library}"
            }).encode())
            return

        library_name, library_code = result
        books = search_author_at_library(author, library_name, library_code)

        self.wfile.write(json.dumps({
            "author": author,
            "library": {"name": library_name, "code": library_code},
            "books": books
        }).encode())

    def handle_libraries(self):
        libraries = get_all_libraries()
        result = [{"name": name, "code": code} for name, code in libraries.items()]
        self.wfile.write(json.dumps({"count": len(result), "libraries": result}).encode())

    def log_message(self, format, *args):
        print(f"[API] {args[0]}")


if __name__ == "__main__":
    port = 3001
    server = HTTPServer(("localhost", port), APIHandler)
    print(f"API server running at http://localhost:{port}")
    server.serve_forever()
