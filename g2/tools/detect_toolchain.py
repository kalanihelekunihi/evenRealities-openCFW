#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Print the reviewed toolchain-profile id that matches the given compiler.

openCFW pins compiled overlays byte-for-byte, so a build must declare which
reviewed toolchain produced (or will verify) those bytes.  This detector maps
a concrete compiler to its reviewed profile id using one overlay config as the
profile registry:

- the canonical ``apple-clang`` profile is the config's top-level
  ``toolchain.reviewed_version_prefix``; and
- every alternate reproducible profile is a
  ``toolchain_profiles[<id>].reviewed_version_prefix``.

The first profile whose reviewed prefix is a prefix of the compiler's
``--version`` first line wins.  If no reviewed profile matches, the detector
exits nonzero with a diagnostic so callers fail closed rather than silently
guessing a profile whose pins the compiler cannot reproduce.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REGISTRY = ROOT / "components/apollo_main/ring_gesture/overlay.json"
DEFAULT_PROFILE = "apple-clang"


def compiler_version(clang: str) -> str:
    try:
        completed = subprocess.run(
            [clang, "--version"],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as error:
        raise SystemExit(f"detect_toolchain: cannot run {clang}: {error}")
    if completed.returncode or not completed.stdout.strip():
        raise SystemExit(
            f"detect_toolchain: {clang} returned no version"
        )
    return completed.stdout.splitlines()[0].strip()


def registry_profiles(registry: Path) -> list[tuple[str, str]]:
    config = json.loads(registry.read_text(encoding="utf-8"))
    candidates: list[tuple[str, str]] = []
    canonical = config.get("toolchain", {}).get("reviewed_version_prefix")
    if canonical:
        candidates.append((DEFAULT_PROFILE, canonical))
    profiles = config.get("toolchain_profiles") or {}
    for profile_id, profile in profiles.items():
        prefix = profile.get("reviewed_version_prefix")
        if prefix:
            candidates.append((profile_id, prefix))
    return candidates


def detect(clang: str, registry: Path) -> str:
    version = compiler_version(clang)
    for profile_id, prefix in registry_profiles(registry):
        if version.startswith(prefix):
            return profile_id
    raise SystemExit(
        f"detect_toolchain: no reviewed profile matches {version!r}; for the "
        "Apollo core, produce two independent `make "
        "core-canonical-observation` runs per reviewed Apple/Linux profile "
        "and verify them with `make core-canonical-admission` (do not use "
        "direct --record-profile); component-specific recorders such as the "
        "ring-source --record-profile workflow remain separate"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--clang", required=True)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    args = parser.parse_args(argv)
    print(detect(args.clang, args.registry))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
