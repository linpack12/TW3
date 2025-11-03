"""
Simple local HTTP server for testing HTML files
Run this before running demo_part_2.py

Usage:
    python run_local_server.py
"""

import http.server
import socketserver
from pathlib import Path

PORT = 8888
DIRECTORY = Path(__file__).parent

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"✓ Local HTTP server started on http://127.0.0.1:{PORT}")
        print(f"✓ Serving files from: {DIRECTORY}")
        print(f"✓ Available URLs:")
        print(f"  - http://127.0.0.1:{PORT}/page1.html")
        print(f"  - http://127.0.0.1:{PORT}/page2.html")
        print(f"\nPress Ctrl+C to stop the server")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n✓ Server stopped")