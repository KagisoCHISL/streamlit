import requests
import time

class GraphAuthentication:
    """
    Handles authentication with Microsoft Graph API for accessing resources such as SharePoint.

    Attributes:
        tenant_id (str): The Azure tenant ID.
        client_id (str): The Azure application (client) ID.
        client_secret (str): The client secret for the application.
        _access_token (str): Cached access token for Graph API requests.
        _expires_at (float): Unix timestamp when the access token expires.
    """

    def __init__(self, tenant_id: str, client_id: str, client_secret: str):
        """
        Initializes the GraphAuthentication object with Azure app credentials.

        Args:
            tenant_id (str): Your Azure tenant ID.
            client_id (str): Your Azure application (client) ID.
            client_secret (str): The secret associated with your Azure application.
        """
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self._access_token = None
        self._expires_at = 0

    def get_token(self) -> str:
        """
        Retrieves a valid access token for the Microsoft Graph API.

        If a token is cached and not expired, it returns the cached token.
        Otherwise, it fetches a new token from the Microsoft identity platform.

        Returns:
            str: A valid access token for use in Graph API requests.
        """
        if not self._access_token or time.time() >= self._expires_at:
            self._fetch_token()
        return self._access_token

    def _fetch_token(self):
        """
        Fetches a new access token from the Microsoft identity platform.

        This is an internal method and should not be called directly outside
        the class. It updates the `_access_token` and `_expires_at` attributes.

        Raises:
            requests.exceptions.RequestException: If the HTTP request fails or
            the response contains an error.
        """
        url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
            "scope": "https://graph.microsoft.com/.default"
        }

        resp = requests.post(url, data=data)
        resp.raise_for_status()

        token_data = resp.json()
        self._access_token = token_data["access_token"]
        self._expires_at = time.time() + token_data["expires_in"] - 60  # Refresh 1 min before expiration
