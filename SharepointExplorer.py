from typing import Dict, List, Union

class SharePointExplorer:
    """
    Provides an in-memory representation of a SharePoint folder structure,
    allowing listing of files and folders for navigation purposes.
    """

    def __init__(self, client, drive_id: str):
        """
        Parameters:
            client: An instance of SharePointClient
            drive_id: ID of the SharePoint drive
        """
        self.client = client
        self.drive_id = drive_id

    def list_items(self, folder_path: str = "") -> Dict[str, List[str]]:
        """
        List folders and files under a given folder path.

        Parameters:
            folder_path (str): Folder path within SharePoint (root if empty)

        Returns:
            Dict[str, List[str]]: {
                "folders": [list of folder names],
                "files": [list of file names]
            }
        """
        all_items = self.client.list_items(self.drive_id, folder_id=None)  # You might need folder_id mapping
        folders, files = [], []

        for item in all_items:
            if item.get("folder"):  # Graph API returns "folder" key for folders
                folders.append(item["name"])
            else:
                files.append(item["name"])

        return {"folders": folders, "files": files}

    def navigate(self, current_path: str = "") -> Dict[str, Union[str, List[str]]]:
        """
        Returns the current folder path and its contents.

        Returns:
            Dict with current path and items:
            {
                "path": "current/folder/path",
                "folders": [...],
                "files": [...]
            }
        """
        items = self.list_items(current_path)
        return {
            "path": current_path or "/",
            "folders": items["folders"],
            "files": items["files"]
        }
