from __future__ import annotations

import os

import ctypes
import hashlib
import random
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


OPENCFW_ROOT = Path(__file__).resolve().parent.parent
COMPONENT_ROOT = OPENCFW_ROOT / "components" / "apollo_main" / "core_overlay"
SOURCE = COMPONENT_ROOT / "pwrctrl_syspll_enabled.c"
FIXTURE = (
    OPENCFW_ROOT / "tests" / "fixtures" / "pwrctrl_syspll_enabled_host.c"
)

PLLCTL0 = 0x400204D8
VDDF_POWER_DOWN = 0x80000000
UINT_MASK = 0xFFFFFFFF


class PwrctrlSyspllEnabledTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "pwrctrl_syspll_enabled.dylib"
            if sys.platform == "darwin"
            else "pwrctrl_syspll_enabled.so"
        )
        command = [
            os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            str(FIXTURE),
        ]
        if sys.platform == "darwin":
            command.extend(["-dynamiclib", "-o", str(library)])
        else:
            command.extend(["-shared", "-fPIC", "-o", str(library)])
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.loaded = ctypes.CDLL(str(library))
        cls.reset_fixture = cls.loaded.open_cfw_test_syspll_enabled_reset
        cls.reset_fixture.argtypes = [ctypes.c_uint, ctypes.c_uint]
        cls.reset_fixture.restype = None
        cls.query = cls.loaded.open_cfw_test_syspll_enabled_call
        cls.query.argtypes = []
        cls.query.restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @classmethod
    def word(cls, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_syspll_enabled_{name}",
        )

    def reset(self, pllctl0: int, output: int = 0xA5A5A5A5) -> None:
        self.reset_fixture(pllctl0, output)

    def test_clear_power_down_bit_reports_enabled(self) -> None:
        self.reset(0)

        self.assertEqual(self.query(), 0)
        self.assertEqual(self.word("output").value, 0xA5A5A501)

    def test_set_power_down_bit_reports_disabled(self) -> None:
        self.reset(VDDF_POWER_DOWN)

        self.assertEqual(self.query(), 0)
        self.assertEqual(self.word("output").value, 0xA5A5A500)

    def test_unrelated_pll_control_bits_do_not_affect_result(self) -> None:
        for pllctl0, expected in (
            (0x7FFFFFFF, 1),
            (0xFFFFFFFF, 0),
            (0x40000000, 1),
            (0xC0000000, 0),
        ):
            with self.subTest(pllctl0=pllctl0):
                self.reset(pllctl0, 0x5A5A5A7E)
                self.assertEqual(self.query(), 0)
                self.assertEqual(
                    self.word("output").value,
                    0x5A5A5A00 | expected,
                )

    def test_query_performs_exactly_one_reviewed_register_read(self) -> None:
        self.reset(0x12345678)

        self.assertEqual(self.query(), 0)
        self.assertEqual(self.word("read_count").value, 1)
        self.assertEqual(self.word("read_address").value, PLLCTL0)

    def test_only_the_boolean_output_byte_is_written(self) -> None:
        for initial in (0x000000FF, 0x12345678, UINT_MASK):
            with self.subTest(initial=initial):
                self.reset(0, initial)
                self.assertEqual(self.query(), 0)
                self.assertEqual(
                    self.word("output").value,
                    (initial & 0xFFFFFF00) | 1,
                )

    def test_randomized_stock_model(self) -> None:
        generator = random.Random(0x004800E4)

        for _ in range(1000):
            pllctl0 = generator.getrandbits(32)
            initial = generator.getrandbits(32)
            self.reset(pllctl0, initial)

            self.assertEqual(self.query(), 0)
            self.assertEqual(
                self.word("output").value,
                (
                    initial & 0xFFFFFF00
                ) | int((pllctl0 & VDDF_POWER_DOWN) == 0),
            )
            self.assertEqual(self.word("read_count").value, 1)
            self.assertEqual(self.word("read_address").value, PLLCTL0)

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "4314220e737db6abead0dbd9f1d71079d4ff5375300bd8ea7f272e442672c9e1",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "81be2135f3861dd62c9d53137302ca42ba1421b107e02a70bbfc65baff796ee8",
        )


if __name__ == "__main__":
    unittest.main()
