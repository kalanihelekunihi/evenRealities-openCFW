#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_clkgen_disable_426d1e.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_clkgen_disable_426d1e_host.c"


class BootloaderClkgenDisableTests(unittest.TestCase):
    def test_host_bit_preservation(self) -> None:
        with tempfile.TemporaryDirectory(prefix="open-cfw-clkgen-disable-") as directory:
            executable = Path(directory) / "clkgen-disable"
            subprocess.run(
                [
                    "/usr/bin/clang", "-std=c11", "-O2", "-Wall", "-Wextra",
                    "-Werror", "-DOPEN_CFW_CLKGEN_DISABLE_HOST_TEST",
                    str(SOURCE), str(FIXTURE), "-o", str(executable),
                ],
                cwd=ROOT,
                check=True,
            )
            subprocess.run([str(executable)], cwd=ROOT, check=True)

    def test_source_is_reviewable_c(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        for token in (
            "open_cfw_bootloader_clkgen_disable_426d1e",
            "0x40004050U", "value >>= 1", "value <<= 1",
        ):
            self.assertIn(token, source)
        for token in ("__asm", ".byte", ".short", ".word"):
            self.assertNotIn(token, source)


if __name__ == "__main__":
    unittest.main()
