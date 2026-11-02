#!/usr/bin/env python3
"""Basic static checks for local links and PWA version consistency."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
index = (ROOT / "index.html").read_text(encoding="utf-8")
cache = (ROOT / "cache.html").read_text(encoding="utf-8")
worker = (ROOT / "sw.js").read_text(encoding="utf-8")

errors = []
for target in re.findall(r'href=["\']\./([^"\']+)["\']', index):
    if target.startswith(("http:", "https:", "#")):
        continue
    if not (ROOT / target).is_file():
        errors.append(f"index.html links to missing file: {target}")

versions = re.findall(r'register\(["\']\./sw\.js\?v=(\d+)["\']', index + cache)
if len(versions) < 2 or len(set(versions)) != 1:
    errors.append("index.html and cache.html must register the same versioned service worker")

if "h4sensi-offline-v9" not in worker:
    errors.append("service worker cache version was not bumped")

if errors:
    print("\n".join("ERROR: " + item for item in errors))
    sys.exit(1)

print("OK: local links exist and PWA versions are consistent.")
