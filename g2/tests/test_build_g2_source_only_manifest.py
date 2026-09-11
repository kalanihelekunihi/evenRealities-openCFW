"""Tests for tools/build_g2_source_only_manifest.py and the manifest it repins.

These check structure and self-consistency (every component resolves to a
``source_build`` provider whose declared size/SHA-256 match the file on
disk, and the declared package pin matches an actual assembly) rather than
literal hash values, because the underlying touch/case/codec source builds
are rebuilt by other concurrently running agents.

The repin is a single, real subprocess call (this repository's builds
compete with several other concurrently running agents for CPU, so it is
shared across every test method via ``setUpClass`` rather than repeated per
test) plus one idempotent ``--check`` call; every other assertion inspects
the resulting file in-process.
"""

# SPDX-License-Identifier: MIT

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = ROOT / "manifests/g2-2.2.6.10-source-only.json"
sys.path.insert(0, str(ROOT / "tools"))

import open_cfw as oc  # noqa: E402

SIX_COMPONENTS = {
    "apollo_main", "apollo_bootloader", "ble_em9305", "codec", "touch", "case",
}

REQUIRED_SOURCE_BUILDS = (
    ROOT / "build/gx8002-source-candidate/firmware_codec.hybrid-candidate.bin",
    ROOT / "build/touch-source-image/firmware_touch.bin",
    ROOT / "build/case-source-image/firmware_box.bin",
)


def _missing_source_builds() -> list[str]:
    return [str(p) for p in REQUIRED_SOURCE_BUILDS if not p.is_file()]


@unittest.skipIf(
    _missing_source_builds(),
    "source builds not present; run `make gx8002-source-candidate "
    "touch-source-image case-source-image` first",
)
class SourceOnlyManifestRepinTests(unittest.TestCase):
    original_manifest: str
    check_after_repin: subprocess.CompletedProcess

    @classmethod
    def setUpClass(cls) -> None:
        cls.original_manifest = MANIFEST_PATH.read_text()
        cls.pre_repin_json = json.loads(cls.original_manifest)
        repin = subprocess.run(
            [sys.executable, str(ROOT / "tools/build_g2_source_only_manifest.py")],
            capture_output=True, text=True, cwd=str(ROOT),
        )
        assert repin.returncode == 0, (
            f"repin failed:\nstdout={repin.stdout}\nstderr={repin.stderr}"
        )
        cls.repin_result = repin
        cls.manifest = json.loads(MANIFEST_PATH.read_text())
        cls.check_after_repin = subprocess.run(
            [sys.executable, str(ROOT / "tools/build_g2_source_only_manifest.py"),
             "--check"],
            capture_output=True, text=True, cwd=str(ROOT),
        )

    @classmethod
    def tearDownClass(cls) -> None:
        MANIFEST_PATH.write_text(cls.original_manifest)

    def test_pre_repin_manifest_is_valid_json_and_extends_core_source(self) -> None:
        self.assertEqual(
            self.pre_repin_json["extends"], "g2-2.2.6.10-core-source.json"
        )

    def test_repin_succeeded(self) -> None:
        self.assertEqual(self.repin_result.returncode, 0)

    def test_selects_source_build_for_all_six_components(self) -> None:
        resolved = oc.load_manifest(MANIFEST_PATH)
        names = {c["name"] for c in resolved["components"]}
        self.assertEqual(names, SIX_COMPONENTS)
        for component in resolved["components"]:
            self.assertEqual(
                component["provider"]["kind"], "source_build",
                msg=f"{component['name']} is not a source_build provider "
                    "(source-only manifest must select source_build for "
                    "every component, not official_blob)",
            )

    def test_no_official_blob_provider_survives_the_overrides(self) -> None:
        resolved = oc.load_manifest(MANIFEST_PATH)
        blob_components = [
            c["name"] for c in resolved["components"]
            if c["provider"]["kind"] == "official_blob"
        ]
        self.assertEqual(blob_components, [])

    def test_repin_is_idempotent_and_check_agrees(self) -> None:
        self.assertEqual(
            self.check_after_repin.returncode, 0,
            msg="--check disagreed with the repin it followed:\n"
                f"{self.check_after_repin.stdout}\n{self.check_after_repin.stderr}",
        )

    def test_provider_pins_match_the_bytes_on_disk(self) -> None:
        overrides = self.manifest["component_overrides"]
        checks = {
            "codec": ROOT / "build/gx8002-source-candidate/firmware_codec.hybrid-candidate.bin",
            "touch": ROOT / "build/touch-source-image/firmware_touch.bin",
            "case": ROOT / "build/case-source-image/firmware_box.bin",
        }
        for name, path in checks.items():
            provider = overrides[name]["provider"]
            data = path.read_bytes()
            self.assertEqual(provider["size"], len(data))
            self.assertEqual(provider["sha256"], oc.sha256_bytes(data))

    def test_touch_and_case_regions_partition_their_provider_exactly(self) -> None:
        overrides = self.manifest["component_overrides"]
        for name in ("touch", "case"):
            provider_size = overrides[name]["provider"]["size"]
            regions = overrides[name]["regions"]
            total = sum(r["size"] for r in regions)
            self.assertEqual(
                total, provider_size,
                msg=f"{name} regions ({total}) do not cover its provider "
                    f"({provider_size})",
            )

    def test_package_pin_matches_an_actual_assembly(self) -> None:
        resolved, _root, payloads = oc.verify_manifest(
            MANIFEST_PATH, toolchain_profile=oc.DEFAULT_TOOLCHAIN_PROFILE,
            strict_release=False,
        )
        image, _entries = oc.assemble_evenota(resolved, payloads)
        self.assertEqual(self.manifest["package"]["expected_size"], len(image))
        self.assertEqual(
            self.manifest["package"]["expected_sha256"], oc.sha256_bytes(image)
        )


if __name__ == "__main__":
    unittest.main()
