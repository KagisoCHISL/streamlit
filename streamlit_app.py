import streamlit as st
import os
from dotenv import load_dotenv
from SharepointClient import SharePointClient
from GraphAuth import GraphAuthentication

# Page configuration.
st.set_page_config(page_title="SharePoint File Manager", page_icon="📂", layout="wide")

# Initialization of the session state.
if 'client' not in st.session_state:
    load_dotenv()
    auth = GraphAuthentication(
        tenant_id=os.getenv("TENANT_ID"),
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET")
    )
    st.session_state.client = SharePointClient(auth.get_token())
    st.session_state.drive_id = os.getenv("DRIVE_ID")

# The header of the site.
st.title("🗁 SharePoint File Manager")
st.divider()

# Sidebar to upload and download the file.
with st.sidebar:
    st.header("Select File")
    
    if st.button("⟲ Refresh"):
        st.rerun()
    

    files = st.session_state.client.list_items(st.session_state.drive_id)  # Gets the list of filenames from sharepoint.
    selected_file = st.selectbox("Choose a file:", [""] + files) # [""] just for the default value in the field to be empty, I do not like it where it shows the first file.
    
    # If a file was selected and the user confirms with the download button that they want it downloaded, download the file.
    if selected_file and st.button("🡻 Download File", type="primary"):
        try:
            st.session_state.client.download_file(st.session_state.drive_id, selected_file)
            with open(selected_file, "rb") as f:
                st.download_button("⎙ Save to Computer", f, selected_file)

            # Report back to the user for success, user feedback is very important!
            st.success(f"Downloaded {selected_file}")
        except Exception as e:
            st.error(f"Error: {e}")

# Main panel, split into two, one to display the file's metadata and one for uploading.
col1, col2 = st.columns(2)

# Metadata section...
with col1:
    st.subheader("📊 File Metadata")
    if selected_file:
        st.write(f"**File Name:** {selected_file}")
        st.write(f"**File Type:** {selected_file.split('.')[-1].upper()}")
        st.info("Select a file to view full metadata")
    else:
        st.info("Select a file from the sidebar")

# Upload file section.
with col2:
    st.subheader("🢁 Upload New File")
    uploaded_file = st.file_uploader("Choose a file") #OPens file manager.
    folder_path = st.text_input("Folder Path (optional)", value="/") #The actual URL can be inputted.
    
    if st.button("Upload to SharePoint", type="primary"):
        if uploaded_file:
            try:
                # Read the bytes of the file and it's path.
                file_bytes = uploaded_file.read()
                clean_path = folder_path.strip('/')

                #File uploading.
                st.session_state.client.upload_file(
                    st.session_state.drive_id,
                    uploaded_file.name,
                    file_bytes,
                    clean_path if clean_path else ""
                )

                #Report back to the user that the file upload was succesful.
                st.success(f"Uploaded {uploaded_file.name}")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Please select a file")

