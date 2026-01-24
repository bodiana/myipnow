import http.server
import socketserver
import os

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # If the file doesn't exist, try adding .html
        path = self.translate_path(self.path)
        if not os.path.exists(path) and not path.endswith('/'):
            if os.path.exists(path + ".html"):
                self.path += ".html"
        return super().do_GET()

with socketserver.TCPServer(("", 8000), MyHandler) as httpd:
    print("Server started at http://localhost:8000")
    httpd.serve_forever()