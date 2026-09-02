#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_clkgen_hfadj_enable_426c58.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_clkgen_hfadj_enable_426c58_host.c"


class BootloaderClkgenHfadjEnableTests(unittest.TestCase):
    def test_host_register_semantics_and_low_byte_abi(self) -> None:
        with tempfile.TemporaryDirectory(prefix="open-cfw-hfadj-enable-") as directory:
            executable = Path(directory) / "hfadj-enable"
            subprocess.run(
                [
                    "/usr/bin/clang",
                    "-std=c11",
                    "-O2",
                    "-Wall",
                    "-Wextra",
                    "-Werror",
                    "-DOPEN_CFW_HFADJ_HOST_TEST",
                    str(SOURCE),
                    str(FIXTURE),
                    "-o",
                    str(executable),
                ],
                cwd=ROOT,
                check=True,
            )
            subprocess.run([str(executable)], cwd=ROOT, check=True)

    def test_source_is_reviewable_c(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        self.assertIn("0x40004044U", source)
        self.assertIn("enable & 0xFFU", source)
        self.assertIn("value & ~1U", source)
        self.assertNotIn("__asm", source)
        self.assertNotIn(".byte", source)
        self.assertNotIn(".short", source)


if __name__ == "__main__":
    unittest.main()
