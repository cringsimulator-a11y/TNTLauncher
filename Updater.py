import os
import sys
import requests
import zipfile
from io import BytesIO

current_folder = os.path.dirname(os.path.abspath(__file__))
github_zip_url = "https://github.com/YourUsername/YourRepo/archive/refs/heads/main.zip"

print("Downloading latest launcher files...")
r = requests.get(github_zip_url, stream=True, timeout=60)
r.raise_for_status()
zip_bytes = BytesIO(r.content)

with zipfile.ZipFile(zip_bytes) as zf:
    # The first entry is usually the root folder, like 'Repo-main/'
    root_folder_in_zip = zf.namelist()[0].split('/')[0]

    for member in zf.namelist():
        if member.endswith('/'):
            continue  # skip directories

        # remove the root folder from the path
        rel_path = os.path.relpath(member, start=root_folder_in_zip)

        # skip updater itself and launcher_data.json
        if rel_path in ("launcher_data.json", os.path.basename(__file__)):
            continue

        target_path = os.path.join(current_folder, rel_path)
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        with open(target_path, "wb") as f:
            f.write(zf.read(member))

print("Update complete!")
