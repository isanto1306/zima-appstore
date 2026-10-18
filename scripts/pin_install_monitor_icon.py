#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Keep the original Install Monitor static icon linked in published store data.

The upstream ZimaOS store builder rewrites x-casaos.icon to its generated
assets/icon.png URL. Those bytes are already identical to the source icon;
the goal here is only to point published metadata and Compose back to the
unchanged original from Install-Monitor/static.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

APP_ID = "io.github.isanto1306.install-monitor"
ICON_URL = (
    "https://raw.githubusercontent.com/isanto1306/Install-Monitor/"
    "main/static/install-monitor-icon.png"
)
# Git blob SHA of the approved, unchanged original image in Install-Monitor.
APPROVED_ICON_BLOB_SHA = "99f47d03a7fc4f4c6dbaad7366b3b491afaaccda"


def check_original_icon(asset_path: Path) -> None:
    data = asset_path.read_bytes()
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise RuntimeError(f"{asset_path}: source icon is not a PNG")
    git_blob = hashlib.sha1(b"blob " + str(len(data)).encode("ascii") +
                            b"\x00" + data).hexdigest()
    if git_blob != APPROVED_ICON_BLOB_SHA:
        raise RuntimeError(
            f"{asset_path}: icon differs from original static/install-monitor-icon.png "
            f"(expected Git SHA {APPROVED_ICON_BLOB_SHA}, got {git_blob}); "
            "do not publish a processed or substitute image"
        )


def pin_compose_icon(compose_path: Path) -> None:
    text = compose_path.read_text(encoding="utf-8")
    if "\nx-casaos:\n" not in text:
        raise RuntimeError(f"{compose_path}: missing x-casaos metadata")
    before, metadata = text.rsplit("\nx-casaos:\n", 1)
    updated, count = re.subn(
        r"(?m)^  icon: [^\n]*$",
        "  icon: " + ICON_URL,
        metadata,
    )
    if count != 1:
        raise RuntimeError(f"{compose_path}: expected exactly one x-casaos icon; got {count}")
    result = before + "\nx-casaos:\n" + updated
    compose_path.write_text(result, encoding="utf-8")
    print(f"Pinned original icon in {compose_path}")


def main(dist: Path) -> None:
    app_dir = dist / "apps" / APP_ID
    check_original_icon(app_dir / "assets" / "icon.png")

    index_path = dist / "index.json"
    catalog = json.loads(index_path.read_text(encoding="utf-8"))
    apps = catalog.get("apps", [])
    matches = [app for app in apps if app.get("id") == APP_ID]
    if len(matches) != 1:
        raise RuntimeError(f"Expected Install Monitor once in index.json; got {len(matches)}")
    matches[0]["icon"] = ICON_URL
    index_path.write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print("Pinned original icon URL in store index.json")

    compose_files = sorted(app_dir.glob("docker-compose*.yml"))
    if not compose_files:
        raise RuntimeError("Missing published Install Monitor Compose files")
    for compose_path in compose_files:
        pin_compose_icon(compose_path)

    # Do not modify icon bytes, other apps or their metadata.
    print("Verified original PNG bytes are unchanged; no image conversion performed")


if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv) > 1 else "dist"))
