from GraphAuth import GraphAuthentication
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

# Load environment variables
tenant_id = os.getenv("TENANT_ID")
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
site_id = os.getenv("SITE_ID") 
drive_id = os.getenv("DRIVE_ID")

# Initialize authentication
auth = GraphAuthentication(
    tenant_id=tenant_id,
    client_id=client_id,
    client_secret=client_secret
)

headers = {
    "Authorization": f"Bearer {auth.get_token()}"
}


# 3️⃣ Optionally, list root items in this drive
root_items_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root/children"
root_resp = requests.get(root_items_url, headers=headers)
root_resp.raise_for_status()
items = root_resp.json()

print("\nFiles and folders in 'Shared Documents' root:")
print(json.dumps(items, indent=4))
