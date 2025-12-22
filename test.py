from GraphAuth import GraphAuthentication
import os
from dotenv import load_dotenv
from SharepointClient import SharePointClient

load_dotenv()

# Load environment variables
tenant_id = os.getenv("TENANT_ID")
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
site_id = os.getenv("SITE_ID") 
drive_id = os.getenv("DRIVE_ID")

# Authenticate
auth = GraphAuthentication(
    tenant_id=tenant_id,
    client_id=client_id,
    client_secret=client_secret
)

sharepoint_client = SharePointClient(auth.get_token())

# List items in the drive
file_names = sharepoint_client.list_items(drive_id=drive_id)
print("Files in drive:", file_names)

# Upload a local file
local_file_path = "Book1.xlsx"
with open(local_file_path, "rb") as f:
    file_bytes = f.read()

upload_response = sharepoint_client.upload_file(
    drive_id=drive_id,
    file_name="Book1.xlsx",
    file_content=file_bytes
)

print("Uploaded file info:", upload_response.get("name"))
