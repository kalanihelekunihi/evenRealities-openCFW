#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_float_ratio_426db4.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_float_ratio_426db4_host.c"


class BootloaderFloatRatioTests(unittest.TestCase):
    def test_host_ratio_validation_and_scaling(self) -> None:
        with tempfile.TemporaryDirectory(prefix="open-cfw-float-ratio-") as directory:
            executable = Path(directory) / "float-ratio"
            subprocess.run(
                [
                    "/usr/bin/clang", "-std=c11", "-O2", "-Wall", "-Wextra",
                    "-Werror", str(SOURCE), str(FIXTURE), "-o", str(executable),
                ],
                cwd=ROOT,
                check=True,
            )
            subprocess.run([str(executable)], cwd=ROOT, check=True)

    def test_source_is_reviewable_c(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        for token in (
            "open_cfw_bootloader_float_ratio_426db4",
            "open_cfw_bootloader_float_gcd_426d48",
            'pcs("aapcs-vfp")',
            "open_cfw_float_ratio_u8 *first_ratio",
            "open_cfw_float_ratio_u16 *second_ratio",
            "open_cfw_bootloader_fmodf_427ccc",
            "open_cfw_bootloader_roundf_427d98",
            "0x1.000002p-23f", "0x1.e00002p+9f", "0x1.f80002p+5f",
            "(second_count + 3U) / second_count",
        ):
            self.assertIn(token, source)
        for token in ("__asm", ".byte", ".short", ".word"):
            self.assertNotIn(token, source)


if __name__ == "__main__":
    unittest.main()
