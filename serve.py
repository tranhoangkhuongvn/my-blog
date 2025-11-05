#!/usr/bin/env python3
"""
Simple HTTP server to preview the static site locally
"""
import http.server
import socketserver
import os
import sys
from pathlib import Path

# Configuration
PORT = 8001
DIRECTORY = "output"

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def end_headers(self):
        # Add headers for better development experience
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()
    
    def log_message(self, format, *args):
        # Custom log format
        sys.stderr.write(f"[{self.log_date_time_string()}] {format % args}\n")

def serve():
    """Start the development server"""
    os.chdir(Path(__file__).parent)
    
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"🚀 Server running at http://localhost:{PORT}")
        print(f"📁 Serving files from: {DIRECTORY}/")
        print(f"Press Ctrl+C to stop the server\n")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Server stopped")
            sys.exit(0)

if __name__ == "__main__":
    serve()
