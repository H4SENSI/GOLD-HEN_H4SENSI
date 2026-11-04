#!/usr/bin/env python3
"""Validate enabled firmware routes, offline assets and pinned Git blob metadata."""

from hashlib import sha1
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]


def read_text(path: str) -> str:
    file_path = ROOT / path
    if not file_path.is_file():
        raise SystemExit(f"ERROR: required project file not found: {path}")
    return file_path.read_text(encoding="utf-8")


def quoted_paths(source: str) -> list[str]:
    return re.findall(r'"([^"]+)"', source)


def object_values(source: str, variable: str) -> set[str]:
    match = re.search(
        rf"var {re.escape(variable)}\s*=\s*\{{(.*?)\}};",
        source,
        re.S,
    )
    if not match:
        raise SystemExit(f"ERROR: could not parse {variable} in index.html")
    return set(re.findall(r'"([^"]+)"\s*:\s*1', match.group(1)))


def array_values(source: str, variable: str) -> list[str]:
    match = re.search(
        rf"var {re.escape(variable)}\s*=\s*\[.*?,\[(.*?)\],\s*[01]\];",
        source,
        re.S,
    )
    if not match:
        raise SystemExit(f"ERROR: could not parse {variable} in index.html")
    return quoted_paths(match.group(1))


def require_files(paths: list[str], label: str) -> None:
    missing = []
    for raw_path in paths:
        normalized = raw_path.split("?", 1)[0].removeprefix("./")
        candidate = (ROOT / normalized).resolve()
        if candidate != ROOT and ROOT not in candidate.parents:
            missing.append(f"{raw_path} (path escapes repository)")
        elif not candidate.is_file():
            missing.append(raw_path)
    if missing:
        print(f"ERROR: {label} contains missing assets:")
        for item in sorted(set(missing)):
            print(f"  - {item}")
        raise SystemExit(1)


def git_blob_sha1(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return sha1(header + data).hexdigest()


def main() -> int:
    index = read_text("index.html")
    cache_html = read_text("cache.html")
    service_worker = read_text("sw.js")
    jailbreak_page = read_text("jb.html")

    # Only firmware versions explicitly enabled in ROUTE_READY are validated.
    enabled = object_values(index, "ROUTE_READY")
    families = {
        "F700": object_values(index, "F700"),
        "F900": object_values(index, "F900"),
        "FCSS": object_values(index, "FCSS"),
        "FSLOP": object_values(index, "FSLOP"),
    }
    engines = {
        "F700": array_values(index, "A700"),
        "F900": array_values(index, "A900"),
        "FCSS": array_values(index, "ACSS"),
    }

    slop_match = re.search(
        r'return \["jb\.js",\[(.*?)\],1\];',
        index,
        re.S,
    )
    if not slop_match:
        slop_match = re.search(
            r'return \["jb\.js",\[(.*?)\],1\];',
            index,
            re.S,
        )
    if not slop_match:
        raise SystemExit("ERROR: could not parse SLOPKIT asset list in index.html")
    slop_assets = quoted_paths(slop_match.group(1))

    active_assets: set[str] = set()
    for firmware in sorted(enabled):
        if firmware in families["F700"]:
            active_assets.update(engines["F700"])
        elif firmware in families["F900"]:
            active_assets.update(engines["F900"])
        elif firmware in families["FCSS"]:
            active_assets.update(engines["FCSS"])
        elif firmware in families["FSLOP"]:
            active_assets.update(slop_assets)
            patch = (
                "patches/1302.bin"
                if firmware in {"13.02", "13.04"}
                else f"patches/{firmware.replace('.', '')}.bin"
            )
            active_assets.add(patch)
        else:
            raise SystemExit(
                f"ERROR: ROUTE_READY enables {firmware}, but no engine family handles it"
            )

    manifest_path = ROOT / "asset-manifest.json"
    if not manifest_path.is_file():
        raise SystemExit("ERROR: asset-manifest.json is missing")
    manifest_bytes = manifest_path.read_bytes()
    try:
        manifest = json.loads(manifest_bytes)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"ERROR: asset-manifest.json is invalid JSON: {exc}") from exc

    if manifest.get("schema_version") != 1 or manifest.get("hash_format") != "git-blob-sha1":
        raise SystemExit("ERROR: unsupported asset-manifest schema or hash format")
    manifest_files = manifest.get("files")
    if not isinstance(manifest_files, dict) or not manifest_files:
        raise SystemExit("ERROR: asset-manifest.json has no file entries")

    actual_manifest_sha = git_blob_sha1(manifest_bytes)
    pinned_sha = re.search(r'ASSET_MANIFEST_SHA1="([a-f0-9]{40})"', index)
    pinned_size = re.search(r"ASSET_MANIFEST_SIZE=(\d+)", index)
    if not pinned_sha or pinned_sha.group(1) != actual_manifest_sha:
        raise SystemExit("ERROR: index.html does not pin the current asset-manifest Git blob SHA-1")
    if not pinned_size or int(pinned_size.group(1)) != len(manifest_bytes):
        raise SystemExit("ERROR: index.html does not pin the current asset-manifest byte size")

    for path, expected in manifest_files.items():
        if not isinstance(path, str) or not isinstance(expected, dict):
            raise SystemExit(f"ERROR: malformed asset manifest entry: {path!r}")
        file_path = ROOT / path
        if not file_path.is_file():
            raise SystemExit(f"ERROR: manifest references missing asset: {path}")
        data = file_path.read_bytes()
        if expected.get("size") != len(data):
            raise SystemExit(f"ERROR: byte-size mismatch for {path}")
        if expected.get("git_blob_sha1") != git_blob_sha1(data):
            raise SystemExit(f"ERROR: Git blob SHA-1 mismatch for {path}")

    missing_manifest_entries = sorted(active_assets - set(manifest_files))
    if missing_manifest_entries:
        raise SystemExit(
            "ERROR: enabled routes are missing integrity entries: "
            + ", ".join(missing_manifest_entries)
        )

    cache_match = re.search(r"urls\s*:\[(.*?)\]\s*\}\s*\);", cache_html, re.S)
    if not cache_match:
        raise SystemExit("ERROR: could not parse offline precache URL list in cache.html")
    cache_assets = [path.removeprefix("./") for path in quoted_paths(cache_match.group(1))]
    if len(cache_assets) != len(set(cache_assets)):
        raise SystemExit("ERROR: offline precache list contains duplicate paths")
    if "asset-manifest.json" not in cache_assets:
        raise SystemExit("ERROR: asset-manifest.json must be available offline")
    if "cache.manifest" in cache_assets:
        raise SystemExit("ERROR: obsolete AppCache manifest must not be precached")

    shell_match = re.search(r"const SHELL\s*=\s*\[(.*?)\];", service_worker, re.S)
    if not shell_match:
        raise SystemExit("ERROR: could not parse service-worker shell list")
    shell_assets = [path.removeprefix("./") for path in quoted_paths(shell_match.group(1))]

    require_files(sorted(active_assets), "active firmware routes")
    require_files(cache_assets, "offline precache")
    require_files(shell_assets, "service-worker shell")

    local_refs = re.findall(r'(?:href|src)=[\"\'](\./[^\"\']+)[\"\']', index + cache_html + jailbreak_page)
    require_files(local_refs, "local HTML links and scripts")

    registrations = re.findall(r'register\([\"\']\./sw\.js\?v=(\d+)', index + cache_html)
    worker_version = re.search(r'const CACHE_VERSION = "([0-9]+)"', service_worker)
    if len(registrations) != 2 or len(set(registrations)) != 1:
        raise SystemExit("ERROR: index.html and cache.html must use the same Service Worker URL version")
    if not worker_version or registrations[0] != worker_version.group(1):
        raise SystemExit("ERROR: Service Worker URL and cache namespace versions are out of sync")
    if re.search(r'<html[^>]+\bmanifest=', jailbreak_page, re.I):
        raise SystemExit("ERROR: deprecated Application Cache attribute remains in jb.html")

    print(f"OK: {len(enabled)} enabled firmware routes reference existing files.")
    print(f"OK: {len(active_assets)} active route assets have pinned size and Git blob SHA-1.")
    print(f"OK: {len(cache_assets)} offline-cache entries exist.")
    print(f"OK: {len(shell_assets)} service-worker shell entries exist.")
    print("OK: Service Worker versions and manifest pin match.")
    print("OK: no broken local HTML links or obsolete AppCache references.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
