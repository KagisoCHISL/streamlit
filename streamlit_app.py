import streamlit as st
from dotenv import load_dotenv
from SharepointClient import SharePointClient
from GraphAuth import GraphAuthentication
import os

# Configure the Streamlit page layout and metadata.
st.set_page_config(
    page_title="Simitree Processing Dashboard",
    page_icon="⚙️",
    layout="wide"
)

# Page header and short description for the user.
st.title("Simitree File Processing Dashboard")
st.caption("Navigate SharePoint, select files, and run the process.")
st.divider()

# Initialize authentication and SharePoint client once per session.
# This block only runs on the first script execution for a user session.
if "client" not in st.session_state:
    load_dotenv()
    try:
        # Create the Graph authentication object using environment variables.
        auth = GraphAuthentication(
            tenant_id=os.getenv("TENANT_ID"),
            client_id=os.getenv("CLIENT_ID"),
            client_secret=os.getenv("CLIENT_SECRET")
        )

        # Store the authenticated SharePoint client and drive ID in session state.
        st.session_state.client = SharePointClient(auth.get_token())
        st.session_state.drive_id = os.getenv("DRIVE_ID")
        st.session_state.authenticated = True
    except Exception as e:
        # Stop execution if authentication fails.
        st.error(f"Authentication failed: {e}")
        st.session_state.authenticated = False
        st.stop()

# Prevent the app from running further if authentication was not successful.
if not st.session_state.authenticated:
    st.stop()

# Read commonly used session state values into local variables for convenience.
client = st.session_state.client
drive_id = st.session_state.drive_id

# Initialize navigation and selection state.
# These values persist across reruns for the duration of the session.
if "folder_stack" not in st.session_state:
    st.session_state.folder_stack = []  # Tracks the current browsing path.
if "selected_files" not in st.session_state:
    st.session_state.selected_files = []  # Stores selected file names and IDs.
if "upload_folder_stack" not in st.session_state:
    st.session_state.upload_folder_stack = []  # Tracks the upload destination path.
if "choosing_upload_dest" not in st.session_state:
    st.session_state.choosing_upload_dest = False  # Controls upload folder selection UI.

# Return the current folder ID based on the navigation stack.
# None represents the root of the drive.
def get_current_folder_id():
    return None if not st.session_state.folder_stack else st.session_state.folder_stack[-1][1]

# Build a human-readable path string for the current browsing location.
def get_current_path():
    return "/" if not st.session_state.folder_stack else "/" + "/".join(
        f[0] for f in st.session_state.folder_stack
    )

# Build a human-readable path string for the upload destination.
def get_upload_path():
    return "/" if not st.session_state.upload_folder_stack else "/" + "/".join(
        f[0] for f in st.session_state.upload_folder_stack
    )

# Build the upload folder path in the format expected by the SharePoint API.
def get_upload_folder_path():
    return "" if not st.session_state.upload_folder_stack else "/".join(
        f[0] for f in st.session_state.upload_folder_stack
    )

# SharePoint browsing section.
st.subheader("1. Browse SharePoint")

try:
    # Fetch all items in the current folder.
    current_folder_id = get_current_folder_id()
    all_items = client.list_items(drive_id, folder_id=current_folder_id)

    # Separate folders and files based on Graph API metadata.
    folders = [(item["name"], item["id"]) for item in all_items if "folder" in item]
    files = [(item["name"], item["id"]) for item in all_items if "file" in item]

    # Display the current browsing path.
    st.write(f"Current Path: `{get_current_path()}`")

    # Allow navigation back to the parent folder when not at the root.
    if st.session_state.folder_stack:
        if st.button("Back to Parent Folder", key="back_btn"):
            st.session_state.folder_stack.pop()
            st.rerun()

    st.divider()

    # Display folders as navigation buttons.
    if folders:
        st.write("Folders:")
        folder_cols = st.columns(min(len(folders), 4))
        for idx, (folder_name, folder_id) in enumerate(folders):
            if folder_cols[idx % 4].button(folder_name, key=f"folder_{folder_id}"):
                st.session_state.folder_stack.append((folder_name, folder_id))
                st.rerun()
        st.divider()

    # Display files with checkbox-based multi-selection.
    if files:
        st.write(f"Files in this folder ({len(files)} files):")
        for file_name, file_id in files:
            is_selected = any(f[1] == file_id for f in st.session_state.selected_files)

            if st.checkbox(file_name, value=is_selected, key=f"file_{file_id}"):
                if not is_selected:
                    st.session_state.selected_files.append((file_name, file_id))
            else:
                if is_selected:
                    st.session_state.selected_files = [
                        f for f in st.session_state.selected_files if f[1] != file_id
                    ]

        # Allow clearing all selected files at once.
        if st.session_state.selected_files:
            if st.button("Clear Selection"):
                st.session_state.selected_files = []
                st.rerun()
    else:
        st.info("No files in this folder.")

except Exception as e:
    # Catch and display any errors that occur while loading SharePoint items.
    st.error(f"Error loading files: {e}")
    import traceback
    st.code(traceback.format_exc())
    st.stop()

# Display a summary of selected files.
st.divider()
if st.session_state.selected_files:
    st.success(f"Selected {len(st.session_state.selected_files)} file(s):")
    for file_name, _ in st.session_state.selected_files:
        st.write(f"- {file_name}")
else:
    st.info("No files selected.")

# Processing section.
st.divider()
st.subheader("2. Run Processing")

# Upload destination selection.
st.write("Choose Upload Destination:")

col_path, col_btn = st.columns([3, 1])
with col_path:
    st.write(f"Current destination: `{get_upload_path()}`")
with col_btn:
    if st.button("Change Destination", key="change_dest_btn"):
        st.session_state.choosing_upload_dest = True

# Show upload destination navigation when enabled.
if st.session_state.choosing_upload_dest:
    st.info("Navigate to the folder where processed files should be uploaded.")

    try:
        current_upload_folder_id = (
            None if not st.session_state.upload_folder_stack
            else st.session_state.upload_folder_stack[-1][1]
        )

        upload_items = client.list_items(drive_id, folder_id=current_upload_folder_id)
        upload_folders = [(item["name"], item["id"]) for item in upload_items if "folder" in item]

        st.write(f"Navigating: `{get_upload_path()}`")

        col_back, col_select, col_cancel = st.columns(3)
        with col_back:
            if st.session_state.upload_folder_stack and st.button("Back", key="upload_back_btn"):
                st.session_state.upload_folder_stack.pop()
                st.rerun()

        with col_select:
            if st.button("Select This Folder", key="select_folder_btn", type="primary"):
                st.session_state.choosing_upload_dest = False
                st.rerun()

        with col_cancel:
            if st.button("Cancel", key="cancel_dest_btn"):
                st.session_state.choosing_upload_dest = False
                st.rerun()

        st.divider()

        if upload_folders:
            st.write("Available folders:")
            upload_folder_cols = st.columns(min(len(upload_folders), 4))
            for idx, (folder_name, folder_id) in enumerate(upload_folders):
                if upload_folder_cols[idx % 4].button(folder_name, key=f"upload_folder_{folder_id}"):
                    st.session_state.upload_folder_stack.append((folder_name, folder_id))
                    st.rerun()
        else:
            st.info("No subfolders in this location.")

    except Exception as e:
        st.error(f"Error loading folders: {e}")

    st.divider()

# Run processing action.
col1, col2 = st.columns([3, 1])
with col1:
    st.info("Select files, choose an upload destination, and click Run Process.")
with col2:
    run_button = st.button("Run Process", type="primary", use_container_width=True)

if run_button:
    if not st.session_state.selected_files:
        st.warning("Please select at least one file first.")
        st.stop()

    st.write(f"Processing {len(st.session_state.selected_files)} file(s).")

    # Process each selected file sequentially.
    for file_name, file_id in st.session_state.selected_files:
        with st.status(f"Processing {file_name}...", expanded=True) as status:
            try:
                status.write("Downloading file from SharePoint.")
                input_file_bytes = client.download_file(drive_id, file_id)

                #W##################################################################
                #Windows app needs to to be used here, and return the processed bytes to be uploaded.
                status.write("Processing file.")
                processed_file_bytes = input_file_bytes

                output_filename = f"processed_{file_name}"
                client.upload_file(
                    drive_id,
                    output_filename,
                    processed_file_bytes,
                    folder_path=get_upload_folder_path()
                )

                status.update(label=f"{file_name} completed.", state="complete")

            except Exception as e:
                status.update(label=f"{file_name} failed.", state="error")
                st.error(f"Error processing {file_name}: {e}")

    st.success("All files processed successfully.")

    # Allow clearing the file selection after processing completes.
    if st.button("Clear Selection After Processing"):
        st.session_state.selected_files = []
        st.rerun()

# Footer guidance for users.
st.divider()
st.caption("Tip: Navigate folders by clicking on them and select multiple files using checkboxes.")
