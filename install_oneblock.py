import os
import json
import requests

mods_dir = os.path.join(os.getenv("APPDATA"), ".minecraft", "mods")
if not os.path.exists(mods_dir):
    os.makedirs(mods_dir)

data_file = os.path.join(os.path.dirname(__file__), "launcher_data.json")

def load_data():
    if os.path.exists(data_file):
        return json.load(open(data_file, "r", encoding="utf-8"))
    return {}

data = load_data()
mc_version = data.get("FabricAPI_Version")
if not mc_version:
    raise SystemExit("FabricAPI_Version not set in launcher_data.json")

project_id = "oneblock-data-pack"
api_url = f"https://api.modrinth.com/v2/project/{project_id}/version"

resp = requests.get(api_url, timeout=20)
resp.raise_for_status()
versions = resp.json()

selected = None
for v in versions:
    if mc_version in v.get("game_versions", []) and "fabric" in v.get("loaders", []):
        selected = v
        break

if not selected:
    raise SystemExit(f"No OneBlock version found for Minecraft {mc_version} with Fabric")

file_info = None
for f in selected["files"]:
    if f.get("primary", False):
        file_info = f
        break
if not file_info:
    file_info = selected["files"][0]

download_url = file_info["url"]
filename = file_info["filename"]
out_path = os.path.join(mods_dir, filename)

if os.path.exists(out_path):
    print(f"{filename} already exists, skipping download")
else:
    print(f"Downloading {filename} for Minecraft {mc_version} (Fabric)...")
    r = requests.get(download_url, stream=True, timeout=30)
    r.raise_for_status()
    with open(out_path, "wb") as f:
        for chunk in r.iter_content(8192):
            if chunk:
                f.write(chunk)
    print(f"Downloaded to {out_path}")
