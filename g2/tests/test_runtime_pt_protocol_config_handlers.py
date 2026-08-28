# SPDX-License-Identifier: MIT
from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INCLUDE = ROOT / "components/apollo_main/core_overlay"
SOURCES = [INCLUDE / "pt_protocol_procsr.c",
           INCLUDE / "pt_protocol_handlers_config.c"]


class PtProtocolConfigHandlersTests(unittest.TestCase):
    def test_strict_host_and_apollo510_compile(self) -> None:
        compiler = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        with tempfile.TemporaryDirectory(prefix="g2-pt-config-") as directory:
            for source in SOURCES:
                for suffix, flags in (
                    ("host", ["clang"]),
                    ("target", [compiler, "--target=arm-none-eabi",
                     "-mcpu=cortex-m55", "-mthumb", "-ffreestanding",
                     "-fno-builtin", "-ffunction-sections", "-fdata-sections"]),
                ):
                    output = Path(directory) / f"{source.stem}-{suffix}.o"
                    subprocess.run(flags + ["-std=c11", "-Oz", "-Wall",
                        "-Wextra", "-Werror", "-I", str(INCLUDE), "-c",
                        str(source), "-o", str(output)], check=True,
                        capture_output=True, text=True)

    def test_exact_handler_batch_is_bound(self) -> None:
        text = (INCLUDE / "pt_protocol_handlers_config.c").read_text()
        commands = (0x01, 0x26, 0x29, 0x30, 0x38, 0x3A,
                    0x42, 0x62, 0x63, 0x64, 0x66, 0x6A)
        for command in commands:
            self.assertIn(f"{{0x{command:02X}U,", text)
        self.assertIn("write_sensor_calibration_36", text)
        self.assertIn("write_and_verify_psn_14", text)


if __name__ == "__main__":
    unittest.main()
