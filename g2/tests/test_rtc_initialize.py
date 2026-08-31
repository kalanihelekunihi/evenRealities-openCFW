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
SOURCE = COMPONENT_ROOT / "rtc_initialize.c"
FIXTURE = OPENCFW_ROOT / "tests" / "fixtures" / "rtc_initialize_host.c"
UINT_MASK = (1 << 32) - 1
CLKGEN_OCTRL = 0x4000400C
RTC_CONTROL = 0x40004800


class RtcInitializeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "rtc_initialize.dylib"
            if sys.platform == "darwin"
            else "rtc_initialize.so"
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
        cls.reset_fixture = cls.loaded.open_cfw_test_rtc_reset
        cls.reset_fixture.argtypes = []
        cls.reset_fixture.restype = None
        cls.initialize = cls.loaded.open_cfw_rtc_initialize
        cls.initialize.argtypes = []
        cls.initialize.restype = ctypes.c_uint
        cls.event_kind = (
            ctypes.c_uint * 16
        ).in_dll(cls.loaded, "open_cfw_test_rtc_event_kind")
        cls.event_address = (
            ctypes.c_uint * 16
        ).in_dll(cls.loaded, "open_cfw_test_rtc_event_address")
        cls.event_value = (
            ctypes.c_uint * 16
        ).in_dll(cls.loaded, "open_cfw_test_rtc_event_value")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset_fixture()

    @classmethod
    def word(cls, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_rtc_{name}",
        )

    def events(self) -> list[tuple[int, int, int]]:
        count = self.word("event_count").value
        return [
            (
                self.event_kind[index],
                self.event_address[index],
                self.event_value[index],
            )
            for index in range(count)
        ]

    def test_exact_read_modify_write_order_and_return(self) -> None:
        self.word("clock_control").value = 0xFFFFFFFF
        self.word("control").value = 0xA5A5A5A5
        self.assertEqual(self.initialize(), 0)
        self.assertEqual(
            self.events(),
            [
                (1, CLKGEN_OCTRL, 0xFFFFFFFF),
                (2, CLKGEN_OCTRL, 0xFFFFFF7F),
                (1, CLKGEN_OCTRL, 0xFFFFFF7F),
                (2, CLKGEN_OCTRL, 0xFFFFFF7F),
                (1, RTC_CONTROL, 0xA5A5A5A5),
                (2, RTC_CONTROL, 0xA5A5A5A5 & ~0x10),
            ],
        )

    def test_preserves_every_non_control_bit(self) -> None:
        generator = random.Random(0x0047EE60)
        for _ in range(500):
            clock = generator.getrandbits(32)
            rtc = generator.getrandbits(32)
            self.reset_fixture()
            self.word("clock_control").value = clock
            self.word("control").value = rtc
            self.assertEqual(self.initialize(), 0)
            self.assertEqual(
                self.word("clock_control").value,
                clock & ~0x80 & UINT_MASK,
            )
            self.assertEqual(
                self.word("control").value,
                rtc & ~0x10 & UINT_MASK,
            )

    def test_already_selected_and_running_state_is_still_rewritten(self) -> None:
        self.word("clock_control").value = 0x12345600
        self.word("control").value = 0xABCDEF00
        self.assertEqual(self.initialize(), 0)
        self.assertEqual(self.word("event_count").value, 6)
        self.assertEqual(self.initialize(), 0)
        self.assertEqual(self.word("event_count").value, 12)

    def test_zero_and_full_register_edges_return_zero(self) -> None:
        for clock, rtc in ((0, 0), (UINT_MASK, UINT_MASK)):
            with self.subTest(clock=clock, rtc=rtc):
                self.reset_fixture()
                self.word("clock_control").value = clock
                self.word("control").value = rtc
                self.assertEqual(self.initialize(), 0)

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "1f1d2c8399d3d4929295f9849bb663ccd672566311a718afe8a389e1017560d8",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "b4a0682a2cf44673847c1677dddd17ab2c4638b95572b3b38787bc597b2dbb09",
        )


if __name__ == "__main__":
    unittest.main()
