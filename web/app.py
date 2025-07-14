import json
import os
import sys
from http.server import SimpleHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from core.steel_plant import run_steel_plant

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/api/run'):
            qs = parse_qs(urlparse(self.path).query)
            supply = qs.get('type', ['hazer'])[0]
            demand = [7550 / 24] * 24
            result = run_steel_plant(demand, supply_type=supply)
            data = json.dumps(result).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        else:
            super().do_GET()


def main():
    HTTPServer(('0.0.0.0', 8000), Handler).serve_forever()


if __name__ == '__main__':
    main()
