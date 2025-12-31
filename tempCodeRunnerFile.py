    def download_thread(self, project_id):
        try:
            os.makedirs(MODS_DIR, exist_ok=True)

            r = requests.get(VERSION_URL.format(project_id), timeout=20)
            r.raise_for_status()
            versions = r.json()

            for v in versions:
                if "fabric" not in v.get("loaders", []):
                    continue

                if MC_VERSION not in v.get("game_versions", []):
                    continue

                file = None
                for f in v.get("files", []):
                    if f.get("primary"):
                        file = f
                        break
                if not file:
                    for f in v.get("files", []):
                        if f["filename"].endswith(".jar"):
                            file = f
                            break

                if not file:
                    continue

                path = os.path.join(MODS_DIR, file["filename"])

                with requests.get(file["url"], stream=True, timeout=60) as d:
                    d.raise_for_status()
                    with open(path, "wb") as out:
                        for chunk in d.iter_content(8192):
                            if chunk:
                                out.write(chunk)

                self.root.after(0, lambda: self.status.config(
                    text=f"Downloaded: {file['filename']}"
                ))
                return

            self.root.after(0, lambda: self.status.config(
                text=f"No Fabric mod found for Minecraft {MC_VERSION}"
            ))

        except Exception as e:
            self.root.after(0, lambda: self.status.config(
                text=f"Download error: {e}"
            ))
