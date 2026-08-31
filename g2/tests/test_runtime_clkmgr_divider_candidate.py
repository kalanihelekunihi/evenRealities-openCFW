#!/usr/bin/env python3
"""Host and Cortex-M55 gates for the clean-room clock-divider candidate."""

# SPDX-License-Identifier: MIT

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import verify_g2_clkmgr_divider_public as verifier  # noqa: E402
SOURCE = ROOT / "components/shared/ambiq/runtime_clkmgr_divider_candidate.c"
HEADER = SOURCE.with_suffix(".h")
FIXTURE = ROOT / "tests/fixtures/runtime_clkmgr_divider_candidate_host.c"


class ClockManagerDividerCandidateTests(unittest.TestCase):
    def test_host_behavior_and_target_object(self) -> None:
        compiler = shutil.which("clang")
        self.assertIsNotNone(compiler)
        with tempfile.TemporaryDirectory(prefix="open-cfw-clkmgr-divider-") as tmp:
            temporary = Path(tmp)
            host = temporary / "host"
            command = [
                compiler, "-std=c11", "-Wall", "-Wextra", "-Werror",
                "-I", str(SOURCE.parent), str(SOURCE), str(FIXTURE),
                "-o", str(host),
            ]
            subprocess.run(command, check=True, capture_output=True, text=True)
            subprocess.run([str(host)], check=True, capture_output=True, text=True)

            target = temporary / "divider.o"
            command = [
                compiler, "--target=arm-none-eabi", "-mcpu=cortex-m55",
                "-mthumb", "-mfloat-abi=hard", "-ffreestanding",
                "-fno-builtin", "-std=c11", "-Wall", "-Wextra", "-Werror",
                "-I", str(SOURCE.parent), "-c", str(SOURCE), "-o", str(target),
            ]
            subprocess.run(command, check=True, capture_output=True, text=True)
            self.assertGreater(target.stat().st_size, 0)
            undefined = subprocess.run(
                ["nm", "-u", str(target)], check=True,
                capture_output=True, text=True,
            ).stdout.strip()
            self.assertEqual(undefined, "")

    def test_source_is_semantic_c(self) -> None:
        combined = SOURCE.read_text() + HEADER.read_text()
        self.assertEqual(combined.count("SPDX-License-Identifier: MIT"), 2)
        self.assertNotIn("__asm", combined)
        self.assertNotIn(".byte", combined)
        self.assertIn("open_cfw_clkmgr_hfrc2_uq15_divider", combined)
        self.assertIn("open_cfw_clkmgr_hfrc_integer_divider", combined)

    def test_public_dual_image_route_contract(self) -> None:
        report = verifier.verify()
        self.assertEqual(
            report["status"], "public-clock-divider-source-and-route-verified")
        self.assertEqual(report["functions"], 2)
        self.assertEqual(report["profiles_declared"],
                         ["apple-clang", "linux-clang"])
        self.assertTrue(report[
            "private_admission_artifacts_required_for_receipt_reproduction"])
        self.assertFalse(report["private_admission_receipt_reproduced"])
        self.assertEqual(
            report["hardware_validation"],
            "blocked by unavailable physical evidence",
        )
        self.assertEqual(report["hardware_operations"], [])

    def test_public_verifier_rejects_source_identity_drift(self) -> None:
        with tempfile.TemporaryDirectory(prefix="open-cfw-clkmgr-public-") as tmp:
            changed = Path(tmp) / "runtime_clkmgr_divider_candidate.c"
            changed.write_bytes(verifier.SOURCE.read_bytes() + b"\n")
            with mock.patch.object(verifier, "SOURCE", changed):
                with self.assertRaisesRegex(
                    verifier.VerificationError,
                    "source identity changed",
                ):
                    verifier.verify()


if __name__ == "__main__":
    unittest.main()
