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
SOURCE = COMPONENT_ROOT / "pwrctrl_periph_enable.c"
FIXTURE = (
    OPENCFW_ROOT / "tests" / "fixtures" / "pwrctrl_periph_enable_host.c"
)


class PwrctrlPeriphEnableTests(unittest.TestCase):
    DESCRIPTOR = 1
    READ = 2
    POSTPONE = 3
    GPU_SELECT = 4
    CLOCK = 5
    SPOT = 6
    IRQ_DISABLE = 7
    WRITE = 8
    IRQ_RESTORE = 9
    PENDING = 10
    STATUS_CHECK = 11
    STATUS_CHANGE = 12
    DELAY = 13

    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "pwrctrl_periph_enable.dylib"
            if sys.platform == "darwin"
            else "pwrctrl_periph_enable.so"
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
        cls.reset_fixture = cls.loaded.open_cfw_test_enable_reset
        cls.reset_fixture.argtypes = []
        cls.reset_fixture.restype = None
        cls.enable = cls.loaded.open_cfw_pwrctrl_periph_enable
        cls.enable.argtypes = [ctypes.c_uint]
        cls.enable.restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset_fixture()

    @classmethod
    def word(cls, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_enable_{name}",
        )

    @classmethod
    def words(cls, name: str, count: int) -> ctypes.Array:
        return (ctypes.c_uint * count).in_dll(
            cls.loaded,
            f"open_cfw_test_enable_{name}",
        )

    def trace(self) -> list[tuple[int, int, int, int]]:
        count = min(self.word("trace_count").value, 64)
        events = self.words("trace_event", 64)
        a = self.words("trace_a", 64)
        b = self.words("trace_b", 64)
        c = self.words("trace_c", 64)
        return [
            (events[index], a[index], b[index], c[index])
            for index in range(count)
        ]

    def test_descriptor_error_and_low_byte_abi(self) -> None:
        self.word("descriptor_result").value = 6

        self.assertEqual(self.enable(0x12345678), 6)
        self.assertEqual(
            self.trace(),
            [(self.DESCRIPTOR, 0x78, 0, 0)],
        )

    def test_already_enabled_returns_without_power_sequence(self) -> None:
        self.word("enable_mask").value = 0x20
        self.word("enable_register").value = 0xA5A50020

        self.assertEqual(self.enable(7), 0)
        self.assertEqual(
            self.trace(),
            [
                (self.DESCRIPTOR, 7, 0, 0),
                (self.READ, 0x1000, 0xA5A50020, 0),
            ],
        )

    def test_crypto_requires_otp_before_tempco(self) -> None:
        self.word("device_status").value = 0

        self.assertEqual(self.enable(23), 1)
        self.assertEqual(
            self.trace(),
            [
                (self.DESCRIPTOR, 23, 0, 0),
                (self.READ, 0x1000, 0, 0),
                (self.READ, 0x40021008, 0, 0),
            ],
        )

    def test_normal_device_sequence_and_ignored_spot_result(self) -> None:
        self.word("enable_register").value = 0xA5000000
        self.word("enable_mask").value = 0x20
        self.word("status_mask").value = 0x200
        self.word("status_register").value = 0xA0000200
        self.word("spot_result").value = 19
        self.word("primask").value = 1

        self.assertEqual(self.enable(5), 0)
        self.assertEqual(
            self.trace(),
            [
                (self.DESCRIPTOR, 5, 0, 0),
                (self.READ, 0x1000, 0xA5000000, 0),
                (self.POSTPONE, 0, 0, 0),
                (self.SPOT, 3, 1, 0x200),
                (self.IRQ_DISABLE, 1, 0, 0),
                (self.READ, 0x1000, 0xA5000000, 0),
                (self.WRITE, 0x1000, 0xA5000020, 0),
                (self.IRQ_RESTORE, 1, 0, 0),
                (self.PENDING, 0, 0, 0),
                (self.STATUS_CHECK, 5, 0x1004, 0x200),
                (self.READ, 0x1004, 0xA0000200, 0),
            ],
        )
        self.assertEqual(self.word("status_equal").value, 1)

    def test_audio_monitor_and_unmonitored_masks(self) -> None:
        self.word("enable_mask").value = 0x4
        self.word("status_mask").value = 0xC0
        self.word("status_register").value = 0xC0
        self.assertEqual(self.enable(30), 0)
        self.assertIn((self.SPOT, 4, 1, 0xC0), self.trace())

        self.reset_fixture()
        self.word("enable_mask").value = 0x80000000
        self.assertEqual(self.enable(7), 0)
        self.assertFalse(
            any(event[0] == self.SPOT for event in self.trace())
        )

    def test_gpu_sequence_ignores_gpu_and_spot_results(self) -> None:
        self.word("previous_mode").value = 3
        self.word("current_mode").value = 3
        self.word("gpu_result").value = 12
        self.word("spot_result").value = 13

        self.assertEqual(self.enable(20), 0)
        trace = self.trace()
        expected_prefix = [
            (self.DESCRIPTOR, 20, 0, 0),
            (self.READ, 0x1000, 0, 0),
            (self.POSTPONE, 0, 0, 0),
            (self.GPU_SELECT, 3, 0, 0),
            (self.CLOCK, 4, 20, 0),
            (self.CLOCK, 5, 20, 0),
            (self.SPOT, 1, 1, 2),
        ]
        self.assertEqual(trace[:len(expected_prefix)], expected_prefix)
        self.assertNotIn((self.SPOT, 3, 1, 0x200), trace)

    def test_crypto_idle_and_clock_paths(self) -> None:
        self.word("status_change_result").value = 8
        self.assertEqual(self.enable(23), 8)
        self.assertIn(
            (self.STATUS_CHANGE, 100, 0x400C1F10, 1),
            self.trace(),
        )
        self.assertFalse(
            any(
                event[0] == self.CLOCK and event[2] == 23
                for event in self.trace()
            )
        )

        self.reset_fixture()
        self.assertEqual(self.enable(23), 0)
        self.assertIn((self.CLOCK, 4, 23, 0), self.trace())

    def test_status_failure_otp_delay_and_final_verification(self) -> None:
        self.word("status_check_result").value = 7
        self.assertEqual(self.enable(10), 7)
        self.assertFalse(
            any(event[0] == self.READ and event[1] == 0x1004
                for event in self.trace())
        )

        self.reset_fixture()
        self.assertEqual(self.enable(29), 0)
        self.assertIn((self.DELAY, 100, 0, 0), self.trace())

        self.reset_fixture()
        self.word("status_register").value = 0
        self.assertEqual(self.enable(2), 1)

    def test_randomized_normal_peripheral_model(self) -> None:
        generator = random.Random(0x47F5B8)

        for _ in range(500):
            self.reset_fixture()
            peripheral = generator.randrange(0, 20)
            enable_mask = generator.getrandbits(32)
            enable_value = generator.getrandbits(32) & ~enable_mask
            status_mask = generator.getrandbits(32) | 1
            status_value = generator.getrandbits(32)
            self.word("enable_mask").value = enable_mask
            self.word("enable_register").value = enable_value
            self.word("status_mask").value = status_mask
            self.word("status_register").value = status_value

            result = self.enable(peripheral)

            self.assertEqual(
                self.word("enable_register").value,
                enable_value | enable_mask,
            )
            self.assertEqual(
                result,
                0 if status_value & status_mask else 1,
            )
            spot_expected = ((enable_mask << 2) & 0xFFFFFFFF) != 0
            self.assertEqual(
                any(event[0] == self.SPOT for event in self.trace()),
                spot_expected,
            )

    def test_sources_are_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "7a2a382590d734fe2020242d28a39059b67e3f10e77ecfb17db3c3201e37e3d2",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "1afe216d6e606f4c2370e52a00d76bb166ae662413558192b82134126e6ba4db",
        )


if __name__ == "__main__":
    unittest.main()
