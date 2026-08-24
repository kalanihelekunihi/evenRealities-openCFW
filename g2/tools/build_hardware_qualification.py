#!/usr/bin/env python3
"""Build the non-flashing G2 stock-control and minimal-hook test rungs."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


G2_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = G2_ROOT.parent
BUILD = G2_ROOT / "build" / "hardware-validation"


def run(*args: str) -> None:
    subprocess.run(args, cwd=REPO_ROOT, check=True)


def main() -> int:
    rungs = (
        (
            "minimal-advertised-name-hook",
            "advertised-name-overlay.json",
            "g2-2.2.6.10-minimal-name-hook.json",
            "g2-openCFW-s200_v2.2.6.10-minimal-name-hook.evenota.bin",
            "g2-openCFW-s200_v2.2.6.0-minimal-name-hook",
        ),
        (
            "name-memcpy-hook",
            "name-memcpy-overlay.json",
            "g2-2.2.6.10-name-memcpy-hook.json",
            "g2-openCFW-s200_v2.2.6.10-name-memcpy-hook.evenota.bin",
            "g2-openCFW-s200_v2.2.6.0-name-memcpy-hook",
        ),
    )
    for directory, config, manifest, package_name, release_stem in rungs:
        component_dir = BUILD / directory
        package_dir = BUILD / f"{directory}-package"
        package = package_dir / "package" / package_name
        release = BUILD / f"{release_stem}.evenota.bin"
        release_report = BUILD / f"{release_stem}.json"
        run(
            sys.executable,
            str(G2_ROOT / "tools" / "apollo_overlay.py"),
            "--config",
            str(G2_ROOT / "hardware" / "qualification" / config),
            "--output-dir",
            str(component_dir),
        )
        run(
            sys.executable,
            str(G2_ROOT / "tools" / "open_cfw.py"),
            "build",
            "--manifest",
            str(G2_ROOT / "manifests" / manifest),
            "--output-dir",
            str(package_dir),
        )
        run(
            sys.executable,
            str(G2_ROOT / "tools" / "release_cfw.py"),
            str(package),
            str(release),
            "--report",
            str(release_report),
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
