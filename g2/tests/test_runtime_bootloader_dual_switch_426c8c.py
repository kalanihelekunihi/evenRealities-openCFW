#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_dual_switch_426c8c.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_dual_switch_426c8c_host.c"


class BootloaderDualSwitchTests(unittest.TestCase):
    def test_host_transition_and_status_check_semantics(self) -> None:
        with tempfile.TemporaryDirectory(prefix="open-cfw-dual-switch-") as directory:
            executable = Path(directory) / "dual-switch"
            subprocess.run(
                [
                    "/usr/bin/clang",
                    "-std=c11",
                    "-O2",
                    "-Wall",
                    "-Wextra",
                    "-Werror",
                    "-DOPEN_CFW_DUAL_SWITCH_HOST_TEST",
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
        for token in (
            "0x40004044U",
            "0x40004030U",
            "0x01000000U",
            "open_cfw_bootloader_retained_status_check_41d246",
        ):
            self.assertIn(token, source)
        self.assertNotIn("__asm", source)
        self.assertNotIn(".byte", source)
        self.assertNotIn(".short", source)


if __name__ == "__main__":
    unittest.main()
