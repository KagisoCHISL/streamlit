import streamlit as st
from dotenv import load_dotenv
from SharepointClient import SharePointClient
from GraphAuth import GraphAuthentication
import os

# Page setup
st.set_page_config(
    page_title="Simitree Processing Dashboard",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ Simitree File Processing Dashboard")
st.caption("Navigate SharePoint, select files, and run the processing workflow.")
st.divider()

# Session initialization
if "client" not in st.session_state:
    load_dotenv()
    try:
        auth = GraphAuthentication(
            tenant_id=os.getenv("TENANT_ID"),
            client_id=os.getenv("CLIENT_ID"),
            client_secret=os.getenv("CLIENT_SECRET")
        )
        st.session_state.client = SharePointClient(auth.get_token())
        st.session_state.drive_id = os.getenv("DRIVE_ID")
        st.session_state.authenticated = True
    except Exception as e:
        st.error(f"Authentication failed: {e}")
        st.session_state.authenticated = False
        st.stop()

if not st.session_state.authenticated:
    st.stop()

client = st.session_state.client
drive_id = st.session_state.drive_id

# Initialize navigation state
if "folder_stack" not in st.session_state:
    st.session_state.folder_stack = []  # Stack of (folder_name, folder_id) tuples
if "selected_files" not in st.session_state:
    st.session_state.selected_files = []  # List of (file_name, file_id) tuples
if "upload_folder_stack" not in st.session_state:
    st.session_state.upload_folder_stack = []  # Separate stack for upload destination
if "choosing_upload_dest" not in st.session_state:
    st.session_state.choosing_upload_dest = False

# Helper function to get current folder_id
def get_current_folder_id():
    if not st.session_state.folder_stack:
        return None  # Root
    return st.session_state.folder_stack[-1][1]

# Helper function to get current path display
def get_current_path():
    if not st.session_state.folder_stack:
        return "/"
    return "/" + "/".join([f[0] for f in st.session_state.folder_stack])

# Helper function to get upload destination path
def get_upload_path():
    if not st.session_state.upload_folder_stack:
        return "/"
    return "/" + "/".join([f[0] for f in st.session_state.upload_folder_stack])

# Helper function to get upload folder path for API
def get_upload_folder_path():
    if not st.session_state.upload_folder_stack:
        return ""
    return "/".join([f[0] for f in st.session_state.upload_folder_stack])

# SharePoint File Explorer
st.subheader("1️⃣ Browse SharePoint")

try:
    # Get items from current folder
    current_folder_id = get_current_folder_id()
    all_items = client.list_items(drive_id, folder_id=current_folder_id)
    
    # Separate folders and files
    folders = [(item["name"], item["id"]) for item in all_items if "folder" in item]
    files = [(item["name"], item["id"]) for item in all_items if "file" in item]
    
    # Display breadcrumb
    st.write(f"📂 **Current Path:** `{get_current_path()}`")
    
    # Back button
    if st.session_state.folder_stack:
        if st.button("⬅️ Back to Parent Folder", key="back_btn"):
            st.session_state.folder_stack.pop()
            st.rerun()
    
    st.divider()
    
    # Display folders
    if folders:
        st.write("**📁 Folders:**")
        folder_cols = st.columns(min(len(folders), 4))
        for idx, (folder_name, folder_id) in enumerate(folders):
            col_idx = idx % 4
            if folder_cols[col_idx].button(f"📁 {folder_name}", key=f"folder_{folder_id}"):
                st.session_state.folder_stack.append((folder_name, folder_id))
                st.rerun()
        st.divider()
    
    # Display files with multi-select
    if files:
        st.write(f"**📄 Files in this folder:** ({len(files)} files)")
        
        # Create checkboxes for each file
        for file_name, file_id in files:
            # Check if file is currently selected
            is_selected = any(f[0] == file_name and f[1] == file_id for f in st.session_state.selected_files)
            
            # Checkbox for selection
            if st.checkbox(
                f"📄 {file_name}",
                value=is_selected,
                key=f"file_{file_id}"
            ):
                if not is_selected:
                    st.session_state.selected_files.append((file_name, file_id))
            else:
                if is_selected:
                    st.session_state.selected_files = [
                        f for f in st.session_state.selected_files 
                        if not (f[0] == file_name and f[1] == file_id)
                    ]
        
        # Clear selection button
        if st.session_state.selected_files:
            if st.button("🗑️ Clear Selection"):
                st.session_state.selected_files = []
                st.rerun()
    else:
        st.info("No files in this folder")
    
except Exception as e:
    st.error(f"Error loading files: {e}")
    import traceback
    st.code(traceback.format_exc())
    st.stop()

# Display selected files
st.divider()
if st.session_state.selected_files:
    st.success(f"✅ **Selected {len(st.session_state.selected_files)} file(s):**")
    for file_name, file_id in st.session_state.selected_files:
        st.write(f"  • {file_name}")
else:
    st.info("No files selected")

# Run Processing Section
st.divider()
st.subheader("2️⃣ Run Processing")

# Upload destination selector
st.write("**📁 Choose Upload Destination:**")

col_path, col_btn = st.columns([3, 1])
with col_path:
    st.write(f"Current destination: `{get_upload_path()}`")
with col_btn:
    if st.button("📂 Change Destination", key="change_dest_btn"):
        st.session_state.choosing_upload_dest = True

# Show folder picker modal
if st.session_state.choosing_upload_dest:
    st.info("👇 Navigate to the folder where you want to upload processed files, then click 'Select This Folder'")
    
    try:
        # Get current folder_id for upload navigation
        current_upload_folder_id = None if not st.session_state.upload_folder_stack else st.session_state.upload_folder_stack[-1][1]
        upload_items = client.list_items(drive_id, folder_id=current_upload_folder_id)
        upload_folders = [(item["name"], item["id"]) for item in upload_items if "folder" in item]
        
        # Show current path
        st.write(f"📂 **Navigating:** `{get_upload_path()}`")
        
        # Back button for upload navigation
        col_back, col_select, col_cancel = st.columns([1, 1, 1])
        with col_back:
            if st.session_state.upload_folder_stack and st.button("⬅️ Back", key="upload_back_btn"):
                st.session_state.upload_folder_stack.pop()
                st.rerun()
        
        with col_select:
            if st.button("✅ Select This Folder", key="select_folder_btn", type="primary"):
                st.session_state.choosing_upload_dest = False
                st.success(f"Upload destination set to: {get_upload_path()}")
                st.rerun()
        
        with col_cancel:
            if st.button("❌ Cancel", key="cancel_dest_btn"):
                st.session_state.choosing_upload_dest = False
                st.rerun()
        
        st.divider()
        
        # Display folders for upload destination
        if upload_folders:
            st.write("**Available folders:**")
            upload_folder_cols = st.columns(min(len(upload_folders), 4))
            for idx, (folder_name, folder_id) in enumerate(upload_folders):
                col_idx = idx % 4
                if upload_folder_cols[col_idx].button(f"📁 {folder_name}", key=f"upload_folder_{folder_id}"):
                    st.session_state.upload_folder_stack.append((folder_name, folder_id))
                    st.rerun()
        else:
            st.info("No subfolders in this location")
    
    except Exception as e:
        st.error(f"Error loading folders: {e}")
    
    st.divider()

col1, col2 = st.columns([3, 1])
with col1:
    st.info("Select files above, choose upload destination, and click 'Run Process'")
with col2:
    run_button = st.button("🚀 Run Process", type="primary", use_container_width=True)

if run_button:
    if not st.session_state.selected_files:
        st.warning("⚠️ Please select at least one file first.")
        st.stop()
    
    st.write(f"Processing {len(st.session_state.selected_files)} file(s)...")
    
    for file_name, file_id in st.session_state.selected_files:
        with st.status(f"Processing {file_name}...", expanded=True) as status:
            try:
                # Step 1: Download using file_id
                status.write("📥 Downloading file from SharePoint...")
                input_file_bytes = client.download_file(drive_id, file_id)
                status.write(f"✓ Downloaded {len(input_file_bytes)} bytes")
                
                # Step 2: Process (placeholder)
                status.write("⚙️ Processing file...")
                processed_file_bytes = input_file_bytes  # Replace with actual processing
                status.write("✓ Processing completed")
                
                # Step 3: Upload
                upload_path = get_upload_folder_path()
                status.write(f"📤 Uploading processed file to '{get_upload_path()}'...")
                output_filename = f"processed_{file_name}"
                
                upload_response = client.upload_file(
                    drive_id,
                    output_filename,
                    processed_file_bytes,
                    folder_path=upload_path
                )
                status.write(f"✓ Uploaded as '{output_filename}' to {get_upload_path()}")
                
                status.update(label=f"✅ {file_name} completed!", state="complete")
                
            except Exception as e:
                status.update(label=f"❌ {file_name} failed", state="error")
                st.error(f"Error processing {file_name}: {str(e)}")
                import traceback
                st.code(traceback.format_exc())
    
    st.success(f"🎉 All files processed!")
    
    # Clear selection after processing
    if st.button("Clear Selection After Processing"):
        st.session_state.selected_files = []
        st.rerun()

# Footer
st.divider()
st.caption("💡 Tip: Navigate folders by clicking on them, select multiple files with checkboxes")