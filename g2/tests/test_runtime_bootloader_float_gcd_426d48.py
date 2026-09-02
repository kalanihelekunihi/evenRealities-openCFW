#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_float_gcd_426d48.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_float_gcd_426d48_host.c"


class BootloaderFloatGcdTests(unittest.TestCase):
    def test_host_bounded_euclidean_semantics(self) -> None:
        with tempfile.TemporaryDirectory(prefix="open-cfw-float-gcd-") as directory:
            executable = Path(directory) / "float-gcd"
            subprocess.run(
                [
                    "/usr/bin/clang", "-std=c11", "-O2", "-Wall", "-Wextra",
                    "-Werror", "-DOPEN_CFW_FLOAT_GCD_HOST_TEST",
                    str(SOURCE), str(FIXTURE), "-o", str(executable),
                ],
                cwd=ROOT,
                check=True,
            )
            subprocess.run([str(executable)], cwd=ROOT, check=True)

    def test_source_is_reviewable_c(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        for token in (
            "open_cfw_bootloader_float_gcd_426d48",
            "open_cfw_bootloader_floorf_427c90",
            'pcs("aapcs-vfp")',
            "0x1p-23f", "iteration >= 16U", "large - quotient * small",
        ):
            self.assertIn(token, source)
        for token in ("__asm", ".byte", ".short", ".word"):
            self.assertNotIn(token, source)


if __name__ == "__main__":
    unittest.main()
