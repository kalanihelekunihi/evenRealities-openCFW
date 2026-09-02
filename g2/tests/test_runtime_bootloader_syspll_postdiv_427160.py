# SPDX-License-Identifier: MIT
from __future__ import annotations

import ctypes
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/bootloader_syspll_postdiv_427160_host.c"


class Config(ctypes.Structure):
    _fields_ = [
        ("reference_select", ctypes.c_uint8),
        ("vco_select", ctypes.c_uint8),
        ("fraction_mode", ctypes.c_uint8),
        ("reference_divider", ctypes.c_uint8),
        ("post_divider_1", ctypes.c_uint8),
        ("post_divider_2", ctypes.c_uint8),
        ("feedback_divider_integer", ctypes.c_uint16),
        ("feedback_divider_fraction", ctypes.c_uint32),
    ]


class SyspllPostdivTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory()
        library = Path(cls.temp.name) / "syspll-postdiv.so"
        subprocess.run(
            ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared",
             "-fPIC", str(FIXTURE), "-o", str(library)],
            cwd=ROOT, check=True,
        )
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.open_cfw_host_syspll_postdiv_set_candidates.argtypes = [
            ctypes.POINTER(Config), ctypes.c_uint32,
            ctypes.POINTER(Config), ctypes.c_uint32,
        ]
        cls.lib.open_cfw_bootloader_syspll_postdiv_427160.argtypes = [
            ctypes.POINTER(Config), ctypes.c_uint32, ctypes.c_uint32,
        ]
        cls.lib.open_cfw_bootloader_syspll_postdiv_427160.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def configure(self, low: Config, low_status: int,
                  high: Config, high_status: int) -> Config:
        self.lib.open_cfw_host_syspll_postdiv_set_candidates(
            ctypes.byref(low), low_status, ctypes.byref(high), high_status)
        output = Config(reference_select=9)
        status = self.lib.open_cfw_bootloader_syspll_postdiv_427160(
            ctypes.byref(output), 32_000_000, 12_000_000)
        self.assertEqual(status, 0)
        self.assertEqual(output.reference_select, 9)
        return output

    def test_only_valid_candidate_is_published_without_reference_select(self) -> None:
        low = Config(vco_select=0, fraction_mode=1, reference_divider=2,
                     post_divider_1=2, post_divider_2=3,
                     feedback_divider_integer=7,
                     feedback_divider_fraction=123)
        high = Config(vco_select=1, fraction_mode=0, reference_divider=4,
                      post_divider_1=4, post_divider_2=5,
                      feedback_divider_integer=11,
                      feedback_divider_fraction=456)
        output = self.configure(low, 5, high, 0)
        self.assertEqual(bytes(output)[1:], bytes(high)[1:])

    def test_lower_points_candidate_wins_and_ties_choose_high(self) -> None:
        low = Config(vco_select=0, fraction_mode=1, reference_divider=2,
                     post_divider_1=1, post_divider_2=1,
                     feedback_divider_integer=7)
        high = Config(vco_select=1, fraction_mode=1, reference_divider=1,
                      post_divider_1=8, post_divider_2=8,
                      feedback_divider_integer=11)
        output = self.configure(low, 0, high, 0)
        self.assertEqual(output.feedback_divider_integer, 7)

        same = Config(vco_select=0, fraction_mode=1, reference_divider=2,
                      post_divider_1=1, post_divider_2=1,
                      feedback_divider_integer=13)
        output = self.configure(low, 0, same, 0)
        self.assertEqual(output.feedback_divider_integer, 13)

    def test_no_valid_candidate_reports_out_of_range(self) -> None:
        low = Config()
        high = Config()
        self.lib.open_cfw_host_syspll_postdiv_set_candidates(
            ctypes.byref(low), 5, ctypes.byref(high), 5)
        output = Config(reference_select=7)
        self.assertEqual(
            self.lib.open_cfw_bootloader_syspll_postdiv_427160(
                ctypes.byref(output), 32_000_000, 12_000_000),
            5,
        )
        self.assertEqual(output.reference_select, 7)


if __name__ == "__main__":
    unittest.main()
