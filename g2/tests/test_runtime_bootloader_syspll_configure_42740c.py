# SPDX-License-Identifier: MIT
from __future__ import annotations

import ctypes
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_syspll_configure_42740c.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_syspll_configure_42740c_host.c"


class SyspllConfigureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory()
        library = Path(cls.temp.name) / "syspll-configure.so"
        subprocess.run(
            ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared",
             "-fPIC", str(FIXTURE), "-o", str(library)],
            cwd=ROOT, check=True,
        )
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.open_cfw_host_syspll_configure_reset.argtypes = [
            ctypes.c_uint32,
        ] * 13
        cls.lib.open_cfw_bootloader_row6_configure_42740c.argtypes = [
            ctypes.c_void_p, ctypes.c_void_p,
        ]
        cls.lib.open_cfw_bootloader_row6_configure_42740c.restype = ctypes.c_uint32
        for name in (
            "open_cfw_host_syspll_configure_call",
            "open_cfw_host_syspll_configure_pllctl0",
            "open_cfw_host_syspll_configure_plldiv0",
            "open_cfw_host_syspll_configure_plldiv1",
            "open_cfw_host_syspll_configure_pllctl0_reads",
            "open_cfw_host_syspll_configure_pllctl0_writes",
            "open_cfw_host_syspll_configure_plldiv0_reads",
            "open_cfw_host_syspll_configure_plldiv0_writes",
            "open_cfw_host_syspll_configure_plldiv1_reads",
            "open_cfw_host_syspll_configure_plldiv1_writes",
            "open_cfw_host_syspll_configure_fref_calls",
            "open_cfw_host_syspll_configure_fref_value",
        ):
            getattr(cls.lib, name).restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def reset(self, *, prefix: int = 0xA1504C30, module: int = 0,
              fref: int = 0, vco: int = 0, mode: int = 0, refdiv: int = 2,
              post1: int = 3, post2: int = 2, fbint: int = 13,
              fbfrac: int = 0x123456, pllctl0: int = 0xA5A5A5A5,
              plldiv0: int = 0xFF000000, plldiv1: int = 0xF0008000) -> None:
        self.lib.open_cfw_host_syspll_configure_reset(
            prefix, module, fref, vco, mode, refdiv, post1, post2,
            fbint, fbfrac, pllctl0, plldiv0, plldiv1,
        )

    def assert_no_hardware_actions(self) -> None:
        for suffix in (
            "pllctl0_reads", "pllctl0_writes", "plldiv0_reads",
            "plldiv0_writes", "plldiv1_reads", "plldiv1_writes",
            "fref_calls",
        ):
            self.assertEqual(
                getattr(self.lib, "open_cfw_host_syspll_configure_" + suffix)(),
                0,
            )

    def test_invalid_handle_and_enabled_state_fail_before_hardware(self) -> None:
        self.reset(prefix=0xA1504C31)
        self.assertEqual(self.lib.open_cfw_host_syspll_configure_call(), 2)
        self.assertEqual(
            self.lib.open_cfw_bootloader_row6_configure_42740c(None, None), 2)
        self.assert_no_hardware_actions()
        self.reset(prefix=0xA3504C30)
        self.assertEqual(self.lib.open_cfw_host_syspll_configure_call(), 7)
        self.assert_no_hardware_actions()

    def test_all_argument_range_failures_precede_hardware(self) -> None:
        invalid = (
            {"refdiv": 64},
            {"mode": 1, "fbint": 3},
            {"mode": 1, "fbint": 961},
            {"mode": 0, "fbint": 9},
            {"mode": 0, "fbint": 97},
            {"post1": 8},
            {"post2": 8},
            {"post1": 2, "post2": 3},
        )
        for values in invalid:
            with self.subTest(values=values):
                self.reset(**values)
                self.assertEqual(self.lib.open_cfw_host_syspll_configure_call(), 6)
                self.assert_no_hardware_actions()

    def test_valid_configuration_programs_all_fields_and_output_policy(self) -> None:
        initial_ctl = 0xA5A5A5A5
        initial_div1 = 0xF0008000
        self.reset(fref=1, vco=1, mode=0, refdiv=5, post1=6, post2=2,
                   fbint=42, fbfrac=0x123456, pllctl0=initial_ctl,
                   plldiv1=initial_div1)
        self.assertEqual(self.lib.open_cfw_host_syspll_configure_call(), 0)
        expected_ctl = initial_ctl
        expected_ctl = (expected_ctl & ~(1 << 9)) | (1 << 9)
        expected_ctl = (expected_ctl & ~(1 << 5)) | (1 << 5)
        expected_ctl &= ~(1 << 3)
        expected_ctl &= ~(1 << 4)
        expected_ctl |= 1
        expected_ctl &= ~6
        self.assertEqual(self.lib.open_cfw_host_syspll_configure_pllctl0(),
                         expected_ctl)
        self.assertEqual(self.lib.open_cfw_host_syspll_configure_plldiv0(),
                         0xFF123456)
        expected_div1 = initial_div1
        expected_div1 = (expected_div1 & ~(0xFFF << 16)) | (42 << 16)
        expected_div1 = (expected_div1 & ~0x3F) | 5
        expected_div1 = (expected_div1 & ~(7 << 12)) | (6 << 12)
        expected_div1 = (expected_div1 & ~(7 << 8)) | (2 << 8)
        self.assertEqual(self.lib.open_cfw_host_syspll_configure_plldiv1(),
                         expected_div1)
        self.assertEqual(self.lib.open_cfw_host_syspll_configure_pllctl0_reads(), 7)
        self.assertEqual(self.lib.open_cfw_host_syspll_configure_pllctl0_writes(), 7)
        self.assertEqual(self.lib.open_cfw_host_syspll_configure_plldiv0_reads(), 1)
        self.assertEqual(self.lib.open_cfw_host_syspll_configure_plldiv0_writes(), 1)
        self.assertEqual(self.lib.open_cfw_host_syspll_configure_plldiv1_reads(), 4)
        self.assertEqual(self.lib.open_cfw_host_syspll_configure_plldiv1_writes(), 4)
        self.assertEqual(self.lib.open_cfw_host_syspll_configure_fref_calls(), 1)
        self.assertEqual(self.lib.open_cfw_host_syspll_configure_fref_value(), 1)

    def test_integer_and_fraction_feedback_boundaries_are_inclusive(self) -> None:
        for mode, feedback in ((1, 4), (1, 960), (0, 10), (0, 96)):
            with self.subTest(mode=mode, feedback=feedback):
                self.reset(mode=mode, fbint=feedback)
                self.assertEqual(self.lib.open_cfw_host_syspll_configure_call(), 0)

    def test_source_is_reviewable_c_with_authenticated_register_contract(self) -> None:
        text = SOURCE.read_text()
        for token in (
            "am_hal_syspll_configure", "0x400204d8U", "0x400204dcU",
            "0x400204e0U", "feedback < 4U", "feedback > 960U",
            "feedback < 10U", "feedback > 96U",
            "open_cfw_bootloader_sysctrl_pll_fref_update_41ac92",
        ):
            self.assertIn(token, text)
        self.assertNotIn("__asm", text)
        self.assertNotIn(".byte", text)


if __name__ == "__main__":
    unittest.main()
