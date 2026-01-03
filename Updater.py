import os
import sys
import requests
import zipfile
import shutil
from io import BytesIO

# Current folder
current_folder = os.path.dirname(os.path.abspath(__file__))

# Rename updater to temp.py at the start
updater_name = os.path.join(current_folder, "temp.py")
if os.path.basename(__file__) != "temp.py":
    os.rename(__file__, updater_name)

# URL of GitHub repo ZIP
github_zip_url = "https://github.com/cringsimulator-a11y/TNTLauncher/archive/refs/heads/main.zip"

print("Starting update...")

# Delete old files except folders and launcher_data.json and temp.py itself
for item in os.listdir(current_folder):
    item_path = os.path.join(current_folder, item)
    if item in ("launcher_data.json", "temp.py"):
        continue
    if os.path.isdir(item_path):
        continue
    else:
        os.remove(item_path)

# Download ZIP
print("Downloading latest launcher files...")
r = requests.get(github_zip_url, stream=True, timeout=60)
r.raise_for_status()
zip_bytes = BytesIO(r.content)

# Extract files
with zipfile.ZipFile(zip_bytes) as zf:
    root_folder_in_zip = zf.namelist()[0].split('/')[0]  # usually Repo-main/
    for member in zf.namelist():
        if member.endswith('/'):
            continue  # skip directories
        rel_path = os.path.relpath(member, start=root_folder_in_zip)
        target_path = os.path.join(current_folder, rel_path)

        # Skip updater itself and launcher_data.json
        if rel_path in ("launcher_data.json", "temp.py"):
            continue

        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        with open(target_path, "wb") as f:
            f.write(zf.read(member))

print("Update complete!")

# Self-delete
try:
    os.remove(updater_name)
except Exception as e:
    print(f"Could not delete updater: {e}")
