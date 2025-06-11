#!/usr/bin/env python3

import yaml
import subprocess
import os
from pathlib import Path

CONFIG_FILE = "/etc/repomirror/repos.yaml"

def load_config(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def sync_repo(name, remote, local_path, extra_opts=None):
    full_local = Path(local_path)
    full_local.mkdir(parents=True, exist_ok=True)

    print(f"\n🌀 Syncing {name}")
    print(f"→ Remote: {remote}")
    print(f"→ Local: {full_local}")

    # Base rsync command
    cmd = ["rsync", "-av", "--delete"]

    # Append extra options if provided
    if extra_opts:
        if isinstance(extra_opts, str):
            cmd.extend(extra_opts.split())
        elif isinstance(extra_opts, list):
            cmd.extend(extra_opts)

    cmd.append(remote)
    cmd.append(f"{full_local}/")

    try:
        subprocess.run(cmd, check=True)
        print(f"✅ {name} synced successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Sync failed for {name}: {e}")

def main():
    config = load_config(CONFIG_FILE)
    base_path = config.get("base_path", "/srv/mirror")

    for repo in config.get("repos", []):
        name = repo["name"]
        remote = repo["remote"]
        local_rel = repo["local"]
        extra_opts = repo.get("rsync_opts", None)
        full_path = os.path.join(base_path, local_rel)

        sync_repo(name, remote, full_path, extra_opts)

if __name__ == "__main__":
    main()

