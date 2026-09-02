#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_clkgen_config_426ccc.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_clkgen_config_426ccc_host.c"


class BootloaderClkgenConfigTests(unittest.TestCase):
    def test_host_register_field_semantics(self) -> None:
        with tempfile.TemporaryDirectory(prefix="open-cfw-clkgen-config-") as directory:
            executable = Path(directory) / "clkgen-config"
            subprocess.run(
                [
                    "/usr/bin/clang", "-std=c11", "-O2", "-Wall", "-Wextra",
                    "-Werror", "-DOPEN_CFW_CLKGEN_CONFIG_HOST_TEST",
                    str(SOURCE), str(FIXTURE), "-o", str(executable),
                ],
                cwd=ROOT,
                check=True,
            )
            subprocess.run([str(executable)], cwd=ROOT, check=True)

    def test_source_is_reviewable_c(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        for token in (
            "0x40004020U", "0x4000404CU", "0x40004048U",
            "clock_select : 2", "divider : 29", "preserved_top_bit : 1",
            "0x1FFFFFFFU",
        ):
            self.assertIn(token, source)
        for token in ("__asm", ".byte", ".short", ".word"):
            self.assertNotIn(token, source)


if __name__ == "__main__":
    unittest.main()
