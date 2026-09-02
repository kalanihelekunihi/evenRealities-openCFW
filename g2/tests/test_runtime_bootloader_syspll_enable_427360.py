# SPDX-License-Identifier: MIT
from __future__ import annotations

import ctypes
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_syspll_enable_427360.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_syspll_enable_427360_host.c"


class SyspllEnableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory()
        library = Path(cls.temp.name) / "syspll-enable.so"
        subprocess.run(
            ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared",
             "-fPIC", str(FIXTURE), "-o", str(library)],
            cwd=ROOT, check=True,
        )
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.open_cfw_host_syspll_enable_reset.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
        ]
        cls.lib.open_cfw_bootloader_row6_start_427360.argtypes = [ctypes.c_void_p]
        cls.lib.open_cfw_bootloader_row6_start_427360.restype = ctypes.c_uint32
        for name in (
            "open_cfw_host_syspll_enable_call",
            "open_cfw_host_syspll_enable_prefix",
            "open_cfw_host_syspll_enable_pllctl0",
            "open_cfw_host_syspll_enable_vrctrl_reads",
            "open_cfw_host_syspll_enable_pllctl0_reads",
            "open_cfw_host_syspll_enable_pllctl0_writes",
        ):
            getattr(cls.lib, name).restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def reset(self, prefix: int, vrctrl: int = 0, pllctl0: int = 0) -> None:
        self.lib.open_cfw_host_syspll_enable_reset(prefix, vrctrl, pllctl0)

    def test_invalid_handles_have_no_mmio_side_effects(self) -> None:
        self.reset(0xA1504C31, 0x000F0000, 0x12345678)
        self.assertEqual(
            self.lib.open_cfw_bootloader_row6_start_427360(None), 2)
        self.assertEqual(self.lib.open_cfw_host_syspll_enable_call(), 2)
        self.assertEqual(self.lib.open_cfw_host_syspll_enable_vrctrl_reads(), 0)
        self.assertEqual(self.lib.open_cfw_host_syspll_enable_pllctl0_reads(), 0)
        self.assertEqual(self.lib.open_cfw_host_syspll_enable_pllctl0_writes(), 0)

    def test_already_enabled_is_idempotent(self) -> None:
        self.reset(0xA3504C30, 0, 0x12345678)
        self.assertEqual(self.lib.open_cfw_host_syspll_enable_call(), 0)
        self.assertEqual(self.lib.open_cfw_host_syspll_enable_prefix(), 0xA3504C30)
        self.assertEqual(self.lib.open_cfw_host_syspll_enable_vrctrl_reads(), 0)
        self.assertEqual(self.lib.open_cfw_host_syspll_enable_pllctl0_writes(), 0)

    def test_inactive_simobuck_rejects_without_writes(self) -> None:
        self.reset(0xA1504C30, 0x00070000, 0x12345678)
        self.assertEqual(self.lib.open_cfw_host_syspll_enable_call(), 7)
        self.assertEqual(self.lib.open_cfw_host_syspll_enable_prefix(), 0xA1504C30)
        self.assertEqual(self.lib.open_cfw_host_syspll_enable_vrctrl_reads(), 1)
        self.assertEqual(self.lib.open_cfw_host_syspll_enable_pllctl0_writes(), 0)

    def test_active_simobuck_enables_pll_and_state(self) -> None:
        self.reset(0xA1504C30, 0x000F0000, 0x12345678)
        self.assertEqual(self.lib.open_cfw_host_syspll_enable_call(), 0)
        self.assertEqual(self.lib.open_cfw_host_syspll_enable_prefix(), 0xA3504C30)
        self.assertEqual(self.lib.open_cfw_host_syspll_enable_vrctrl_reads(), 4)
        self.assertEqual(self.lib.open_cfw_host_syspll_enable_pllctl0_reads(), 1)
        self.assertEqual(self.lib.open_cfw_host_syspll_enable_pllctl0_writes(), 1)
        self.assertEqual(self.lib.open_cfw_host_syspll_enable_pllctl0(), 0x32345678)

    def test_source_is_reviewable_c_with_authenticated_mmio(self) -> None:
        text = SOURCE.read_text()
        self.assertIn("am_hal_syspll_enable", text)
        self.assertIn("0x40020060U", text)
        self.assertIn("0x400204d8U", text)
        self.assertNotIn("__asm", text)
        self.assertNotIn(".byte", text)


if __name__ == "__main__":
    unittest.main()
