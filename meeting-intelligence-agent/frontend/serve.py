#!/usr/bin/env python3
"""
Simple frontend server - serves static HTML while waiting for full React frontend
Runs on http://localhost:5173 to match Vite development server port
"""

import http.server
import socketserver
import os
from pathlib import Path

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/index-simple.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

if __name__ == '__main__':
    # Change to frontend directory
    frontend_dir = Path(__file__).parent.absolute()
    os.chdir(frontend_dir)
    
    PORT = 5173
    Handler = MyHTTPRequestHandler
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"\n{'='*60}")
        print(f"📱 Frontend Server")
        print(f"{'='*60}")
        print(f"✅ Running on http://localhost:{PORT}")
        print(f"📂 Serving from: {frontend_dir}")
        print(f"\n📝 Note: This is a temporary server.")
        print(f"   Once Node.js is installed, run:")
        print(f"   npm install")
        print(f"   npm run dev")
        print(f"\n🛑 Press Ctrl+C to stop\n")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n✅ Server stopped")
