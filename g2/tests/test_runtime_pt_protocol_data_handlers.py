# SPDX-License-Identifier: MIT
from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INCLUDE = ROOT / "components/apollo_main/core_overlay"
SOURCES = [
    INCLUDE / "pt_protocol_procsr.c",
    INCLUDE / "pt_protocol_handlers_data.c",
]


class PtProtocolDataHandlersTests(unittest.TestCase):
    def test_sources_compile_for_host_and_apollo510(self) -> None:
        compiler = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        with tempfile.TemporaryDirectory(prefix="g2-pt-data-") as directory:
            for source in SOURCES:
                host = Path(directory) / (source.stem + "-host.o")
                target = Path(directory) / (source.stem + "-target.o")
                subprocess.run([
                    "clang", "-std=c11", "-Wall", "-Wextra", "-Werror",
                    "-I", str(INCLUDE), "-c", str(source), "-o", str(host),
                ], check=True, capture_output=True, text=True)
                subprocess.run([
                    compiler, "--target=arm-none-eabi", "-mcpu=cortex-m55",
                    "-mthumb", "-std=c11", "-Oz", "-ffreestanding",
                    "-fno-builtin", "-ffunction-sections", "-fdata-sections",
                    "-Wall", "-Wextra", "-Werror", "-I", str(INCLUDE),
                    "-c", str(source), "-o", str(target),
                ], check=True, capture_output=True, text=True)

    def test_recovered_command_set_is_present(self) -> None:
        text = (INCLUDE / "pt_protocol_handlers_data.c").read_text()
        for command in (0x05, 0x25, 0x35, 0x39, 0x44, 0x45, 0x46,
                        0x67, 0x69, 0x6B, 0x6C, 0x6D):
            self.assertIn(f"{{0x{command:02X}U,", text)
        self.assertIn("86400U", text)
        self.assertIn("read_diagnostic_blob_36", text)


if __name__ == "__main__":
    unittest.main()
