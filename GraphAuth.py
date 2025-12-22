import requests
import time

class GraphAuthentication:
    def __init__(self, tenant_id: str, client_id: str, client_secret: str):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self._access_token = None
        self._expires_at = 0

    """fetches the token to navigate through the graph ecosystem including Sharepoint, not hitting the endpoint, just the one stored in memory
       also a new token if the old one exprired, expires in around 60 min. (Might need to look into if there is a refresh token)
    """
    def get_token(self) -> str:
        if not self._access_token or time.time() >= self._expires_at:
            self._fetch_token()
        return self._access_token

    def _fetch_token(self):
        url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
            "scope": "https://graph.microsoft.com/.default"
        }

        resp = requests.post(url, data=data)
        resp.raise_for_status()

        token = resp.json()
        self._access_token = token["access_token"]
        self._expires_at = time.time() + token["expires_in"] - 60
