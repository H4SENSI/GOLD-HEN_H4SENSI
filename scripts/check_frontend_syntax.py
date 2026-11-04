#!/usr/bin/env python3
"""Run a syntax-only Node.js check on the launcher, cache page and Service Worker."""

from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import sys

ROOT = Path(__file__).resolve().parents[1]


def inline_scripts(path: str) -> list[str]:
    html = (ROOT / path).read_text(encoding="utf-8")
    scripts = []
    pattern = re.compile(r"<script\b([^>]*)>(.*?)</script\s*>", re.I | re.S)
    for match in pattern.finditer(html):
        attributes, source = match.groups()
        if re.search(r"\btype\s*=\s*['\"]module['\"]", attributes, re.I):
            continue
        if source.strip():
            scripts.append(source)
    return scripts


def main() -> int:
    node = shutil.which("node")
    if not node:
        raise SystemExit("ERROR: Node.js is required for frontend syntax checks")

    sources = []
    for page in ("index.html", "cache.html"):
        sources.extend((f"{page} inline script #{i}", code)
                       for i, code in enumerate(inline_scripts(page), start=1))
    sources.append(("sw.js", (ROOT / "sw.js").read_text(encoding="utf-8")))

    errors = []
    for label, source in sources:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".js", encoding="utf-8", delete=False
        ) as temporary:
            temporary.write(source)
            temp_path = Path(temporary.name)
        try:
            result = subprocess.run(
                [node, "--check", str(temp_path)],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode:
                errors.append(f"{label}: {result.stderr.strip()}")
        finally:
            temp_path.unlink(missing_ok=True)

    if errors:
        print("\n".join("ERROR: " + item for item in errors))
        return 1

    print(f"OK: JavaScript syntax checked in {len(sources)} launcher/worker scripts.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
