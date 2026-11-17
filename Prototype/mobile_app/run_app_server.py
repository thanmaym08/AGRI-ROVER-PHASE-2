#!/usr/bin/env python3
"""
Agri Rover Mobile App Local Host Server
File: Prototype/mobile_app/run_app_server.py

Hosts the responsive mobile application locally on your PC so you can
connect from any phone on the same Wi-Fi network.
"""

import http.server
import socketserver
import socket
import os

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't need to be reachable
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        # Enable CORS for easy prototyping
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

def main():
    local_ip = get_local_ip()
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("=" * 60)
        print("       🌿 AGRI ROVER MOBILE APP WEB SERVER STARTED         ")
        print("=" * 60)
        print(f"Local Browser URL : http://localhost:{PORT}")
        print(f"Phone Browser URL : http://{local_ip}:{PORT}")
        print("=" * 60)
        print(f"Open 'http://{local_ip}:{PORT}' in Chrome or Safari on your phone!")
        print("Press Ctrl+C to terminate the server.\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")

if __name__ == "__main__":
    main()
