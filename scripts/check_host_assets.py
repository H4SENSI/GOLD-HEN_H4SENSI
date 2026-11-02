#!/usr/bin/env python3
"""Check that active firmware routes and offline-cache entries point to real files."""

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
    match = re.search(rf"var {re.escape(variable)}\s*=\s*(\{{.*?\}});", source, re.S)
    if not match:
        raise SystemExit(f"ERROR: could not parse {variable} in index.html")
    return set(re.findall(r'"([^"]+)"\s*:\s*1', match.group(1)))


def array_values(source: str, variable: str) -> list[str]:
    match = re.search(rf"var {re.escape(variable)}\s*=\s*(\[.*?\]);", source, re.S)
    if not match:
        raise SystemExit(f"ERROR: could not parse {variable} in index.html")
    return quoted_paths(match.group(1))


def require_files(paths: list[str], label: str) -> None:
    missing = []
    for raw_path in paths:
        normalized = raw_path.removeprefix("./")
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


def main() -> int:
    index = read_text("index.html")
    cache_html = read_text("cache.html")
    service_worker = read_text("sw.js")

    # Only validate routes explicitly enabled by ROUTE_READY. Disabled engines
    # may intentionally retain incomplete upstream scaffolding.
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

    slop_match = re.search(r'return \["jb\\.js",\[(.*?)\],1\];', index, re.S)
    # Be tolerant of the literal-dot spelling used in the JavaScript source.
    if not slop_match:
        slop_match = re.search(r'return \["jb\.js",\[(.*?)\],1\];', index, re.S)
    if not slop_match:
        raise SystemExit("ERROR: could not parse SLOPKIT asset list in index.html")
    slop_assets = quoted_paths(slop_match.group(1))

    active_assets: list[str] = []
    for firmware in sorted(enabled):
        if firmware in families["F700"]:
            active_assets.extend(engines["F700"])
        elif firmware in families["F900"]:
            active_assets.extend(engines["F900"])
        elif firmware in families["FCSS"]:
            active_assets.extend(engines["FCSS"])
        elif firmware in families["FSLOP"]:
            active_assets.extend(slop_assets)
            patch = "patches/1302.bin" if firmware in {"13.02", "13.04"} else f"patches/{firmware.replace('.', '')}.bin"
            active_assets.append(patch)
        else:
            raise SystemExit(f"ERROR: ROUTE_READY enables {firmware}, but no engine family handles it")

    cache_match = re.search(r'urls:\[(.*?)\]\}\);', cache_html, re.S)
    if not cache_match:
        raise SystemExit("ERROR: could not parse offline precache URL list in cache.html")
    cache_assets = [path.removeprefix("./") for path in quoted_paths(cache_match.group(1))]

    shell_match = re.search(r"const SHELL\s*=\s*\[(.*?)\];", service_worker, re.S)
    if not shell_match:
        raise SystemExit("ERROR: could not parse service-worker shell list")
    shell_assets = [path.removeprefix("./") for path in quoted_paths(shell_match.group(1))]
    shell_assets = [path for path in shell_assets if path]

    # The index links should not point to deleted local HTML pages.
    local_html_links = re.findall(r'href=["\']\./([^"\']+\.html)["\']', index)
    require_files(active_assets, "active firmware routes")
    require_files(cache_assets, "offline precache")
    require_files(shell_assets, "service-worker shell")
    require_files(local_html_links, "local page links")

    print(f"OK: {len(enabled)} enabled firmware routes reference existing files.")
    print(f"OK: {len(set(cache_assets))} offline-cache entries exist.")
    print(f"OK: {len(shell_assets)} service-worker shell entries exist.")
    print("OK: no broken local HTML links found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
