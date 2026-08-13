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
SOURCE = COMPONENT_ROOT / "pwrctrl_gpu_mode_select.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "pwrctrl_gpu_mode_select_host.c"
)


class PwrctrlGpuModeSelectTests(unittest.TestCase):
    READ_VR = 1
    PERIPH = 2
    READ_CURRENT = 3
    READ_PREVIOUS = 4
    WRITE_PREVIOUS = 5
    IRQ_DISABLE = 6
    TON = 7
    READ_POWER = 8
    WRITE_POWER = 9
    DELAY = 10
    READ_PERFORMANCE = 11
    WRITE_PERFORMANCE = 12
    WRITE_CURRENT = 13
    IRQ_RESTORE = 14

    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "pwrctrl_gpu_mode_select.dylib"
            if sys.platform == "darwin"
            else "pwrctrl_gpu_mode_select.so"
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
        cls.reset_fixture = cls.loaded.open_cfw_test_gpu_select_reset
        cls.reset_fixture.argtypes = []
        cls.reset_fixture.restype = None
        cls.select = cls.loaded.open_cfw_pwrctrl_gpu_mode_select
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
            f"open_cfw_test_gpu_select_{name}",
        )

    def trace(self) -> list[tuple[int, int]]:
        count = self.word("trace_count").value
        events = (ctypes.c_uint * 32).in_dll(
            self.loaded,
            "open_cfw_test_gpu_select_trace_event",
        )
        values = (ctypes.c_uint * 32).in_dll(
            self.loaded,
            "open_cfw_test_gpu_select_trace_value",
        )
        return [(events[index], values[index]) for index in range(count)]

    def test_invalid_low_byte_returns_six_without_side_effects(self) -> None:
        for requested_mode in (1, 2, 4, 0xFF, 0xABCDEF02):
            with self.subTest(requested_mode=requested_mode):
                self.reset_fixture()

                self.assertEqual(self.select(requested_mode), 6)
                self.assertEqual(self.trace(), [])

    def test_high_bits_are_truncated_before_hp_processing(self) -> None:
        self.word("current_mode").value = 3
        self.word("previous_mode").value = 3

        result = self.select(0xA5A50103)

        self.assertEqual(result, 0)
        self.assertEqual(
            self.trace(),
            [
                (self.READ_VR, 0x30),
                (self.PERIPH, 20),
                (self.READ_CURRENT, 3),
                (self.READ_PREVIOUS, 3),
                (self.READ_CURRENT, 3),
            ],
        )

    def test_hp_requires_active_simobuck(self) -> None:
        for simobuck_state in (0, 1, 2):
            with self.subTest(simobuck_state=simobuck_state):
                self.reset_fixture()
                register_value = 0xA5A50000 | (simobuck_state << 4)
                self.word("vr_status").value = register_value

                self.assertEqual(self.select(3), 7)
                self.assertEqual(
                    self.trace(),
                    [(self.READ_VR, register_value)],
                )

    def test_peripheral_query_failure_is_normalized_to_one(self) -> None:
        for status in (1, 2, 0xDEADBEEF):
            with self.subTest(status=status):
                self.reset_fixture()
                self.word("periph_status").value = status

                self.assertEqual(self.select(0), 1)
                self.assertEqual(self.word("periph_calls").value, 1)
                self.assertEqual(self.word("periph_id").value, 20)
                self.assertEqual(self.trace(), [(self.PERIPH, 20)])

    def test_enabled_graphics_returns_in_use(self) -> None:
        self.word("graphics_enabled").value = 0x101

        self.assertEqual(self.select(0), 3)
        self.assertEqual(self.trace(), [(self.PERIPH, 20)])

    def test_same_mode_returns_success_without_entering_critical_section(
        self,
    ) -> None:
        self.word("current_mode").value = 0
        self.word("previous_mode").value = 0

        self.assertEqual(self.select(0), 0)
        self.assertEqual(self.word("previous_writes").value, 0)
        self.assertEqual(
            self.trace(),
            [
                (self.PERIPH, 20),
                (self.READ_CURRENT, 0),
                (self.READ_PREVIOUS, 0),
                (self.READ_CURRENT, 0),
            ],
        )

    def test_same_mode_repairs_previous_mode_cache(self) -> None:
        self.word("current_mode").value = 3
        self.word("previous_mode").value = 0

        self.assertEqual(self.select(3), 0)
        self.assertEqual(self.word("previous_mode").value, 3)
        self.assertEqual(self.word("previous_writes").value, 1)
        self.assertEqual(
            self.trace(),
            [
                (self.READ_VR, 0x30),
                (self.PERIPH, 20),
                (self.READ_CURRENT, 3),
                (self.READ_PREVIOUS, 0),
                (self.READ_CURRENT, 3),
                (self.WRITE_PREVIOUS, 3),
            ],
        )

    def test_hp_transition_preserves_unrelated_bits_and_order(self) -> None:
        self.word("power_switch").value = 0xA5A50000
        self.word("performance").value = 0x5A5A00FC
        self.word("current_mode").value = 0
        self.word("previous_mode").value = 0
        self.word("primask").value = 1

        result = self.select(3)

        self.assertEqual(result, 0)
        self.assertEqual(self.word("power_switch").value, 0xA5A50001)
        self.assertEqual(self.word("performance").value, 0x5A5A00FF)
        self.assertEqual(self.word("current_mode").value, 3)
        self.assertEqual(self.word("previous_mode").value, 3)
        self.assertEqual(self.word("current_writes").value, 1)
        self.assertEqual(self.word("previous_writes").value, 1)
        self.assertEqual(self.word("ton_calls").value, 1)
        self.assertEqual(self.word("delay_calls").value, 2)
        self.assertEqual(self.word("delay_total").value, 7)
        self.assertEqual(self.word("restored_primask").value, 1)
        self.assertEqual(
            self.trace(),
            [
                (self.READ_VR, 0x30),
                (self.PERIPH, 20),
                (self.READ_CURRENT, 0),
                (self.IRQ_DISABLE, 1),
                (self.TON, 0x103),
                (self.READ_POWER, 0xA5A50000),
                (self.WRITE_POWER, 0xA5A50001),
                (self.DELAY, 1),
                (self.READ_PERFORMANCE, 0x5A5A00FC),
                (self.WRITE_PERFORMANCE, 0x5A5A00FF),
                (self.WRITE_CURRENT, 3),
                (self.WRITE_PREVIOUS, 3),
                (self.DELAY, 6),
                (self.IRQ_RESTORE, 1),
            ],
        )

    def test_lp_transition_changes_ton_after_clock_settles(self) -> None:
        self.word("power_switch").value = 0x12345679
        self.word("performance").value = 0xABCDEF03
        self.word("current_mode").value = 3
        self.word("previous_mode").value = 3
        self.word("primask").value = 0

        result = self.select(0)

        self.assertEqual(result, 0)
        self.assertEqual(self.word("power_switch").value, 0x12345678)
        self.assertEqual(self.word("performance").value, 0xABCDEF00)
        self.assertEqual(self.word("current_mode").value, 0)
        self.assertEqual(self.word("previous_mode").value, 0)
        self.assertEqual(self.word("ton_calls").value, 1)
        self.assertEqual(self.word("delay_calls").value, 2)
        self.assertEqual(self.word("delay_total").value, 7)
        self.assertEqual(self.word("restored_primask").value, 0)
        self.assertEqual(
            self.trace(),
            [
                (self.PERIPH, 20),
                (self.READ_CURRENT, 3),
                (self.IRQ_DISABLE, 0),
                (self.READ_POWER, 0x12345679),
                (self.WRITE_POWER, 0x12345678),
                (self.DELAY, 1),
                (self.READ_PERFORMANCE, 0xABCDEF03),
                (self.WRITE_PERFORMANCE, 0xABCDEF00),
                (self.WRITE_CURRENT, 0),
                (self.WRITE_PREVIOUS, 0),
                (self.DELAY, 6),
                (self.TON, 0x100),
                (self.IRQ_RESTORE, 0),
            ],
        )

    def test_randomized_stock_model(self) -> None:
        randomizer = random.Random(0x47F11C)

        for _ in range(1000):
            self.reset_fixture()
            power_mode = randomizer.choice((0, 3, 1, 2, 4, 0xFF))
            requested_mode = (
                randomizer.randrange(0, 1 << 24) << 8
            ) | power_mode
            vr_status = randomizer.randrange(0, 1 << 32)
            periph_status = randomizer.randrange(0, 5)
            graphics_enabled = randomizer.randrange(0, 4)
            current_mode = randomizer.randrange(0, 4)
            previous_mode = randomizer.randrange(0, 4)
            power_switch = randomizer.randrange(0, 1 << 32)
            performance = randomizer.randrange(0, 1 << 32)
            primask = randomizer.randrange(0, 2)
            self.word("vr_status").value = vr_status
            self.word("periph_status").value = periph_status
            self.word("graphics_enabled").value = graphics_enabled
            self.word("current_mode").value = current_mode
            self.word("previous_mode").value = previous_mode
            self.word("power_switch").value = power_switch
            self.word("performance").value = performance
            self.word("primask").value = primask

            if power_mode not in (0, 3):
                expected = 6
            elif power_mode == 3 and ((vr_status >> 4) & 3) != 3:
                expected = 7
            elif periph_status != 0:
                expected = 1
            elif graphics_enabled & 0xFF:
                expected = 3
            else:
                expected = 0

            self.assertEqual(self.select(requested_mode), expected)

            transition = (
                expected == 0
                and power_mode in (0, 3)
                and current_mode != power_mode
            )
            if transition:
                expected_power = (
                    power_switch | 1
                    if power_mode == 3
                    else power_switch & ~1
                )
                expected_performance = (
                    performance & ~3
                ) | power_mode
                self.assertEqual(
                    self.word("power_switch").value,
                    expected_power & 0xFFFFFFFF,
                )
                self.assertEqual(
                    self.word("performance").value,
                    expected_performance & 0xFFFFFFFF,
                )
                self.assertEqual(
                    self.word("current_mode").value,
                    power_mode,
                )
                self.assertEqual(
                    self.word("previous_mode").value,
                    power_mode,
                )
                self.assertEqual(
                    self.word("restored_primask").value,
                    primask,
                )
                self.assertEqual(self.word("delay_total").value, 7)
                self.assertEqual(self.word("ton_calls").value, 1)
            elif (
                expected == 0
                and current_mode == power_mode
                and previous_mode != current_mode
            ):
                self.assertEqual(
                    self.word("previous_mode").value,
                    power_mode,
                )
                self.assertEqual(self.word("previous_writes").value, 1)
                self.assertEqual(self.word("delay_calls").value, 0)
            else:
                self.assertEqual(
                    self.word("power_switch").value,
                    power_switch,
                )
                self.assertEqual(
                    self.word("performance").value,
                    performance,
                )
                self.assertEqual(self.word("delay_calls").value, 0)

    def test_sources_are_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "ae0e754919056fa48c695ccec040983d13f1a0036d6ee920436ecbb434fc0657",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "9c002afdb447cff0f967b6c14a056982982631b7c43741f9159251c0b2b6b2f4",
        )


if __name__ == "__main__":
    unittest.main()
