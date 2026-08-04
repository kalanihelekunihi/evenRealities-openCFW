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
SOURCE = COMPONENT_ROOT / "pwrctrl_rom_disable.c"
FIXTURE = OPENCFW_ROOT / "tests" / "fixtures" / "pwrctrl_rom_disable_host.c"


class PwrctrlRomDisableTests(unittest.TestCase):
    MODE_READ = 1
    ENABLE_READ = 2
    ENABLE_WRITE = 3
    STATUS_READ = 4
    SPOT_UPDATE = 5

    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "pwrctrl_rom_disable.dylib"
            if sys.platform == "darwin"
            else "pwrctrl_rom_disable.so"
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
        cls.reset_fixture = cls.loaded.open_cfw_test_rom_disable_reset
        cls.reset_fixture.argtypes = []
        cls.reset_fixture.restype = None
        cls.disable = cls.loaded.open_cfw_pwrctrl_rom_disable
        cls.disable.argtypes = []
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
            f"open_cfw_test_rom_disable_{name}",
        )

    @classmethod
    def word_array(cls, name: str, count: int = 64) -> ctypes.Array:
        return (ctypes.c_uint * count).in_dll(
            cls.loaded,
            f"open_cfw_test_rom_disable_{name}",
        )

    def trace(self) -> list[tuple[int, int]]:
        count = min(self.word("trace_count").value, 64)
        events = self.word_array("trace_event")
        values = self.word_array("trace_value")
        return [(events[index], values[index]) for index in range(count)]

    def test_non_auto_modes_are_no_ops(self) -> None:
        for mode in (0, 2, 0xFF, 0x12345602):
            with self.subTest(mode=mode):
                self.reset_fixture()
                self.word("mode").value = mode
                self.word("memory_enable").value = 0xA5A5A5A5
                self.word("memory_status").value = 0x5A5A5A5A

                self.assertEqual(self.disable(), 0)

                self.assertEqual(self.word("memory_enable").value, 0xA5A5A5A5)
                self.assertEqual(self.word("memory_status").value, 0x5A5A5A5A)
                self.assertEqual(self.word("spot_calls").value, 0)
                self.assertEqual(self.word("poll_reads").value, 0)
                self.assertEqual(
                    self.trace(),
                    [(self.MODE_READ, mode & 0xFF)],
                )

    def test_already_clear_path_has_exact_operation_order(self) -> None:
        self.word("mode").value = 1
        self.word("memory_enable").value = 0xA5A50034
        self.word("memory_status").value = 0x12345678

        self.assertEqual(self.disable(), 0)

        self.assertEqual(self.word("memory_enable").value, 0xA5A50014)
        self.assertEqual(self.word("poll_reads").value, 1)
        self.assertEqual(self.word("status_reads").value, 2)
        self.assertEqual(self.word("spot_calls").value, 1)
        self.assertEqual(self.word("spot_stimulus").value, 5)
        self.assertEqual(self.word("spot_enabled").value, 0)
        self.assertEqual(self.word("spot_value").value, 0x12345678)
        self.assertEqual(
            self.trace(),
            [
                (self.MODE_READ, 1),
                (self.ENABLE_READ, 0xA5A50034),
                (self.ENABLE_WRITE, 0xA5A50014),
                (self.STATUS_READ, 0x12345678),
                (self.STATUS_READ, 0x12345678),
                (self.SPOT_UPDATE, 0x12345678),
            ],
        )

    def test_delayed_clear_poll_count_is_exact(self) -> None:
        self.word("mode").value = 1
        self.word("memory_status").value = 0x92
        self.word("clear_after_polls").value = 3

        self.assertEqual(self.disable(), 0)

        self.assertEqual(self.word("poll_reads").value, 4)
        self.assertEqual(self.word("status_reads").value, 5)
        self.assertEqual(self.word("memory_status").value, 0x12)
        self.assertEqual(
            [event for event, _ in self.trace()][3:8],
            [self.STATUS_READ] * 5,
        )
        self.assertEqual(self.trace()[-1], (self.SPOT_UPDATE, 0x12))

    def test_ten_thousand_failed_polls_return_timeout_without_spot(self) -> None:
        self.word("mode").value = 1
        self.word("memory_enable").value = 0xCAFEBABE
        self.word("memory_status").value = 0xC2
        self.word("clear_after_polls").value = 10000

        self.assertEqual(self.disable(), 4)

        self.assertEqual(self.word("poll_reads").value, 10000)
        self.assertEqual(self.word("status_reads").value, 10000)
        self.assertEqual(self.word("memory_enable").value, 0xCAFEBABE & ~0x20)
        self.assertEqual(self.word("spot_calls").value, 0)

    def test_spot_error_is_deliberately_ignored(self) -> None:
        self.word("mode").value = 1
        self.word("memory_status").value = 0x42
        self.word("spot_result").value = 0xDEADBEEF

        self.assertEqual(self.disable(), 0)

        self.assertEqual(self.word("spot_calls").value, 1)
        self.assertEqual(self.word("poll_reads").value, 1)
        self.assertEqual(self.word("spot_enabled").value, 0)

    def test_enable_clear_preserves_unrelated_bits(self) -> None:
        self.word("mode").value = 1
        self.word("memory_enable").value = 0xFFFFFFFF
        self.word("memory_status").value = 0xA5A50001

        self.assertEqual(self.disable(), 0)

        self.assertEqual(self.word("memory_enable").value, 0xFFFFFFDF)
        self.assertEqual(self.word("spot_value").value, 0xA5A50001)
        self.assertEqual(self.word("memory_status").value, 0xA5A50001)

    def test_randomized_stock_model(self) -> None:
        generator = random.Random(0x47F418)

        for _ in range(1000):
            self.reset_fixture()
            mode = generator.randrange(256)
            memory_enable = generator.getrandbits(32)
            memory_status = generator.getrandbits(32)
            clear_after = generator.randrange(10001)
            spot_result = generator.getrandbits(32)
            self.word("mode").value = mode
            self.word("memory_enable").value = memory_enable
            self.word("memory_status").value = memory_status
            self.word("clear_after_polls").value = clear_after
            self.word("spot_result").value = spot_result

            result = self.disable()

            if mode != 1:
                self.assertEqual(result, 0)
                self.assertEqual(self.word("memory_enable").value, memory_enable)
                self.assertEqual(self.word("poll_reads").value, 0)
                self.assertEqual(self.word("spot_calls").value, 0)
                continue

            initially_clear = (memory_status & 0x80) == 0
            expected_polls = (
                1
                if initially_clear
                else min(clear_after + 1, 10000)
            )
            expected_timeout = (
                not initially_clear and clear_after == 10000
            )
            expected_status = (
                memory_status
                if initially_clear or expected_timeout
                else memory_status & ~0x80
            )
            self.assertEqual(result, 4 if expected_timeout else 0)
            self.assertEqual(
                self.word("memory_enable").value,
                memory_enable & ~0x20,
            )
            self.assertEqual(self.word("poll_reads").value, expected_polls)
            self.assertEqual(
                self.word("status_reads").value,
                expected_polls + (0 if expected_timeout else 1),
            )
            self.assertEqual(
                self.word("spot_calls").value,
                0 if expected_timeout else 1,
            )
            if not expected_timeout:
                self.assertEqual(self.word("spot_stimulus").value, 5)
                self.assertEqual(self.word("spot_enabled").value, 0)
                self.assertEqual(self.word("spot_value").value, expected_status)

    def test_sources_are_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "a0046509b7c9d6d3d701438783bb6c983585670d8b04116bd5802a5fa903b02c",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "6d01daab2844cac6e636671b652f6bede776690774f6bf07e82a59c7f7fdd043",
        )


if __name__ == "__main__":
    unittest.main()
