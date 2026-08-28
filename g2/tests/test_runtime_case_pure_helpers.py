# SPDX-License-Identifier: MIT
from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "components/shared/case"
SOURCE = CASE / "runtime_case_pure_helpers.c"
FIXTURE = ROOT / "tests/fixtures/runtime_case_pure_helpers_host.c"


class CasePureHelperTests(unittest.TestCase):
    def test_host_oracle(self) -> None:
        clang = shutil.which("clang")
        if clang is None:
            self.skipTest("clang unavailable")
        with tempfile.TemporaryDirectory(prefix="g2-case-pure-host-") as tmp:
            executable = Path(tmp) / "oracle"
            subprocess.run([
                clang, "-std=c11", "-O2", "-Wall", "-Wextra",
                "-Werror", "-I", str(CASE), str(SOURCE), str(FIXTURE),
                "-o", str(executable),
            ], check=True, capture_output=True, text=True)
            subprocess.run([str(executable)], check=True, timeout=5)

    def test_strict_cortex_m0plus_compile(self) -> None:
        clang = shutil.which("clang")
        if clang is None:
            self.skipTest("clang unavailable")
        with tempfile.TemporaryDirectory(prefix="g2-case-pure-target-") as tmp:
            output = Path(tmp) / "pure.o"
            subprocess.run([
                clang, "--target=arm-none-eabi", "-mcpu=cortex-m0plus",
                "-mthumb", "-std=c11", "-Oz", "-ffreestanding", "-fno-builtin",
                "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra",
                "-Werror", "-I", str(CASE), "-c", str(SOURCE), "-o", str(output),
            ], check=True, capture_output=True, text=True)
            self.assertGreater(output.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
