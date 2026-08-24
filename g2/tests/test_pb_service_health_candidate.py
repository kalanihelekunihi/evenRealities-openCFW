#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/pb_service_health.c"
FIXTURE = ROOT / "tests/fixtures/pb_service_health_host.c"


class PbServiceHealthCandidateTests(unittest.TestCase):
    def test_host_behavior(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            executable = Path(directory) / "pb-service-health"
            subprocess.run([
                "clang", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                str(FIXTURE), "-o", str(executable),
            ], cwd=ROOT, check=True)
            subprocess.run([str(executable)], check=True)

    def test_strict_thumb_compile_exposes_nine_entries(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            obj = Path(directory) / "pb-service-health.o"
            subprocess.run([
                "clang", "-target", "thumbv7em-none-eabi", "-mthumb", "-O2",
                "-ffreestanding", "-fno-jump-tables", "-fomit-frame-pointer",
                "-fno-builtin", "-mno-unaligned-access", "-fno-unwind-tables",
                "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections",
                "-fdata-sections", "-Wall", "-Wextra", "-Werror",
                "-c", str(SOURCE), "-o", str(obj),
            ], cwd=ROOT, check=True)
            symbols = subprocess.run(
                ["nm", str(obj)], check=True, capture_output=True, text=True
            ).stdout
            entries = {
                fields[2] for line in symbols.splitlines()
                if len(fields := line.split()) == 3 and fields[1] == "T"
            }
            self.assertEqual(entries, {
                "open_cfw_pb_service_health_buffer_write",
                "PB_RxHealthSingleData", "APP_PbTxEncodeHealthSingleData",
                "PB_RxHealthMultData", "APP_PbTxEncodeHealthMultData",
                "PB_RxHealthSingleHighlight",
                "APP_PbTxEncodeHealthSingleHighlight",
                "PB_RxHealthMultHighlight",
                "APP_PbTxEncodeHealthMultHighlight",
            })

    def test_source_is_pinned(self) -> None:
        data = SOURCE.read_bytes()
        self.assertEqual(len(data), 12366)
        self.assertEqual(
            hashlib.sha256(data).hexdigest(),
            "2a5faf89b2fc881b8ae2a19a28f1a2ba780fb7776939c5a560879f1c8791b6d6",
        )


if __name__ == "__main__":
    unittest.main()
