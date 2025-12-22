import requests
from typing import List, Dict
import json

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
            List[Dict]: A list of items (files and folders) in the folder
        """
        if folder_id:
            url = f"{self.base_url}/drives/{drive_id}/items/{folder_id}/children"
        else:
            url = f"{self.base_url}/drives/{drive_id}/root/children"

        response = requests.get(url, headers=self._headers())
        response.raise_for_status()

        data = response.json()
        items = data.get("value", [])

        file_names = [] 
        for item in items:
            file_names.append(item["name"])


        # print(file_names)

        return file_names
    

    def download_file(self, drive_id: str, file_name: str, save_path: str = None) -> None:
        """
        Download a file from the root of a drive.

        Parameters:
            drive_id (str): The ID of the document library (drive)
            file_name (str): The name of the file to download
            save_path (str, optional): Local path to save the file. Defaults to current directory.
        """
        url = f"{self.base_url}/drives/{drive_id}/root:/{file_name}:/content"
        response = requests.get(url, headers=self._headers())
        response.raise_for_status()

        if not save_path:
            save_path = file_name

        with open(save_path, "wb") as f:
            f.write(response.content)

        print(f"Downloaded '{file_name}' to '{save_path}'")


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



