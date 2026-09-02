# SPDX-License-Identifier: MIT
from __future__ import annotations

import ctypes
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_syspll_lock_wait_427522.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_syspll_lock_wait_427522_host.c"


class SyspllLockWaitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory()
        library = Path(cls.temp.name) / "syspll-lock-wait.so"
        subprocess.run(
            ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared",
             "-fPIC", str(FIXTURE), "-o", str(library)],
            cwd=ROOT, check=True,
        )
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.open_cfw_host_syspll_lock_wait_reset.argtypes = [
            ctypes.c_uint32,
        ] * 6
        cls.lib.open_cfw_bootloader_row6_lock_wait_427522.argtypes = [
            ctypes.c_void_p,
        ]
        cls.lib.open_cfw_bootloader_row6_lock_wait_427522.restype = ctypes.c_uint32
        for suffix in (
            "call", "pllctl0_reads", "plldiv1_reads", "status_calls",
            "order", "timeout", "address", "mask", "expected", "equality",
        ):
            getattr(cls.lib, "open_cfw_host_syspll_lock_wait_" + suffix).restype = (
                ctypes.c_uint32
            )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def reset(self, *, prefix: int = 0xA1504C30, module: int = 0,
              first: int = 0, refdiv: int = 1,
              second: int = 1 << 29, status: int = 0) -> None:
        self.lib.open_cfw_host_syspll_lock_wait_reset(
            prefix, module, first, refdiv, second, status,
        )

    def test_invalid_handles_fail_before_mmio(self) -> None:
        self.reset(prefix=0xA1504C31)
        self.assertEqual(self.lib.open_cfw_host_syspll_lock_wait_call(), 2)
        self.assertEqual(
            self.lib.open_cfw_bootloader_row6_lock_wait_427522(None), 2)
        self.assertEqual(self.lib.open_cfw_host_syspll_lock_wait_order(), 0)
        self.assertEqual(self.lib.open_cfw_host_syspll_lock_wait_status_calls(), 0)

    def test_disabled_pll_preserves_read_order_and_avoids_polling(self) -> None:
        self.reset(first=1 << 9, refdiv=23, second=0)
        self.assertEqual(self.lib.open_cfw_host_syspll_lock_wait_call(), 7)
        self.assertEqual(self.lib.open_cfw_host_syspll_lock_wait_order(), 121)
        self.assertEqual(self.lib.open_cfw_host_syspll_lock_wait_pllctl0_reads(), 2)
        self.assertEqual(self.lib.open_cfw_host_syspll_lock_wait_plldiv1_reads(), 1)
        self.assertEqual(self.lib.open_cfw_host_syspll_lock_wait_status_calls(), 0)

    def test_low_vco_timeout_boundaries_and_provider_contract(self) -> None:
        for refdiv, timeout in ((0, 0), (63, 5250)):
            with self.subTest(refdiv=refdiv):
                self.reset(refdiv=refdiv, status=11)
                self.assertEqual(self.lib.open_cfw_host_syspll_lock_wait_call(), 11)
                self.assertEqual(self.lib.open_cfw_host_syspll_lock_wait_order(), 1213)
                self.assertEqual(
                    self.lib.open_cfw_host_syspll_lock_wait_timeout(), timeout)
                self.assertEqual(
                    self.lib.open_cfw_host_syspll_lock_wait_address(), 0x400204E4)
                self.assertEqual(self.lib.open_cfw_host_syspll_lock_wait_mask(), 1)
                self.assertEqual(self.lib.open_cfw_host_syspll_lock_wait_expected(), 1)
                self.assertEqual(self.lib.open_cfw_host_syspll_lock_wait_equality(), 1)

    def test_high_vco_uses_1875_cycle_timeout_and_propagates_status(self) -> None:
        self.reset(first=1 << 9, refdiv=63, status=0xA5)
        self.assertEqual(self.lib.open_cfw_host_syspll_lock_wait_call(), 0xA5)
        self.assertEqual(self.lib.open_cfw_host_syspll_lock_wait_timeout(), 9844)

    def test_source_is_reviewable_c_with_authenticated_contract(self) -> None:
        text = SOURCE.read_text()
        for token in (
            "am_hal_syspll_lock_wait", "0x400204d8U", "0x400204e0U",
            "0x400204e4U", "OPEN_CFW_SYSPLL_LOCK_WAIT_VCO_LOW_CYCLES 1000U",
            "OPEN_CFW_SYSPLL_LOCK_WAIT_VCO_HIGH_CYCLES 1875U",
            "open_cfw_bootloader_delay_us_status_check_41d246",
        ):
            self.assertIn(token, text)
        self.assertNotIn("__asm", text)
        self.assertNotIn(".byte", text)


if __name__ == "__main__":
    unittest.main()
