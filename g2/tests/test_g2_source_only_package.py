"""Assemble and verify the source-only EVENOTA package end to end.

This is the host-side equivalent of `make source-only`'s packaging step: it
repins manifests/g2-2.2.6.10-source-only.json against whatever source builds
are currently on disk, assembles the EVENOTA image into a private scratch
directory (never build/source-only/, so this never collides with another
agent's shared build output), and checks the assembled package against the
manifest's own pins and structure -- not a hardcoded hash, since the
underlying component builds are rebuilt by other concurrently running
agents.
"""

# SPDX-License-Identifier: MIT

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = ROOT / "manifests/g2-2.2.6.10-source-only.json"
sys.path.insert(0, str(ROOT / "tools"))

import open_cfw as oc  # noqa: E402

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
class SourceOnlyPackageBuildTests(unittest.TestCase):
    def setUp(self) -> None:
        self.original_manifest = MANIFEST_PATH.read_text()
        self.addCleanup(lambda: MANIFEST_PATH.write_text(self.original_manifest))
        self.scratch = Path(
            tempfile.mkdtemp(prefix="xc-001-source-only-", dir=str(ROOT / "build"))
        )
        self.addCleanup(lambda: shutil.rmtree(self.scratch, ignore_errors=True))

        repin = subprocess.run(
            [sys.executable, str(ROOT / "tools/build_g2_source_only_manifest.py")],
            capture_output=True, text=True, cwd=str(ROOT),
        )
        self.assertEqual(
            repin.returncode, 0,
            msg=f"repin failed:\n{repin.stdout}\n{repin.stderr}",
        )

    def test_build_assembles_and_self_verifies_on_macos(self) -> None:
        build = subprocess.run(
            [sys.executable, str(ROOT / "tools/open_cfw.py"), "build",
             "--manifest", str(MANIFEST_PATH),
             "--output-dir", str(self.scratch),
             "--toolchain-profile", "apple-clang"],
            capture_output=True, text=True, cwd=str(ROOT),
        )
        self.assertEqual(
            build.returncode, 0,
            msg=f"open_cfw build failed:\n{build.stdout}\n{build.stderr}",
        )
        self.assertIn("reference: byte-identical", build.stdout)

        package_dir = self.scratch / "package"
        packages = list(package_dir.glob("*.evenota.bin"))
        self.assertEqual(len(packages), 1, msg=f"unexpected packages: {packages}")

        verify = subprocess.run(
            [sys.executable, str(ROOT / "tools/open_cfw.py"), "verify",
             "--manifest", str(MANIFEST_PATH),
             "--toolchain-profile", "apple-clang"],
            capture_output=True, text=True, cwd=str(ROOT),
        )
        self.assertEqual(
            verify.returncode, 0,
            msg=f"open_cfw verify failed:\n{verify.stdout}\n{verify.stderr}",
        )

    def test_assembled_package_has_six_components_all_source_build(self) -> None:
        resolved, _root, payloads = oc.verify_manifest(
            MANIFEST_PATH, toolchain_profile=oc.DEFAULT_TOOLCHAIN_PROFILE,
            strict_release=True,
        )
        self.assertEqual(len(resolved["components"]), 6)
        for component in resolved["components"]:
            self.assertEqual(component["provider"]["kind"], "source_build")
        image, _entries = oc.assemble_evenota(resolved, payloads)
        self.assertEqual(len(image), resolved["package"]["expected_size"])
        self.assertEqual(oc.sha256_bytes(image), resolved["package"]["expected_sha256"])


if __name__ == "__main__":
    unittest.main()
