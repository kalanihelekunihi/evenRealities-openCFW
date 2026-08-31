#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/health_data_manager.c"
FIXTURE = ROOT / "tests/fixtures/health_data_manager_host.c"


class HealthDataManagerCandidateTests(unittest.TestCase):
    def test_host_behavior(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            executable = Path(directory) / "health-data-manager"
            subprocess.run(
                [
                    "clang", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                    str(FIXTURE), "-o", str(executable),
                ],
                cwd=ROOT,
                check=True,
            )
            subprocess.run([str(executable)], check=True)

    def test_strict_thumb_compile_exposes_ten_entries(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            obj = Path(directory) / "health-data-manager.o"
            subprocess.run(
                [
                    "clang", "-target", "thumbv7em-none-eabi", "-mthumb", "-O2",
                    "-ffreestanding", "-fno-jump-tables", "-fomit-frame-pointer",
                    "-fno-builtin", "-mno-unaligned-access", "-fno-unwind-tables",
                    "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections",
                    "-fdata-sections", "-Wall", "-Wextra", "-Werror",
                    "-c", str(SOURCE), "-o", str(obj),
                ],
                cwd=ROOT,
                check=True,
            )
            symbols = subprocess.run(
                ["nm", str(obj)], check=True, capture_output=True, text=True
            ).stdout
            entries = {
                fields[2]
                for line in symbols.splitlines()
                if len(fields := line.split()) == 3 and fields[1] == "T"
            }
            self.assertEqual(
                entries,
                {
                    "open_cfw_health_data_type_index",
                    "open_cfw_health_data_slot_for_type",
                    "open_cfw_health_data_type_name",
                    "open_cfw_health_data_manager_init",
                    "open_cfw_health_data_convert_from_pb",
                    "open_cfw_health_data_save_single",
                    "open_cfw_health_data_save_multiple",
                    "open_cfw_health_data_convert_highlight_from_pb",
                    "open_cfw_health_data_save_single_highlight",
                    "open_cfw_health_data_save_multiple_highlights",
                },
            )

    def test_source_is_pinned(self) -> None:
        data = SOURCE.read_bytes()
        self.assertEqual(len(data), 15854)
        self.assertEqual(
            hashlib.sha256(data).hexdigest(),
            "dc725113b1d7b985dfd0f958a884848e5757d934d9edd32e64547e836861962b",
        )


if __name__ == "__main__":
    unittest.main()
