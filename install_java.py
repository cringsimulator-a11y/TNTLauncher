import os
import re
import subprocess
import sys

# ----------------- CONFIG -----------------
# Replace this with the shared folder URL you want to download
FOLDER_URL = "https://drive.google.com/drive/u/0/folders/1GJQTzbTsGDtODLqoG3DEATDO8fDGgOgF"

# Output directory (next to the script)
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "DriveDownload")

# ----------------------------------------

def extract_folder_id(url):
    """
    Extract the folder ID from a Google Drive folder URL
    """
    # Folder URLs usually have form .../folders/<ID>
    m = re.search(r"/folders/([A-Za-z0-9_-]+)", url)
    return m.group(1) if m else None

def download_folder(folder_id):
    """
    Download using gdown
    """
    print(f"Downloading folder: {folder_id}")
    cmd = [
        sys.executable, "-m", "gdown",
        "--folder",
        f"https://drive.google.com/drive/folders/{folder_id}",
        "-O", OUTPUT_DIR
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print("Download completed successfully!")
    else:
        print("Download error:")
        print(result.stderr)

def main():
    folder_id = extract_folder_id(FOLDER_URL)

    if not folder_id:
        print("Could not extract folder ID from URL!")
        return

    # If the folder is already present, skip
    if os.path.exists(OUTPUT_DIR) and os.listdir(OUTPUT_DIR):
        print("Folder already exists — skipping download.")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    download_folder(folder_id)

if __name__ == "__main__":
    main()
