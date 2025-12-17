import streamlit as st
import pandas as pd
import numpy as np
import matplotlib as plt


st.title("FILE TRANSFORMER")

st.write("Select an Excel file from your SharePoint Input folder, preview its contents, and apply transformations to process your data.")

#I need to be able to connect this to all the file names available there.
#But do I add a file navigation system first, root site first, then drill down

"""
1. GET /sites/{site-id}/drives.  
   From this I select a single drive_id (usually “Documents”).  
   (This is done once, not in a loop.)

<------------------------------- Navigation loop starts here ------------------------------->

2. GET /drives/{drive-id}/root/children.  
   From this response, the user selects either:
   - a folder → obtain its folder_id
   - a file   → obtain its file_id

3. GET /drives/{drive-id}/items/{folder-id}/children.  
   From this response, the user again select.s either:
   - a folder → obtain the next folder_id
   - a file   → obtain the file_id.

4. Repeat step 3 for each folder selection until the response item selected
   contains a `file` object instead of a `folder` object.

   - Presence of `folder` → folder  
   - Presence of `file`   → file  

5. Once a file is selected:
   - stop the navigation loop
   - confirm the file selection with the user

<---------------------------------------------------------------------------------------------------->

"""


