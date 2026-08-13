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
SOURCE = COMPONENT_ROOT / "spotmgr_timer_init.c"
FIXTURE = OPENCFW_ROOT / "tests" / "fixtures" / "spotmgr_timer_init_host.c"

READ = 1
WRITE = 2
CTRL0 = 0x400083E0
COMPARE0 = 0x400083E8
COMPARE1 = 0x400083EC
MODE0 = 0x400083F0
INTEN = 0x40008060
INTCLR = 0x40008068
UINT_MASK = 0xFFFFFFFF


def expected_events(ctrl0: int, inten: int) -> list[tuple[int, int, int]]:
    return [
        (READ, CTRL0, ctrl0),
        (WRITE, CTRL0, ctrl0 & ~1),
        (WRITE, CTRL0, 0x110),
        (WRITE, MODE0, 0x100),
        (WRITE, COMPARE0, UINT_MASK),
        (WRITE, COMPARE1, UINT_MASK),
        (WRITE, INTCLR, 0xC0000000),
        (READ, INTEN, inten),
        (WRITE, INTEN, inten | 0x40000000),
    ]


class SpotmgrTimerInitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "spotmgr_timer_init.dylib"
            if sys.platform == "darwin"
            else "spotmgr_timer_init.so"
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
        cls.reset_fixture = cls.loaded.open_cfw_test_spotmgr_timer_reset
        cls.reset_fixture.argtypes = [
            ctypes.c_uint,
            ctypes.c_uint,
            ctypes.c_uint,
        ]
        cls.reset_fixture.restype = None
        cls.initialize = cls.loaded.open_cfw_spotmgr_timer_init
        cls.initialize.argtypes = []
        cls.initialize.restype = None

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @classmethod
    def word(cls, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_spotmgr_timer_{name}",
        )

    @classmethod
    def words(cls, name: str) -> ctypes.Array:
        return (ctypes.c_uint * 9).in_dll(
            cls.loaded,
            f"open_cfw_test_spotmgr_timer_{name}",
        )

    def run_case(
        self,
        ctrl0: int,
        inten: int,
        sentinel: int = 0xA5A55A5A,
    ) -> list[tuple[int, int, int]]:
        self.reset_fixture(ctrl0, inten, sentinel)
        self.initialize()
        return list(
            zip(
                self.words("event_kinds"),
                self.words("event_addresses"),
                self.words("event_values"),
            )
        )

    def test_exact_stock_register_transaction_order(self) -> None:
        ctrl0 = 0x12345679
        inten = 0x01020304

        self.assertEqual(
            self.run_case(ctrl0, inten),
            expected_events(ctrl0, inten),
        )
        self.assertEqual(self.word("event_count").value, 9)

    def test_final_timer_configuration_matches_stock(self) -> None:
        self.run_case(UINT_MASK, 0)

        self.assertEqual(self.word("ctrl0").value, 0x110)
        self.assertEqual(self.word("mode0").value, 0x100)
        self.assertEqual(self.word("compare0").value, UINT_MASK)
        self.assertEqual(self.word("compare1").value, UINT_MASK)
        self.assertEqual(self.word("intclr").value, 0xC0000000)
        self.assertEqual(self.word("inten").value, 0x40000000)

    def test_existing_interrupt_enables_are_preserved(self) -> None:
        self.run_case(0, 0xBFFFFFFF)

        self.assertEqual(self.word("inten").value, UINT_MASK)

    def test_disable_write_is_not_elided_before_full_configuration(self) -> None:
        events = self.run_case(0xFFFFFFFF, 0)

        self.assertEqual(events[0:3], [
            (READ, CTRL0, UINT_MASK),
            (WRITE, CTRL0, 0xFFFFFFFE),
            (WRITE, CTRL0, 0x110),
        ])

    def test_randomized_stock_model(self) -> None:
        generator = random.Random(0x004801FC)

        for _ in range(1000):
            ctrl0 = generator.getrandbits(32)
            inten = generator.getrandbits(32)
            self.assertEqual(
                self.run_case(ctrl0, inten),
                expected_events(ctrl0, inten),
            )

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "fec2157ada5d579e7a93314b6a6869631"
            "fcc43950ce32c99953670b381eb6f97",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "749860a89c5f2cf549ef9ba6ea924d1c"
            "240ccdd3b782f3f1d84c2fa627dc4e93",
        )


if __name__ == "__main__":
    unittest.main()
