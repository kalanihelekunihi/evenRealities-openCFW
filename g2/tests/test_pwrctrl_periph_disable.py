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
SOURCE = COMPONENT_ROOT / "pwrctrl_periph_disable.c"
FIXTURE = (
    OPENCFW_ROOT / "tests" / "fixtures" / "pwrctrl_periph_disable_host.c"
)


class PwrctrlPeriphDisableTests(unittest.TestCase):
    DESCRIPTOR = 1
    READ = 2
    WRITE = 3
    STATUS_CHECK = 4
    POSTPONE = 5
    IRQ_DISABLE = 6
    IRQ_RESTORE = 7
    MASK_CHECK = 8
    MODE_READ = 9
    MODE_WRITE = 10
    GPU_SELECT = 11
    SPOT = 12
    CLOCK_RELEASE = 13
    CLOCK_RELEASE_ALL = 14
    PENDING = 15

    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "pwrctrl_periph_disable.dylib"
            if sys.platform == "darwin"
            else "pwrctrl_periph_disable.so"
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
        cls.reset_fixture = cls.loaded.open_cfw_test_disable_reset
        cls.reset_fixture.argtypes = []
        cls.reset_fixture.restype = None
        cls.disable = cls.loaded.open_cfw_pwrctrl_periph_disable
        cls.disable.argtypes = [ctypes.c_uint]
        cls.disable.restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset_fixture()

    @classmethod
    def word(cls, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_disable_{name}",
        )

    @classmethod
    def words(cls, name: str, count: int) -> ctypes.Array:
        return (ctypes.c_uint * count).in_dll(
            cls.loaded,
            f"open_cfw_test_disable_{name}",
        )

    def trace(self) -> list[tuple[int, int, int, int]]:
        count = min(self.word("trace_count").value, 96)
        events = self.words("trace_event", 96)
        a = self.words("trace_a", 96)
        b = self.words("trace_b", 96)
        c = self.words("trace_c", 96)
        return [
            (events[index], a[index], b[index], c[index])
            for index in range(count)
        ]

    def test_descriptor_error_and_low_byte_abi(self) -> None:
        self.word("descriptor_result").value = 6

        self.assertEqual(self.disable(0x12345678), 6)
        self.assertEqual(
            self.trace(),
            [(self.DESCRIPTOR, 0x78, 0, 0)],
        )

    def test_already_disabled_returns_without_power_sequence(self) -> None:
        self.word("enable_mask").value = 0x20
        self.word("enable_register").value = 0xA5A50000

        self.assertEqual(self.disable(7), 0)
        self.assertEqual(
            self.trace(),
            [
                (self.DESCRIPTOR, 7, 0, 0),
                (self.READ, 0x1000, 0xA5A50000, 0),
            ],
        )

    def test_pre_b1_otp_refuses_disable_while_crypto_is_powered(self) -> None:
        self.word("chip_revision").value = 0x21
        self.word("device_status").value = 0x00200000

        self.assertEqual(self.disable(29), 3)
        self.assertEqual(
            self.trace(),
            [
                (self.DESCRIPTOR, 29, 0, 0),
                (self.READ, 0x1000, 0x20, 0),
                (self.READ, 0x4002000C, 0x21, 0),
                (self.READ, 0x40021008, 0x00200000, 0),
            ],
        )

    def test_otp_wait_parameters_and_timeout_short_circuit(self) -> None:
        self.word("chip_revision").value = 0x22
        self.word("status_check_result").value = 7

        self.assertEqual(self.disable(29), 7)
        self.assertIn(
            (self.STATUS_CHECK, 100000, 0x40014AC4, 1),
            self.trace(),
        )
        self.assertEqual(self.word("status_expected").value, 0)
        self.assertEqual(self.word("status_equal").value, 1)
        self.assertFalse(
            any(event[0] == self.POSTPONE for event in self.trace())
        )
        self.assertEqual(self.word("enable_register").value, 0x20)

    def test_debug_registers_are_quiesced_before_tempco(self) -> None:
        self.word("enable_mask").value = 0x10000000
        self.word("enable_register").value = 0xF0000000
        self.word("demcr").value = 0xA5FFFFFF
        self.word("debug_control").value = 0x123456FF

        self.assertEqual(self.disable(28), 0)
        trace = self.trace()
        self.assertEqual(self.word("demcr").value, 0xA4FFFFFF)
        self.assertEqual(self.word("debug_control").value, 0x123456F0)
        self.assertLess(
            next(index for index, event in enumerate(trace)
                 if event[0] == self.WRITE and event[1] == 0xE000EDFC),
            next(index for index, event in enumerate(trace)
                 if event[0] == self.POSTPONE),
        )
        debug_writes = [
            event
            for event in trace
            if event[0] == self.WRITE and event[1] == 0x40020250
        ]
        self.assertEqual(
            debug_writes,
            [
                (self.WRITE, 0x40020250, 0x123456FE, 0),
                (self.WRITE, 0x40020250, 0x123456F0, 0),
            ],
        )

    def test_shared_domain_skips_status_wait_but_handles_pending(self) -> None:
        self.word("enable_register").value = 0xA5000020
        self.word("mask_result").value = 0
        self.word("status_check_result").value = 9
        self.word("primask").value = 1

        self.assertEqual(self.disable(5), 0)
        self.assertEqual(self.word("enable_register").value, 0xA5000000)
        self.assertFalse(
            any(event[0] == self.STATUS_CHECK for event in self.trace())
        )
        self.assertEqual(self.trace()[-1], (self.PENDING, 0, 0, 0))
        self.assertIn((self.IRQ_RESTORE, 1, 0, 0), self.trace())

    def test_status_failure_is_returned_after_pending_handling(self) -> None:
        self.word("status_check_result").value = 8

        self.assertEqual(self.disable(6), 8)
        self.assertIn(
            (self.STATUS_CHECK, 5, 0x1004, 0x200),
            self.trace(),
        )
        self.assertEqual(self.word("status_expected").value, 0x200)
        self.assertEqual(self.word("status_equal").value, 0)
        self.assertFalse(any(event[0] == self.SPOT for event in self.trace()))
        self.assertEqual(self.trace()[-1], (self.PENDING, 0, 0, 0))

    def test_crypto_success_releases_hfrc(self) -> None:
        self.assertEqual(self.disable(23), 0)
        self.assertIn(
            (self.CLOCK_RELEASE, 4, 23, 0),
            self.trace(),
        )
        self.assertFalse(
            any(event[0] == self.CLOCK_RELEASE_ALL for event in self.trace())
        )

    def test_gpu_high_performance_sequence_ignores_callback_results(
        self,
    ) -> None:
        self.word("current_mode").value = 3
        self.word("previous_mode").value = 1
        self.word("gpu_result").value = 12
        self.word("spot_result").value = 13

        self.assertEqual(self.disable(20), 0)
        tail = [
            event
            for event in self.trace()
            if event[0] in {
                self.MODE_READ,
                self.GPU_SELECT,
                self.MODE_WRITE,
                self.SPOT,
                self.CLOCK_RELEASE_ALL,
            }
        ]
        self.assertEqual(
            tail,
            [
                (self.MODE_READ, 0x20074F60, 3, 0),
                (self.GPU_SELECT, 0, 0, 0),
                (self.MODE_WRITE, 0x20074F61, 3, 0),
                (self.SPOT, 1, 1, 0),
                (self.CLOCK_RELEASE_ALL, 20, 0, 0),
            ],
        )
        self.assertEqual(self.word("previous_mode").value, 3)
        self.assertEqual(self.trace()[-1], (self.PENDING, 0, 0, 0))

    def test_gpu_low_power_and_device_audio_monitor_paths(self) -> None:
        self.word("current_mode").value = 0
        self.word("previous_mode").value = 3
        self.assertEqual(self.disable(20), 0)
        self.assertNotIn(
            (self.GPU_SELECT, 0, 0, 0),
            self.trace(),
        )
        self.assertEqual(self.word("previous_mode").value, 0)

        self.reset_fixture()
        self.word("status_mask").value = 0x1E
        self.assertEqual(self.disable(5), 0)
        self.assertIn((self.SPOT, 3, 0, 0x1E), self.trace())

        self.reset_fixture()
        self.word("enable_mask").value = 0x4
        self.word("enable_register").value = 0x4
        self.word("status_mask").value = 0xC0
        self.assertEqual(self.disable(30), 0)
        self.assertIn((self.SPOT, 4, 0, 0xC0), self.trace())

        self.reset_fixture()
        self.word("enable_mask").value = 0x80000000
        self.word("enable_register").value = 0x80000000
        self.assertEqual(self.disable(7), 0)
        self.assertFalse(any(event[0] == self.SPOT for event in self.trace()))

    def test_randomized_normal_peripheral_model(self) -> None:
        generator = random.Random(0x47F7AE)

        for _ in range(500):
            self.reset_fixture()
            peripheral = generator.randrange(0, 20)
            enable_mask = generator.getrandbits(32) or 1
            enable_value = generator.getrandbits(32) | enable_mask
            status_result = generator.randrange(0, 5)
            mask_result = generator.randrange(0, 2)
            self.word("enable_mask").value = enable_mask
            self.word("enable_register").value = enable_value
            self.word("status_check_result").value = status_result
            self.word("mask_result").value = mask_result

            result = self.disable(peripheral)

            self.assertEqual(
                self.word("enable_register").value,
                enable_value & ~enable_mask,
            )
            self.assertEqual(
                result,
                status_result if mask_result else 0,
            )
            self.assertEqual(
                any(event[0] == self.SPOT for event in self.trace()),
                bool(
                    mask_result
                    and status_result == 0
                    and ((enable_mask << 2) & 0xFFFFFFFF)
                ),
            )
            self.assertEqual(self.trace()[-1], (self.PENDING, 0, 0, 0))

    def test_sources_are_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "7af651f900d25b29bec7fe71d70893009c3d0e48c14db995d0a3a1d32494c57a",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "1ebdac6030a41c6265f60bbec31eb5bcb9bfdee8536c3d8740fe8e7b89c439e6",
        )


if __name__ == "__main__":
    unittest.main()
