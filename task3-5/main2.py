from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import os

HOST = "0.0.0.0"
PORT = int(os.getenv("PORT", 8000))

def lcm(x: int, y: int):
    if x == 0 or y == 0:
        return "0"
    elif x < 0 or y < 0:
        return "NaN"
    a, b = x, y
    while y != 0:
        x, y = y, x % y
    
    return  str((a * b) // x) 

class HTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        payload = parse_qs(parsed_url.query)

        try:
            x = int(payload.get("x")[0])
            y = int(payload.get("y")[0])
            result = lcm(x,y)
        except Exception:
            result = "NaN"

        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(bytes(result, "utf-8"))


server = HTTPServer((HOST, PORT), HTTPRequestHandler)
server.serve_forever()
server.server_close()
