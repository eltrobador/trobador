from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import parse_qs, urlparse

from .aladi import find_library_code, search_author_at_library


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        author = params.get("author", [None])[0]
        library = params.get("library", [None])[0]

        # CORS headers
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

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
            "library": {
                "name": library_name,
                "code": library_code
            },
            "books": books
        }).encode())
