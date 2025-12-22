import requests                
import webbrowser         
import urllib      
from urllib.parse import urlencode, urlparse, parse_qs  
from http.server import HTTPServer, BaseHTTPRequestHandler  
import webbrowser
from http.server import HTTPServer

class RedirectHandler(BaseHTTPRequestHandler):
    """HTTP handler to capture the auth code from redirect."""
    
    def do_GET(self):
        # Parse query parameters from the URL.
        params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        # Store the authorization code on the server object.
        self.server.auth_code = params.get("code")[0] if "code" in params else None

        # Respond to the browser so the user knows they can close it.
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"<html><body><h1>Window can be closed..</h1></body></html>")