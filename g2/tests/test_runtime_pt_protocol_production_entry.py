# SPDX-License-Identifier: MIT
from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "components/apollo_main/core_overlay"
SOURCES = sorted(CORE.glob("pt_protocol*.c"))
FIXTURE = ROOT / "tests/fixtures/pt_protocol_production_entry_host.c"


class PtProtocolProductionEntryTests(unittest.TestCase):
    def test_host_lifecycle_and_stock_shape(self) -> None:
        with tempfile.TemporaryDirectory(prefix="g2-pt-entry-host-") as tmp:
            executable = Path(tmp) / "oracle"
            subprocess.run([
                "/usr/bin/clang", "-std=c11", "-O2", "-Wall", "-Wextra",
                "-Werror", "-I", str(CORE), *map(str, SOURCES), str(FIXTURE),
                "-o", str(executable),
            ], check=True, capture_output=True, text=True)
            subprocess.run([str(executable)], check=True)

    def test_strict_apollo510_link(self) -> None:
        with tempfile.TemporaryDirectory(prefix="g2-pt-entry-target-") as tmp:
            objects = []
            for source in SOURCES:
                output = Path(tmp) / f"{source.stem}.o"
                subprocess.run([
                    "/usr/bin/clang", "--target=arm-none-eabi", "-mcpu=cortex-m55",
                    "-mthumb", "-std=c11", "-Oz", "-ffreestanding", "-fno-builtin",
                    "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra",
                    "-Werror", "-I", str(CORE), "-c", str(source), "-o", str(output),
                ], check=True, capture_output=True, text=True)
                objects.append(output)
            linked = Path(tmp) / "pt-entry.o"
            subprocess.run(["/opt/homebrew/opt/lld/bin/ld.lld", "-r", "-o", str(linked),
                            *map(str, objects)], check=True, capture_output=True, text=True)
            undefined = subprocess.run([
                "/opt/homebrew/opt/llvm/bin/llvm-nm", "-u", str(linked),
            ], check=True, capture_output=True, text=True).stdout.strip()
            self.assertEqual(undefined, "")


if __name__ == "__main__":
    unittest.main()
