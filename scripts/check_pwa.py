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

if "h4sensi-offline-v11" not in worker:
    errors.append("no se actualizó la versión de la caché del Service Worker")

if 'if(fw==="14.00")' not in index or "GoldHEN v2.4b18.13 añade soporte" not in index:
    errors.append("el launcher debe avisar sobre la beta y bloquear la ruta 14.00")
if "https://ko-fi.com/s/e694c36022" not in index:
    errors.append("falta el enlace a la publicación de SiSTRo para GoldHEN v2.4b18.13")

if errors:
    print("\n".join("ERROR: " + item for item in errors))
    sys.exit(1)

print("Correcto: los enlaces locales existen y las versiones de caché coinciden.")
