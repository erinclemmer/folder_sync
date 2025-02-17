# SSH Folder Sync

This Python script monitors a local folder for changes and synchronizes them with a remote folder over SSH. It uses [Fabric](https://www.fabfile.org/) and its underlying SFTP capabilities to keep both folders in sync. Whenever files are created, modified, deleted, or moved locally, the corresponding changes are pushed to the remote server.

---

## Table of Contents
1. [Features](#features)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Usage](#usage)
6. [How It Works](#how-it-works)
7. [Troubleshooting](#troubleshooting)

---

## Features
- **Automatic Folder Creation**: Ensures that any missing folders on the remote side are created.
- **File Synchronization**:
  - **Initial Sync**: On script startup, it transfers any files that are missing or have been updated on the local folder to the remote folder.
  - **Real-time Sync**: Continually watches the local folder for changes and pushes these changes (additions, modifications, deletions, moves) to the remote server.
- **Selective Updates**: Only replaces remote files if the local file is newer.

---

## Prerequisites
- **Python 3.7+** is recommended.
- **Fabric** (v2 or above) and its dependencies:
  - [Paramiko](https://www.paramiko.org/)
- A valid SSH setup with key-based authentication (for passwordless access, configured in `config.json`).

---

## Installation
1. **Clone or Download** this repository to your local machine.
2. **Install Dependencies**:
   ```bash
   pip install fabric paramiko
   ```
3. **Verify** that you have a valid SSH key pair configured for the remote server.

---

## Configuration
All configuration values are stored in a `config.json` file at the root of the project. The application looks for `config.json` in the same directory as the script.

Below is an example `config.json`:

```json
{
  "ip": "192.168.1.10",
  "user": "myuser",
  "port": 22,
  "private_key": "/path/to/private_key.pem",
  "local_folder": "C:/Users/MyName/LocalSyncFolder",
  "remote_folder": "/home/myuser/RemoteSyncFolder"
}
```

| Property       | Description                                                         |
|----------------|---------------------------------------------------------------------|
| **ip**         | IP address (or hostname) of the remote server                       |
| **user**       | Username to log into the remote server                              |
| **port**       | SSH port (default is `22`)                                         |
| **private_key**| Path to your private SSH key file                                   |
| **local_folder**| Absolute path of the local folder to synchronize                  |
| **remote_folder**| Absolute path of the remote folder to synchronize                |

**Important**: The script will refuse to run if any of these fields are missing or empty.

---

## Usage
1. **Prepare the Remote Server**:
   - Ensure the remote folder specified in `config.json` exists on the server. If it does not exist, create it.
   - Make sure your SSH key (`private_key`) is properly authorized on the remote server.
2. **Run the Script**:
   ```bash
   python sync.py
   ```
   Replace `sync.py` with the actual name of your script if it differs.

3. **Real-Time Sync**:
   - The script will perform an initial sync of files from the local folder to the remote folder.
   - It will then continue to watch the local folder for changes. Any time files are added, modified, deleted, or moved, those changes are immediately pushed to the remote folder.

---

## How It Works

1. **Script Initialization**  
   The script reads `config.json` to gather:
   - Connection details (`ip`, `user`, `port`, `private_key`)
   - Folder paths (`local_folder`, `remote_folder`)

2. **Setting Up the SFTP Connection**  
   A [Fabric `Connection`](https://docs.fabfile.org/en/stable/api/connection.html) is established, and its SFTP client is used to manage files on the remote host.

3. **Initial Transfer**  
   - The `transfer_folder('')` call performs a one-time pass over every file in the local folder.
   - Files that don’t exist on the remote host are transferred.
   - Files that exist but have an older modification time on the remote are replaced with the local version.

4. **File Watching**  
   - The script uses a `watch_folder` function (imported from `watch.py`) to track file events in the local folder. 
   - Depending on the event type (add, delete, modify, move), the appropriate action is taken:
     - **Add/Modify**: The file is uploaded to the remote folder.
     - **Delete**: The file is removed from the remote folder.
     - **Move**: The old remote file is deleted, and the new file is uploaded.

5. **Folder Creation**  
   - If a subfolder is created locally, the script ensures the corresponding folder is also created on the remote server.

---

## Troubleshooting

- **SSH Permission Issues**: If you see errors related to SSH permissions, ensure your private key is correct and has the proper permissions on the local system, and that the corresponding public key is authorized on the remote server.
- **Remote Folder Not Found**: The script will raise an exception if the remote folder does not exist. Create the folder on the remote system before running the script.
- **Local Path Issues**: On some operating systems, backslashes vs. forward slashes can cause path issues. The script attempts to handle this by converting backslashes to forward slashes, but be mindful of path conventions.
- **Network Disconnects**: If your connection to the remote server is unstable, the script may fail to transfer certain files. Restart the script once the connection is stable again.
