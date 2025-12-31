import os
import sys
import requests
import zipfile
import shutil
from io import BytesIO

current_folder = os.path.dirname(os.path.abspath(__file__))
temp_folder = os.path.join(current_folder, "TEMP")
os.makedirs(temp_folder, exist_ok=True)

github_zip_url = "https://github.com/YourUsername/YourRepo/archive/refs/heads/main.zip"

print("Downloading latest launcher files...")
r = requests.get(github_zip_url, stream=True, timeout=60)
r.raise_for_status()
zip_bytes = BytesIO(r.content)

with zipfile.ZipFile(zip_bytes) as zf:
    for member in zf.namelist():
        filename = os.path.join(temp_folder, os.path.relpath(member, start=zf.namelist()[0]))
        if member.endswith('/'):
            os.makedirs(filename, exist_ok=True)
        else:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, "wb") as f:
                f.write(zf.read(member))

# Delete old files except TEMP, launcher_data.json, updater itself
for item in os.listdir(current_folder):
    item_path = os.path.join(current_folder, item)
    if item in ("TEMP", "launcher_data.json", os.path.basename(__file__)):
        continue
    if os.path.isdir(item_path):
        shutil.rmtree(item_path)
    else:
        os.remove(item_path)

# Move files from TEMP to current folder
for item in os.listdir(temp_folder):
    shutil.move(os.path.join(temp_folder, item), current_folder)

# Delete TEMP
shutil.rmtree(temp_folder)

# Rename updater to TempFile.py
new_updater_name = os.path.join(current_folder, "TempFile.py")
os.rename(__file__, new_updater_name)

print("Update complete! Temporary updater renamed to TempFile.py")

# Self-delete (works if run as a script, not frozen executable)
if os.name == "nt":
    import subprocess
    subprocess.Popen(f'del "{new_updater_name}"', shell=True)
