#!/usr/bin/env python3
"""Keep the ZimaOS store aligned with a *published* Install Monitor beta.

Do not trust the version in the upstream source alone: the matching GHCR tag
must exist.  Runs before the store builder, only on the public repository.
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
APP = ROOT / "Apps" / "InstallMonitor" / "docker-compose.yml"
SOURCE = "https://raw.githubusercontent.com/isanto1306/Install-Monitor/main/main.py"
BASE = "ghcr.io/isanto1306/install-monitor"
VER = r"(?:[0-9]+\.){2}[0-9]+-beta\.[0-9]+"
IMAGE_LINE = re.compile(r"(?m)^(    image: " + re.escape(BASE) + r":)(" + VER + r")(\s*)$")
VERSION_LINE = re.compile(r'(?m)^(  version: ")(' + VER + r')(")[ \t]*$')
HEADER_LINE = re.compile(r"(?m)^(# Install Monitor v)(" + VER + r")(.*)$")
BACKEND_LINE = re.compile(r'(?m)^VERSION = "(' + VER + r')"$')


def parts(version: str) -> tuple[int, int, int, int]:
    return tuple(int(n) for n in re.findall(r"\d+", version))


def sync(
    compose_path: pathlib.Path = APP,
    fetch=None,
    image_exists=None,
) -> bool:
    """Return True if the store manifest was updated; never downgrade."""
    if fetch is None:
        def fetch() -> str:
            req = urllib.request.Request(SOURCE, headers={"User-Agent": "InstallMonitorStoreSync/1.0"})
            with urllib.request.urlopen(req, timeout=20) as response:
                raw = response.read(600000)
            return raw.decode("utf-8")
    if image_exists is None:
        def image_exists(tag: str) -> bool:
            result = subprocess.run(
                ["docker", "buildx", "imagetools", "inspect", f"{BASE}:{tag}"],
                check=False, capture_output=True, text=True, timeout=90,
            )
            return result.returncode == 0
    content = compose_path.read_text(encoding="utf-8")
    old_image = IMAGE_LINE.search(content)
    old_version = VERSION_LINE.search(content)
    old_header = HEADER_LINE.search(content)
    if not old_image or not old_version or not old_header:
        raise RuntimeError("Store-Compose-Version oder Image-Referenz nicht eindeutig erkannt.")
    installed = old_version.group(2)
    if old_image.group(2) != installed or old_header.group(2) != installed:
        raise RuntimeError("Store-Version, Image-Tag und Kommentar sind nicht identisch.")

    latest_match = BACKEND_LINE.search(fetch())
    if not latest_match:
        raise RuntimeError("Die Quellversion von Install Monitor ist nicht ermittelbar.")
    latest = latest_match.group(1)
    if parts(latest) <= parts(installed):
        print(f"Install Monitor Store bereits aktuell: {installed}")
        return False
    if not image_exists(latest):
        print(f"GHCR-Image {BASE}:{latest} noch nicht veröffentlicht; Store bleibt auf {installed}.")
        return False
    content = IMAGE_LINE.sub(lambda m: m.group(1) + latest + m.group(3), content)
    content = VERSION_LINE.sub(lambda m: m.group(1) + latest + m.group(3), content)
    content = HEADER_LINE.sub(lambda m: m.group(1) + latest + m.group(3), content)
    compose_path.write_text(content, encoding="utf-8")
    print(f"Store auf {latest} aktualisiert, Image in GHCR bestätigt.")
    return True


if __name__ == "__main__":
    try:
        sync()
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
        print(f"Version-Sync fehlgeschlagen; vorhandener Store bleibt erhalten: {exc}", file=sys.stderr)
        sys.exit(1)
)
HEADER_LINE = re.compile(r"(?m)^(# Install Monitor v)(" + VER + r")(.*)$")
BACKEND_LINE = re.compile(r'(?m)^VERSION = "(' + VER + r')"$')


def parts(version: str) -> tuple[int, int, int, int]:
    return tuple(int(n) for n in re.findall(r"\d+", version))


def sync(
    compose_path: pathlib.Path = APP,
    fetch=None,
    image_exists=None,
) -> bool:
    """Return True if the store manifest was updated; never downgrade."""
    if fetch is None:
        def fetch() -> str:
            req = urllib.request.Request(SOURCE, headers={"User-Agent": "InstallMonitorStoreSync/1.0"})
            with urllib.request.urlopen(req, timeout=20) as response:
                raw = response.read(600000)
            return raw.decode("utf-8")
    if image_exists is None:
        def image_exists(tag: str) -> bool:
            result = subprocess.run(
                ["docker", "buildx", "imagetools", "inspect", f"{BASE}:{tag}"],
                check=False, capture_output=True, text=True, timeout=90,
            )
            return result.returncode == 0
    content = compose_path.read_text(encoding="utf-8")
    old_image = IMAGE_LINE.search(content)
    old_version = VERSION_LINE.search(content)
    old_header = HEADER_LINE.search(content)
    if not old_image or not old_version or not old_header:
        raise RuntimeError("Store-Compose-Version oder Image-Referenz nicht eindeutig erkannt.")
    installed = old_version.group(2)
    if old_image.group(2) != installed or old_header.group(2) != installed:
        raise RuntimeError("Store-Version, Image-Tag und Kommentar sind nicht identisch.")

    latest_match = BACKEND_LINE.search(fetch())
    if not latest_match:
        raise RuntimeError("Die Quellversion von Install Monitor ist nicht ermittelbar.")
    latest = latest_match.group(1)
    if parts(latest) <= parts(installed):
        print(f"Install Monitor Store bereits aktuell: {installed}")
        return False
    if not image_exists(latest):
        print(f"GHCR-Image {BASE}:{latest} noch nicht veröffentlicht; Store bleibt auf {installed}.")
        return False
    content = IMAGE_LINE.sub(lambda m: m.group(1) + latest + m.group(3), content)
    content = VERSION_LINE.sub(lambda m: m.group(1) + latest + m.group(3), content)
    content = HEADER_LINE.sub(lambda m: m.group(1) + latest + m.group(3), content)
    compose_path.write_text(content, encoding="utf-8")
    print(f"Store auf {latest} aktualisiert, Image in GHCR bestätigt.")
    return True


if __name__ == "__main__":
    try:
        sync()
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
        print(f"Version-Sync fehlgeschlagen; vorhandener Store bleibt erhalten: {exc}", file=sys.stderr)
        sys.exit(1)
