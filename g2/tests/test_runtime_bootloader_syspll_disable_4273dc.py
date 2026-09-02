# SPDX-License-Identifier: MIT
from __future__ import annotations

import ctypes
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_syspll_disable_4273dc.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_syspll_disable_4273dc_host.c"


class SyspllDisableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory()
        library = Path(cls.temp.name) / "syspll-disable.so"
        subprocess.run(
            ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared",
             "-fPIC", str(FIXTURE), "-o", str(library)],
            cwd=ROOT, check=True,
        )
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.open_cfw_host_syspll_disable_reset.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
        ]
        cls.lib.open_cfw_bootloader_row6_stop_4273dc.argtypes = [ctypes.c_void_p]
        cls.lib.open_cfw_bootloader_row6_stop_4273dc.restype = ctypes.c_uint32
        for name in (
            "open_cfw_host_syspll_disable_call",
            "open_cfw_host_syspll_disable_prefix",
            "open_cfw_host_syspll_disable_module",
            "open_cfw_host_syspll_disable_pllctl0",
            "open_cfw_host_syspll_disable_pllctl0_reads",
            "open_cfw_host_syspll_disable_pllctl0_writes",
        ):
            getattr(cls.lib, name).restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def reset(self, prefix: int, module: int = 0,
              pllctl0: int = 0) -> None:
        self.lib.open_cfw_host_syspll_disable_reset(prefix, module, pllctl0)

    def test_invalid_handles_have_no_mmio_side_effects(self) -> None:
        self.reset(0xA1504C31, 0x12345678, 0xFFFFFFFF)
        self.assertEqual(
            self.lib.open_cfw_bootloader_row6_stop_4273dc(None), 2)
        self.assertEqual(self.lib.open_cfw_host_syspll_disable_call(), 2)
        self.assertEqual(self.lib.open_cfw_host_syspll_disable_pllctl0_reads(), 0)
        self.assertEqual(self.lib.open_cfw_host_syspll_disable_pllctl0_writes(), 0)

    def test_valid_handle_disables_pll_and_publishes_state(self) -> None:
        self.reset(0xA3504C30, 0x12345678, 0xF2345678)
        self.assertEqual(self.lib.open_cfw_host_syspll_disable_call(), 0)
        self.assertEqual(self.lib.open_cfw_host_syspll_disable_prefix(), 0xA1504C30)
        self.assertEqual(self.lib.open_cfw_host_syspll_disable_module(), 0x12345678)
        self.assertEqual(self.lib.open_cfw_host_syspll_disable_pllctl0(), 0xD2345678)
        self.assertEqual(self.lib.open_cfw_host_syspll_disable_pllctl0_reads(), 1)
        self.assertEqual(self.lib.open_cfw_host_syspll_disable_pllctl0_writes(), 1)

    def test_disable_preserves_all_unrelated_bits(self) -> None:
        self.reset(0xFF504C30, 0, 0x20000001)
        self.assertEqual(self.lib.open_cfw_host_syspll_disable_call(), 0)
        self.assertEqual(self.lib.open_cfw_host_syspll_disable_prefix(), 0xFD504C30)
        self.assertEqual(self.lib.open_cfw_host_syspll_disable_pllctl0(), 1)

    def test_valid_already_disabled_handle_still_performs_register_write(self) -> None:
        self.reset(0xA1504C30, 0, 0x12345678)
        self.assertEqual(self.lib.open_cfw_host_syspll_disable_call(), 0)
        self.assertEqual(self.lib.open_cfw_host_syspll_disable_pllctl0(), 0x12345678)
        self.assertEqual(self.lib.open_cfw_host_syspll_disable_pllctl0_reads(), 1)
        self.assertEqual(self.lib.open_cfw_host_syspll_disable_pllctl0_writes(), 1)

    def test_source_is_reviewable_c_with_authenticated_mmio(self) -> None:
        text = SOURCE.read_text()
        self.assertIn("am_hal_syspll_disable", text)
        self.assertIn("0x400204d8U", text)
        self.assertIn("1U << 29", text)
        self.assertNotIn("__asm", text)
        self.assertNotIn(".byte", text)


if __name__ == "__main__":
    unittest.main()
