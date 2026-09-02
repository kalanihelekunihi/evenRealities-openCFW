#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_memset_wrapper_426c10.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_memset_wrapper_426c10_host.c"


class BootloaderMemsetWrapperTests(unittest.TestCase):
    def test_host_semantics_and_standard_argument_order(self) -> None:
        with tempfile.TemporaryDirectory(prefix="open-cfw-memset-wrapper-") as directory:
            executable = Path(directory) / "memset-wrapper"
            subprocess.run(
                [
                    "/usr/bin/clang",
                    "-std=c11",
                    "-O2",
                    "-Wall",
                    "-Wextra",
                    "-Werror",
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
        self.assertIn("return destination", source)
        self.assertIn("open_cfw_bootloader_retained_memset_41560c", source)
        self.assertNotIn("__asm", source)
        self.assertNotIn(".byte", source)
        self.assertNotIn(".short", source)


if __name__ == "__main__":
    unittest.main()
