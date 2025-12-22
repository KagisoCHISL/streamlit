import requests
from typing import List, Dict

class SharePointClient:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://graph.microsoft.com/v1.0"

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}"
        }

    def list_items(self, drive_id: str, folder_id: str = None) -> List[Dict]:
        """
        List files and folders in a drive.

        Parameters:
            drive_id (str): The ID of the document library (drive)
            folder_id (str, optional): The ID of a specific folder. If None, lists root folder.

        Returns:
            List[Dict]: A list of items (files and folders) in the folder with metadata
        """
        if folder_id:
            url = f"{self.base_url}/drives/{drive_id}/items/{folder_id}/children"
        else:
            url = f"{self.base_url}/drives/{drive_id}/root/children"

        response = requests.get(url, headers=self._headers())
        response.raise_for_status()

        data = response.json()
        items = data.get("value", [])

        return items

    def download_file(self, drive_id: str, file_id: str) -> bytes:
        """
        Download a file from SharePoint using its file ID and return its content as bytes.

        Parameters:
            drive_id (str): The ID of the document library (drive)
            file_id (str): The ID of the file to download

        Returns:
            bytes: The content of the file
        """
        url = f"{self.base_url}/drives/{drive_id}/items/{file_id}/content"
        response = requests.get(url, headers=self._headers())
        response.raise_for_status()

        return response.content

    def download_file_by_path(self, drive_id: str, file_path: str) -> bytes:
        """
        Download a file from SharePoint using its path and return its content as bytes.

        Parameters:
            drive_id (str): The ID of the document library (drive)
            file_path (str): The path to the file (e.g., "folder1/folder2/file.xlsx")

        Returns:
            bytes: The content of the file
        """
        url = f"{self.base_url}/drives/{drive_id}/root:/{file_path}:/content"
        response = requests.get(url, headers=self._headers())
        response.raise_for_status()

        return response.content

    def upload_file(self, drive_id: str, file_name: str, file_content: bytes, folder_path: str = "") -> dict:
        """
        Upload or overwrite a file in a drive.

        Parameters:
            drive_id (str): The ID of the document library (drive)
            file_name (str): The name of the file to upload
            file_content (bytes): The content of the file
            folder_path (str, optional): Folder path inside the drive (defaults to root)

        Returns:
            dict: JSON response from Graph API
        """
        if folder_path:
            url = f"{self.base_url}/drives/{drive_id}/root:/{folder_path}/{file_name}:/content"
        else:
            url = f"{self.base_url}/drives/{drive_id}/root:/{file_name}:/content"

        response = requests.put(url, headers=self._headers(), data=file_content)
        response.raise_for_status()
        return response.json()