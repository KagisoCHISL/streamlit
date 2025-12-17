    
import requests                
import webbrowser         
import urllib      
from urllib.parse import urlencode, urlparse, parse_qs  
from http.server import HTTPServer, BaseHTTPRequestHandler  

class GraphAuthentication:

    def __init__(self, tenant_id: str, client_id: str, client_secret: str, redirect_uri: str):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.access_token = None
        self.auth_url = self.get_auth_url()
        self.auth_code = self.get_auth_code()

    """Helper method to build auth URL"""
    def get_auth_url(self, state="12345"):
        base_url = f'https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/authorize'
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": "Files.ReadWrite Sites.ReadWrite.All offline_access",
            "response_mode": "query",
            "state": state
        }
        return f"{base_url}?{urlencode(params)}"

    """Open browser and capture authorization code automatically"""
    def get_auth_code(self):
        import webbrowser
        from http.server import HTTPServer

        # Open the browser to let user sign in.
        webbrowser.open(self.auth_url)

        # Start HTTP server to listen for redirect with auth code (We need to capture this.)
        server_address = ('localhost', 8000)  # This address must match the redirect_url even the port num.
        server = HTTPServer(server_address, RedirectHandler)
        print("Waiting for authorization code.")
        server.handle_request()  # Blocks until the user authenticates and redirects.

        auth_code = server.auth_code
        print("Authorization code received:", auth_code) #needs to be removed.
        return auth_code

    """Exchange authorization code for access token."""
    def request_token(self):
        token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        data = {
            "client_id": self.client_id,
            "scope": "Files.ReadWrite Sites.ReadWrite.All offline_access",
            "code": self.auth_code,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code",
            "client_secret": self.client_secret
        }
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        self.access_token = response.json()["access_token"]
        return response.json()


class RedirectHandler(BaseHTTPRequestHandler):
    """HTTP handler to capture the auth code from redirect."""
    
    def do_GET(self):
        # Parse query parameters from the URL
        params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        # Store the authorization code on the server object
        self.server.auth_code = params.get("code")[0] if "code" in params else None

        # Respond to the browser so the user knows they can close it.
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"<html><body><h1>Window can be closed..</h1></body></html>")

if __name__ == "___main___":
    print("Kagiso says Hello.")