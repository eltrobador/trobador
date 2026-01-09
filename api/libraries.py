from http.server import BaseHTTPRequestHandler
import json

from .aladi import get_all_libraries


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        libraries = get_all_libraries()
        result = [{"name": name, "code": code} for name, code in libraries.items()]

        self.wfile.write(json.dumps({
            "count": len(result),
            "libraries": result
        }).encode())
