#!/usr/bin/env python3
"""Comprueba enlaces internos y versiones de la caché del sitio."""
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
        errors.append(f"index.html apunta a un archivo inexistente: {target}")

versions = re.findall(r'register\(["\']\./sw\.js\?v=(\d+)["\']', index + cache)
if len(versions) < 2 or len(set(versions)) != 1:
    errors.append("index.html y cache.html deben registrar la misma versión del Service Worker")

if "h4sensi-offline-v12" not in worker:
    errors.append("no se actualizó la versión de la caché del Service Worker")

if 'if(fw==="14.00")' not in index or "H4SENSI no incorpora esta cadena" not in index:
    errors.append("el launcher debe advertir que los hosts 14.00 son externos y mantener bloqueado el inicio local")
for host_url in ("feedchats.fr/web14/jb.html", "ps4.sentrix.ac/raw13/jb.html"):
    if host_url not in index:
        errors.append(f"falta el enlace externo esperado: {host_url}")
if "https://ko-fi.com/s/e694c36022" not in index:
    errors.append("falta el enlace a la publicación de SiSTRo para GoldHEN v2.4b18.13")

if errors:
    print("\n".join("ERROR: " + item for item in errors))
    sys.exit(1)

print("Correcto: los enlaces locales existen y las versiones de caché coinciden.")
