#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT
    / "components/bootloader/core_overlay/"
      "runtime_float_encoding_select_426f6c.c"
)
FIXTURE = (
    ROOT / "tests/fixtures/bootloader_float_encoding_select_426f6c_host.c"
)


class BootloaderFloatEncodingSelectTests(unittest.TestCase):
    def test_host_selection_status_and_layout(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="open-cfw-float-select-"
        ) as directory:
            executable = Path(directory) / "float-select"
            subprocess.run(
                [
                    "/usr/bin/clang", "-std=c11", "-O2", "-Wall",
                    "-Wextra", "-Werror", str(SOURCE), str(FIXTURE),
                    "-lm", "-o", str(executable),
                ],
                cwd=ROOT,
                check=True,
            )
            subprocess.run([str(executable)], cwd=ROOT, check=True)

    def test_source_is_reviewable_hard_float_c(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        for token in (
            "open_cfw_bootloader_float_encoding_select_426f6c",
            'pcs("aapcs-vfp")',
            "open_cfw_bootloader_float_ratio_426db4",
            "open_cfw_bootloader_float_multiplier_426eac",
            "0x1.e00002p+9f", "60.0f", "240.0f",
            "return 6U", "return 5U", "return 1U", "return 0U",
            "output->ratio_encoding", "output->fraction",
        ):
            self.assertIn(token, source)
        for token in ("__asm", ".byte", ".short", ".word"):
            self.assertNotIn(token, source)


if __name__ == "__main__":
    unittest.main()
