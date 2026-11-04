#!/usr/bin/env python3
"""Check PWA shell settings and safety interlocks for the PS4 launcher."""

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
index = (ROOT / "index.html").read_text(encoding="utf-8")
cache = (ROOT / "cache.html").read_text(encoding="utf-8")
worker = (ROOT / "sw.js").read_text(encoding="utf-8")
jb_page = (ROOT / "jb.html").read_text(encoding="utf-8")
readme = (ROOT / "README.md").read_text(encoding="utf-8")
notices = ROOT / "THIRD_PARTY_NOTICES.md"

errors = []

versions = re.findall(r'register\\(["\\']\\./sw\\.js\\?v=(\\d+)["\\']', index + cache)
worker_version = re.search(r'const CACHE_VERSION = "([0-9]+)"', worker)
if len(versions) != 2 or len(set(versions)) != 1:
    errors.append("index.html and cache.html must register the same Service Worker version")
elif not worker_version or versions[0] != worker_version.group(1):
    errors.append("Service Worker URL version and cache namespace must match")

if "asset-manifest.json" not in cache or "asset-manifest.json" not in worker:
    errors.append("the integrity manifest must be included in the offline shell and precache")
if "cache.manifest" in cache or re.search(r'<html[^>]+\\bmanifest=', jb_page, re.I):
    errors.append("obsolete Application Cache references must be removed")
if 'if(fw==="14.00")' not in index or "No se iniciará el payload desde este host." not in index:
    errors.append("firmware 14.00 must remain blocked by the internal launcher")
if "H4SENSI no incorpora esta cadena" not in index:
    errors.append("the 14.00 warning must identify external hosts as third-party services")
for host_url in ("feedchats.fr/web14/jb.html", "ps4.sentrix.ac/raw13/jb.html"):
    if host_url not in index:
        errors.append(f"missing expected external test-host notice: {host_url}")
if "https://ko-fi.com/s/e694c36022" not in index:
    errors.append("missing link to the SiSTRo beta publication")
if not notices.is_file() or "redistribución" not in notices.read_text(encoding="utf-8").lower():
    errors.append("THIRD_PARTY_NOTICES.md must document third-party provenance and redistribution checks")
if "asset-manifest.json" not in readme:
    errors.append("README.md must explain the integrity manifest")

if errors:
    print("\\n".join("ERROR: " + item for item in errors))
    sys.exit(1)

print("Correcto: versiones de caché, manifiesto de integridad y bloqueos de firmware están sincronizados.")
