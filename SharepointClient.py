import GraphAuth
import requests

class SharePointClient:
    def __init__(self, auth: GraphAuth, site_id: str):
        self.auth = auth
        self.site_id = site_id
        self.base_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}"

"""Downloads a file from a Sharepoint site."""
def download_file(self, file_path: str) -> bytes:
    url = f"{self.base_url}/drive/root:/{file_path}:/content"
    headers = {
        "Authorization": f"Bearer {self.auth.get_token()}"
    }
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.content


"""Uploads a file to a Sharepoint site."""
def upload_file(self, folder_path: str, filename: str, content: bytes):
    url = f"{self.base_url}/drive/root:/{folder_path}/{filename}:/content"
    headers = {
        "Authorization": f"Bearer {self.auth.get_token()}"
    }
    resp = requests.put(url, headers=headers, data=content)
    resp.raise_for_status()
    return resp.json()



