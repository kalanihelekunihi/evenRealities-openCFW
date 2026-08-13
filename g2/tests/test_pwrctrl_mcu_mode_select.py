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
SOURCE = COMPONENT_ROOT / "pwrctrl_mcu_mode_select.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "pwrctrl_mcu_mode_select_host.c"
)


class PwrctrlMcuModeSelectTests(unittest.TestCase):
    READ_VR_STATUS = 1
    READ_CURRENT_MODE = 2
    SWITCH = 3
    READ_PERFORMANCE = 4

    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "pwrctrl_mcu_mode_select.dylib"
            if sys.platform == "darwin"
            else "pwrctrl_mcu_mode_select.so"
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
        cls.reset_fixture = cls.loaded.open_cfw_test_mcu_select_reset
        cls.reset_fixture.argtypes = []
        cls.reset_fixture.restype = None
        cls.select = cls.loaded.open_cfw_pwrctrl_mcu_mode_select
        cls.select.argtypes = [ctypes.c_uint]
        cls.select.restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset_fixture()

    @classmethod
    def word(cls, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_mcu_select_{name}",
        )

    def trace(self) -> list[tuple[int, int]]:
        count = self.word("trace_count").value
        events = (ctypes.c_uint * 8).in_dll(
            self.loaded,
            "open_cfw_test_mcu_select_trace_event",
        )
        values = (ctypes.c_uint * 8).in_dll(
            self.loaded,
            "open_cfw_test_mcu_select_trace_value",
        )
        return [(events[index], values[index]) for index in range(count)]

    def test_invalid_low_byte_returns_six_without_side_effects(self) -> None:
        for requested_mode in (0, 3, 0xFF, 0x100, 0xABCDEF03):
            with self.subTest(requested_mode=requested_mode):
                self.reset_fixture()
                self.assertEqual(self.select(requested_mode), 6)
                self.assertEqual(self.trace(), [])

    def test_high_bits_are_truncated_before_hp_processing(self) -> None:
        self.word("current_mode").value = 1
        self.word("performance").value = 2 << 3

        result = self.select(0xA5A50102)

        self.assertEqual(result, 0)
        self.assertEqual(self.word("switch_mode").value, 2)
        self.assertEqual(
            self.trace(),
            [
                (self.READ_VR_STATUS, 0x30),
                (self.READ_CURRENT_MODE, 1),
                (self.SWITCH, 2),
                (self.READ_PERFORMANCE, 2 << 3),
            ],
        )

    def test_hp_requires_active_simobuck(self) -> None:
        for simobuck_state in (0, 1, 2):
            with self.subTest(simobuck_state=simobuck_state):
                self.reset_fixture()
                register_value = 0xA5A50000 | (simobuck_state << 4)
                self.word("vr_status").value = register_value

                self.assertEqual(self.select(2), 7)
                self.assertEqual(
                    self.trace(),
                    [(self.READ_VR_STATUS, register_value)],
                )

    def test_hp_already_selected_returns_success_after_vr_check(self) -> None:
        self.word("vr_status").value = 0x5A5A003F
        self.word("current_mode").value = 2

        self.assertEqual(self.select(2), 0)
        self.assertEqual(
            self.trace(),
            [
                (self.READ_VR_STATUS, 0x5A5A003F),
                (self.READ_CURRENT_MODE, 2),
            ],
        )

    def test_lp_already_selected_skips_vr_and_switch(self) -> None:
        self.word("current_mode").value = 1

        self.assertEqual(self.select(1), 0)
        self.assertEqual(
            self.trace(),
            [(self.READ_CURRENT_MODE, 1)],
        )

    def test_switch_error_is_propagated_without_status_read(self) -> None:
        self.word("current_mode").value = 2
        self.word("switch_status").value = 0xDEADBEEF

        self.assertEqual(self.select(1), 0xDEADBEEF)
        self.assertEqual(
            self.trace(),
            [
                (self.READ_CURRENT_MODE, 2),
                (self.SWITCH, 1),
            ],
        )

    def test_success_requires_matching_performance_status(self) -> None:
        self.word("current_mode").value = 1
        self.word("performance").value = 0xA5A50010

        self.assertEqual(self.select(2), 0)
        self.assertEqual(self.word("performance_reads").value, 1)

    def test_mismatched_performance_status_returns_failure(self) -> None:
        self.word("current_mode").value = 2
        self.word("performance").value = 0x5A5A0010

        self.assertEqual(self.select(1), 1)
        self.assertEqual(
            self.trace(),
            [
                (self.READ_CURRENT_MODE, 2),
                (self.SWITCH, 1),
                (self.READ_PERFORMANCE, 0x5A5A0010),
            ],
        )

    def test_randomized_stock_model(self) -> None:
        randomizer = random.Random(0x47F0A0)

        for _ in range(1000):
            self.reset_fixture()
            requested_mode = randomizer.randrange(0, 1 << 32)
            power_mode = requested_mode & 0xFF
            vr_status = randomizer.randrange(0, 1 << 32)
            current_mode = randomizer.randrange(0, 256)
            switch_status = randomizer.randrange(0, 10)
            performance = randomizer.randrange(0, 1 << 32)
            self.word("vr_status").value = vr_status
            self.word("current_mode").value = current_mode
            self.word("switch_status").value = switch_status
            self.word("performance").value = performance

            if power_mode not in (1, 2):
                expected = 6
            elif power_mode == 2 and ((vr_status >> 4) & 3) != 3:
                expected = 7
            elif power_mode == current_mode:
                expected = 0
            elif switch_status != 0:
                expected = switch_status
            elif ((performance >> 3) & 3) == power_mode:
                expected = 0
            else:
                expected = 1

            self.assertEqual(self.select(requested_mode), expected)

    def test_sources_are_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "50e34490d093998755d2fa758be0d89d46a0d93fc2ca5abeceaaeb5851138ba2",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "5facc2fb6c3aba496c7fda3472bf0fbdfd93b5eb048fb474b5f1f52d014df9c9",
        )


if __name__ == "__main__":
    unittest.main()
