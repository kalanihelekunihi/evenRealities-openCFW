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


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import analyze_g2_clkmgr_divider_candidate as analyzer  # noqa: E402
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

    def test_dual_image_production_route_and_package(self) -> None:
        report = analyzer.run_audit()
        self.assertEqual(
            report["status"], "apollo-clkmgr-divider-production-routed")
        self.assertTrue(report["candidate"]["production_routed"])
        self.assertTrue(report["candidate"]["cross_toolchain_routed"])
        self.assertIsNone(report["candidate"]["software_blocker"])
        self.assertEqual(
            set(report["production"]),
            {"apollo_main", "apollo_bootloader", "package", "linux_clang"},
        )
        for image in ("apollo_main", "apollo_bootloader"):
            records = report["production"][image]["records"]
            self.assertEqual(len(records), 2)
            self.assertTrue(all(item["relocations"] == 0 for item in records))
            linux_records = report["production"]["linux_clang"][image]["records"]
            self.assertEqual(len(linux_records), 2)
        self.assertEqual(
            report["hardware_validation"],
            "deferred by project direction",
        )


if __name__ == "__main__":
    unittest.main()
