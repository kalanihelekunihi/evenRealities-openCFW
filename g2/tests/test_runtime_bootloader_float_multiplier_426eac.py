#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT
    / "components/bootloader/core_overlay/runtime_float_multiplier_426eac.c"
)
FIXTURE = (
    ROOT / "tests/fixtures/bootloader_float_multiplier_426eac_host.c"
)


class BootloaderFloatMultiplierTests(unittest.TestCase):
    def test_host_multiplier_validation_and_encoding(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="open-cfw-float-multiplier-"
        ) as directory:
            executable = Path(directory) / "float-multiplier"
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

    def test_source_is_reviewable_c(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        for token in (
            "open_cfw_bootloader_float_multiplier_426eac",
            'pcs("aapcs-vfp")',
            "open_cfw_float_multiplier_u8 *scale_output",
            "open_cfw_float_multiplier_u16 *integer_output",
            "open_cfw_float_multiplier_u32 *fraction_output",
            "open_cfw_bootloader_floorf_427c90",
            "open_cfw_bootloader_fmodf_427ccc",
            "open_cfw_bootloader_roundf_427d98",
            "open_cfw_bootloader_ceilf_427dd0",
            "0x1p-23f", "0x1.f80002p+5f", "0x1p+24f",
            "0x1.800002p+6f",
        ):
            self.assertIn(token, source)
        for token in ("__asm", ".byte", ".short", ".word"):
            self.assertNotIn(token, source)


if __name__ == "__main__":
    unittest.main()
