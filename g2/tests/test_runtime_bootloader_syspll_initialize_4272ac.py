# SPDX-License-Identifier: MIT
from __future__ import annotations

import ctypes
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_syspll_initialize_4272ac.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_syspll_initialize_4272ac_host.c"


class SyspllInitializeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory()
        library = Path(cls.temp.name) / "syspll-initialize.so"
        subprocess.run(
            ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared",
             "-fPIC", str(FIXTURE), "-o", str(library)],
            cwd=ROOT, check=True,
        )
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.open_cfw_host_syspll_initialize_reset.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32,
        ]
        cls.lib.open_cfw_bootloader_row6_create_4272ac.argtypes = [
            ctypes.c_uint32, ctypes.POINTER(ctypes.c_void_p),
        ]
        cls.lib.open_cfw_bootloader_row6_create_4272ac.restype = ctypes.c_uint32
        for name in (
            "open_cfw_host_syspll_initialize_prefix",
            "open_cfw_host_syspll_initialize_module",
            "open_cfw_host_syspll_initialize_power_calls",
        ):
            getattr(cls.lib, name).restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def test_argument_rejections_have_no_side_effects(self) -> None:
        self.lib.open_cfw_host_syspll_initialize_reset(0xA2123456, 99)
        handle = ctypes.c_void_p()
        self.assertEqual(
            self.lib.open_cfw_bootloader_row6_create_4272ac(
                1, ctypes.byref(handle)), 5)
        self.assertEqual(
            self.lib.open_cfw_bootloader_row6_create_4272ac(0, None), 6)
        self.assertEqual(self.lib.open_cfw_host_syspll_initialize_prefix(),
                         0xA2123456)
        self.assertEqual(self.lib.open_cfw_host_syspll_initialize_module(), 99)
        self.assertEqual(
            self.lib.open_cfw_host_syspll_initialize_power_calls(), 0)

    def test_initialized_state_is_rejected(self) -> None:
        self.lib.open_cfw_host_syspll_initialize_reset(0xA1123456, 77)
        handle = ctypes.c_void_p()
        self.assertEqual(
            self.lib.open_cfw_bootloader_row6_create_4272ac(
                0, ctypes.byref(handle)), 7)
        self.assertFalse(handle.value)
        self.assertEqual(self.lib.open_cfw_host_syspll_initialize_prefix(),
                         0xA1123456)
        self.assertEqual(
            self.lib.open_cfw_host_syspll_initialize_power_calls(), 0)

    def test_success_preserves_high_flags_sets_magic_and_powers_pll(self) -> None:
        self.lib.open_cfw_host_syspll_initialize_reset(0xA2123456, 77)
        handle = ctypes.c_void_p()
        self.assertEqual(
            self.lib.open_cfw_bootloader_row6_create_4272ac(
                0, ctypes.byref(handle)), 0)
        self.assertTrue(handle.value)
        self.assertEqual(self.lib.open_cfw_host_syspll_initialize_prefix(),
                         0xA3504C30)
        self.assertEqual(self.lib.open_cfw_host_syspll_initialize_module(), 0)
        self.assertEqual(
            self.lib.open_cfw_host_syspll_initialize_power_calls(), 1)

    def test_source_is_reviewable_c_with_authenticated_addresses(self) -> None:
        text = SOURCE.read_text()
        self.assertIn("am_hal_syspll_initialize", text)
        self.assertIn("0x20027010U", text)
        self.assertIn("open_cfw_bootloader_pwrctrl_syspll_enable_41ca5c", text)
        self.assertNotIn("__asm", text)
        self.assertNotIn(".byte", text)


if __name__ == "__main__":
    unittest.main()
