#!/usr/bin/env python3
"""Repin manifests/g2-2.2.6.10-source-only.json against on-disk source builds.

The source-only manifest (extends g2-2.2.6.10-core-source.json) selects a
``source_build`` provider for every one of the six EVENOTA components.  Three
of those providers (Apollo bootloader, Apollo main, EM9305) are inherited
unmodified from the core-source manifest; this tool owns the other three
(codec, touch, case), whose source builds live outside the core-source
closure, plus the package-level size/SHA-256 pins that only exist once every
provider byte is known.

This is a two-pass repin, not a build: it reads whatever is already on disk
under ``build/gx8002-source-candidate/``, ``build/touch-source-image/`` and
``build/case-source-image/`` (built by ``make gx8002-source-candidate
touch-source-image case-source-image``, transitively via
``make codec-source-experimental``) and rewrites only the fields this tool
owns in the manifest.  It does not invoke a compiler and performs no
hardware operation.
"""

# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "manifests/g2-2.2.6.10-source-only.json"

sys.path.insert(0, str(Path(__file__).resolve().parent))
import open_cfw as oc  # noqa: E402


class RepinError(RuntimeError):
    pass


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _provider_from_disk(relative_path: str) -> tuple[int, str]:
    path = ROOT / relative_path
    if not path.is_file():
        raise RepinError(
            f"source build output is missing: {relative_path} "
            "(run its `make` target first)"
        )
    data = path.read_bytes()
    return len(data), hashlib.sha256(data).hexdigest()


def compute_component_overrides() -> dict[str, dict]:
    manifest = json.loads(MANIFEST_PATH.read_text())
    overrides = manifest["component_overrides"]

    codec_size, codec_sha = _provider_from_disk(
        "build/gx8002-source-candidate/firmware_codec.hybrid-candidate.bin"
    )
    overrides["codec"]["provider"]["size"] = codec_size
    overrides["codec"]["provider"]["sha256"] = codec_sha

    touch_size, touch_sha = _provider_from_disk(
        "build/touch-source-image/firmware_touch.bin"
    )
    overrides["touch"]["provider"]["size"] = touch_size
    overrides["touch"]["provider"]["sha256"] = touch_sha
    touch_regions = overrides["touch"]["regions"]
    wrapper = next(r for r in touch_regions if r["name"] == "fwpk_wrapper")
    application = next(r for r in touch_regions if r["name"] == "touch_application")
    if touch_size <= wrapper["size"]:
        raise RepinError("touch source image is not larger than its FWPK wrapper")
    application["size"] = touch_size - wrapper["size"]

    case_size, case_sha = _provider_from_disk(
        "build/case-source-image/firmware_box.bin"
    )
    overrides["case"]["provider"]["size"] = case_size
    overrides["case"]["provider"]["sha256"] = case_sha
    case_regions = overrides["case"]["regions"]
    wrapper = next(r for r in case_regions if r["name"] == "even_wrapper")
    application = next(r for r in case_regions if r["name"] == "case_application")
    if case_size <= wrapper["size"]:
        raise RepinError("case source image is not larger than its EVEN wrapper")
    application["size"] = case_size - wrapper["size"]

    manifest["component_overrides"] = overrides
    return manifest


def repin_package(manifest_on_disk: dict) -> dict:
    """Assemble the package with strict_release disabled to learn its bytes,
    then return the manifest with package.expected_size/expected_sha256 set.

    Assembly needs a real manifest path (providers/regions resolve relative
    to the project root), so this writes the candidate manifest to a scratch
    file beside the real one rather than mutating it before the pins are
    known to be self-consistent.
    """
    with tempfile.NamedTemporaryFile(
        "w", dir=str(MANIFEST_PATH.parent), suffix=".scratch.json", delete=False,
    ) as handle:
        handle.write(json.dumps(manifest_on_disk, indent=2) + "\n")
        scratch_path = Path(handle.name)
    try:
        resolved, _project_root, payloads = oc.verify_manifest(
            scratch_path, toolchain_profile=oc.DEFAULT_TOOLCHAIN_PROFILE,
            strict_release=False,
        )
        image, _entries = oc.assemble_evenota(resolved, payloads)
    finally:
        scratch_path.unlink(missing_ok=True)
    manifest_on_disk["package"]["expected_size"] = len(image)
    manifest_on_disk["package"]["expected_sha256"] = oc.sha256_bytes(image)
    return manifest_on_disk


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true",
        help="verify the manifest already matches on-disk builds; do not write",
    )
    args = parser.parse_args()

    before = MANIFEST_PATH.read_text()
    manifest = compute_component_overrides()
    manifest = repin_package(manifest)
    after = json.dumps(manifest, indent=2) + "\n"

    if args.check:
        if before != after:
            print(
                "g2-2.2.6.10-source-only.json is stale relative to the "
                "on-disk source builds; rerun without --check to repin it.",
                file=sys.stderr,
            )
            return 1
        print(
            f"source-only manifest is current: {manifest['package']['expected_size']}"
            f" bytes, sha256 {manifest['package']['expected_sha256']}"
        )
        return 0

    MANIFEST_PATH.write_text(after)

    print(
        f"source-only package: {manifest['package']['expected_size']} bytes, "
        f"sha256 {manifest['package']['expected_sha256']}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RepinError, oc.OpenCFWError) as exc:
        raise SystemExit(f"build_g2_source_only_manifest: error: {exc}") from exc
