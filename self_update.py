import os
import shutil
import zipfile
import requests
import sys

base_dir = os.path.dirname(os.path.abspath(__file__))
script_path = os.path.abspath(__file__)
script_name = os.path.basename(script_path)

TEMP_DIR = os.path.join(base_dir, "TEMP")
ZIP_PATH = os.path.join(TEMP_DIR, "repo.zip")

GITHUB_ZIP_URL = "https://github.com/cringsimulator-a11y/TNTLauncher/archive/refs/heads/main.zip"

os.makedirs(TEMP_DIR, exist_ok=True)

r = requests.get(GITHUB_ZIP_URL, stream=True, timeout=30)
r.raise_for_status()

with open(ZIP_PATH, "wb") as f:
    for chunk in r.iter_content(8192):
        if chunk:
            f.write(chunk)

with zipfile.ZipFile(ZIP_PATH, "r") as z:
    z.extractall(TEMP_DIR)

os.remove(ZIP_PATH)

unzipped_root = None
for item in os.listdir(TEMP_DIR):
    p = os.path.join(TEMP_DIR, item)
    if os.path.isdir(p):
        unzipped_root = p
        break

if not unzipped_root:
    raise SystemExit("Unzip failed")

launcher_data = os.path.join(unzipped_root, "launcher_data.json")
if os.path.exists(launcher_data):
    os.remove(launcher_data)

KEEP = {
    "Cache",
    "logs",
    "launcher_data.json",
    script_name
}

for item in os.listdir(base_dir):
    if item in KEEP:
        continue
    p = os.path.join(base_dir, item)
    if os.path.isdir(p):
        shutil.rmtree(p, ignore_errors=True)
    else:
        try:
            os.remove(p)
        except:
            pass

temp_self = os.path.join(base_dir, "TEMPFILE")
os.rename(script_path, temp_self)

for item in os.listdir(unzipped_root):
    src = os.path.join(unzipped_root, item)
    dst = os.path.join(base_dir, item)
    if os.path.exists(dst):
        if os.path.isdir(dst):
            shutil.rmtree(dst, ignore_errors=True)
        else:
            os.remove(dst)
    shutil.move(src, dst)

shutil.rmtree(TEMP_DIR, ignore_errors=True)

os.remove(temp_self)
