import os
import sys
import requests
import zipfile
from io import BytesIO

# Determine base drive
base_drive = "D:" if os.path.exists("D:") else "C:"
install_folder = os.path.join(base_drive, "TNTLauncher")
os.makedirs(install_folder, exist_ok=True)

# URL of GitHub ZIP
github_zip_url = "https://github.com/cringsimulator-a11y/TNTLauncher/archive/refs/heads/main.zip"

print(f"Downloading launcher files to {install_folder}...")

# Download ZIP
r = requests.get(github_zip_url, stream=True, timeout=60)
r.raise_for_status()
zip_bytes = BytesIO(r.content)

# Extract ZIP
with zipfile.ZipFile(zip_bytes) as zf:
    for member in zf.namelist():
        filename = os.path.join(install_folder, os.path.relpath(member, start=zf.namelist()[0]))
        if member.endswith('/'):
            os.makedirs(filename, exist_ok=True)
        else:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, "wb") as f:
                f.write(zf.read(member))

print("Installation complete!")
