import requests
from typing import List, Dict
from GraphAuth import GraphAuth


class SharePointClient:
    def __init__(self, auth: GraphAuth, site_id: str, drive_id: str):
        self.auth = auth
        self.site_id = site_id
        self.drive_id = drive_id
        self.base_url = "https://graph.microsoft.com/v1.0"

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.auth.get_token()}"
        }


    """
    List all the drives in the site. (AKA Document libraries)    
    """


    def list_drives(self) -> List[Dict]:

        url = f"{self.base_url}/sites/{self.site_id}/drives"
        resp = requests.get(url, headers=self._headers())
        resp.raise_for_status()
        return resp.json().get("value", [])

    """List files and folders in the root of the drive."""
    def list_root_items(self) -> List[Dict]:
 
        url = f"{self.base_url}/drives/{self.drive_id}/root/children"
        resp = requests.get(url, headers=self._headers())
        resp.raise_for_status()
        return resp.json().get("value", [])
    
    """List files and folders inside a specific folder."""
    def list_folder_items(self, folder_id: str) -> List[Dict]:

        url = f"{self.base_url}/drives/{self.drive_id}/items/{folder_id}/children"
        resp = requests.get(url, headers=self._headers())
        resp.raise_for_status()
        return resp.json().get("value", [])

    """Get metadata for a file or folder."""
    def get_item(self, item_id: str) -> Dict:

        url = f"{self.base_url}/drives/{self.drive_id}/items/{item_id}"
        resp = requests.get(url, headers=self._headers())
        resp.raise_for_status()
        return resp.json()

  
    """Download a file using its path."""
    def download_file(self, file_path: str) -> bytes:

        url = f"{self.base_url}/drives/{self.drive_id}/root:/{file_path}:/content"
        resp = requests.get(url, headers=self._headers())
        resp.raise_for_status()
        return resp.content

    """Upload or overwrite a file in a specific folder."""
    def upload_file(self, folder_path: str, filename: str, content: bytes) -> Dict:

        url = f"{self.base_url}/drives/{self.drive_id}/root:/{folder_path}/{filename}:/content"
        resp = requests.put(url, headers=self._headers(), data=content)
        resp.raise_for_status()
        return resp.json()
