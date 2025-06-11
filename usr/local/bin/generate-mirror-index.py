#!/usr/bin/env python3

import yaml
import os
import time
from pathlib import Path
from datetime import datetime

CONFIG_FILE = "/etc/repomirror/repos.yaml"
OUTPUT_FILE = "/home/reflection/index.html"
TIME_THRESHOLD = 24 * 60 * 60  # 24h in seconds
BASE_URL = "https://reflection.grit.ucsb.edu"  # Replace with your mirror root URL

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return yaml.safe_load(f)

def latest_mtime(path: Path):
    try:
        files = list(path.rglob("*"))
        if not files:
            return None
        return max(f.stat().st_mtime for f in files if f.is_file())
    except Exception:
        return None

def classify_repo_status(mtime):
    if mtime is None:
        return "failed", "❌", "Not found"
    age = time.time() - mtime
    dt_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
    if age <= TIME_THRESHOLD:
        return "success", "✅", dt_str
    else:
        return "pending", "⚠️", dt_str

def generate_html(config):
    base_path = Path(config["base_path"])
    entries = []

    for repo in config.get("repos", []):
        name = repo["name"]
        rel_path = repo["local"]
        full_path = base_path / rel_path

        if full_path.exists():
            mtime = latest_mtime(full_path)
        else:
            mtime = None

        status, icon, timestamp = classify_repo_status(mtime)
        entries.append((status, icon, name, timestamp, rel_path))

    entries.sort()  # optional: sort alphabetically

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>UCSB Linux Mirrors</title>
<style>
html {{ font-family: Arial, sans-serif; background-color: #f7f7f7; }}
body {{ margin: 2em auto; max-width: 1400px; padding: 0 1em; color: #222; }}
h1 {{ text-align: center; }}
.banner {{ border: 2px solid #0057b7; border-radius: 8px; background-color: #dce6f8; padding: 1em; }}
.banner p {{ text-align: center; font-size: 85%; }}
.statusContainer {{ background-color: #e5e5e5; border: 1px solid #0057b7; border-radius: 5px; padding: 10px; margin-top: 1em; display: flex; flex-wrap: wrap; gap: 8px; }}
.repoStatus {{ padding: 8px 12px; border-radius: 4px; font-size: 90%; border: 1px solid #333; white-space: nowrap; }}
.success {{ background-color: #d0f0ef; border-color: #2a9d8f; }}
.pending {{ background-color: #fff3cd; border-color: #f4a261; }}
.failed  {{ background-color: #f8d7da; border-color: #c0392b; }}
.legend {{ font-size: 90%; margin-top: 1em; padding: 0.5em; background: #fff; border-left: 4px solid #0057b7; }}
.repoList {{ margin-top: 2em; }}
.repoList a {{ display: block; margin: 0.4em 0; color: #0057b7; text-decoration: none; }}
.repoList a:hover {{ text-decoration: underline; }}
</style>
</head>
<body>
<div class="banner">
  <h1>UCSB Repo Mirrors</h1>
  <p>Hosted by: <a href="https://grit.ucsb.edu" target="_blank" rel="noopener">General Research IT (GRIT)</a></p>

  <div class="legend">
    <strong>Status Key:</strong>
    <div class="repoStatus success">✅ <strong>Success:</strong> Updated < 24h</div>
    <div class="repoStatus pending">⚠️ <strong>Pending:</strong> No updates in 24h</div>
    <div class="repoStatus failed">❌ <strong>Failed:</strong> Missing or empty</div>
  </div>

  <div class="statusContainer">
    <strong>Status from latest Repo Sync:</strong><br />
"""
    for status, icon, name, timestamp, rel in entries:
        html += f'<div class="repoStatus {status}">{icon} <strong>{name}:</strong> Last modified: {timestamp}</div>\n'

    html += """</div><div class="repoList">
<h2>Browse Repositories</h2>
"""

    for _, _, name, _, rel in entries:
        html += f'<a href="{BASE_URL}/{rel}/">{name}</a>\n'

    html += "</div></body></html>\n"
    return html

def main():
    config = load_config()
    html = generate_html(config)
    with open(OUTPUT_FILE, "w") as f:
        f.write(html)
    print(f"✅ Web index written to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()

