# Simitree SharePoint File Processing Dashboard

This project provides a Streamlit-based UI for browsing SharePoint document libraries, selecting files, and running a processing workflow using the Microsoft Graph API.

The system is designed to act as a front-end orchestration layer, with authentication, navigation, file retrieval, and upload handled via Graph. Actual file processing is currently represented by a placeholder for a Windows desktop application that will ingest and process the data.

---

## High-Level Architecture

```
Streamlit UI
   |
   |-- GraphAuthentication (OAuth2 client credentials)
   |
   |-- SharePointClient (Microsoft Graph API)
   |       - List files and folders
   |       - Download files as bytes
   |       - Upload processed outputs
   |
   |-- Processing Placeholder
           (Windows Desktop App not yet integrated)
```

---

## Key Components

### 1. GraphAuthentication

Handles OAuth2 authentication against Microsoft Entra ID (Azure AD) using the client credentials flow.

Responsibilities:

* Fetches access tokens for Microsoft Graph
* Caches tokens in memory
* Automatically refreshes expired tokens

Tokens are not fetched per request. They are reused until expiration, approximately 60 minutes.

---

### 2. SharePointClient

A thin wrapper around the Microsoft Graph v1.0 API.

Capabilities:

* List files and folders in a SharePoint drive
* Download files by ID or path as raw bytes
* Upload or overwrite files in SharePoint

This class is intentionally API-focused and contains no UI or business logic.

---

### 3. SharePointExplorer

Provides a logical file-explorer abstraction on top of SharePoint.

Purpose:

* Separate folders from files
* Enable navigation-style behavior
* Support UI-driven browsing without mutating SharePoint

This class strictly mirrors SharePoint’s structure. It does not upload, process, or modify files.

---

### 4. Streamlit Application

The Streamlit app provides:

* Folder-based navigation similar to a file explorer
* Multi-file selection using checkboxes
* Upload destination selection
* Step-by-step processing feedback using status components

What it does not do:

* No local file uploads
* No direct processing logic
* No filesystem writes

---

## Processing Logic Placeholder

At present, the processing step is implemented as a placeholder:

```python
processed_file_bytes = input_file_bytes
```

This represents the future integration point for a Windows desktop application or external executable that will:

* Ingest the downloaded file bytes
* Perform domain-specific processing
* Return processed output bytes back to the Streamlit app

Once integrated, the Streamlit UI will act purely as:

* An orchestrator
* A SharePoint input and output interface
* A user-facing control panel

---

## Environment Variables

The application expects the following environment variables, for example via a `.env` file:

```
TENANT_ID=your_tenant_id
CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret
DRIVE_ID=sharepoint_drive_id
```


## Typical User Flow

1. Authenticate automatically via Microsoft Graph
2. Browse SharePoint folders
3. Select one or more files
4. Choose a destination folder for outputs
5. Run processing
6. Processed files are uploaded back to SharePoint

---

## Design Principles

* Separation of concerns
* Stateless API calls
* Session-based UI state
* No filesystem dependency
* Future-ready external processing integration

## Future Enhancements

* Integrate the Windows desktop processing application
* Parallel file processing
* Progress streaming from the processing engine
* File-type validation
* Processing configuration options per run



## Notes

* Windows allows folder names containing dots, so folder and file detection relies on Graph metadata rather than filename heuristics
* All SharePoint interactions are performed via Microsoft Graph rather than SharePoint REST APIs
