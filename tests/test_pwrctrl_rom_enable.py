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
SOURCE = COMPONENT_ROOT / "pwrctrl_rom_enable.c"
FIXTURE = OPENCFW_ROOT / "tests" / "fixtures" / "pwrctrl_rom_enable_host.c"


class PwrctrlRomEnableTests(unittest.TestCase):
    MODE_READ = 1
    STATUS_READ = 2
    SPOT_UPDATE = 3
    ENABLE_READ = 4
    ENABLE_WRITE = 5

    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "pwrctrl_rom_enable.dylib"
            if sys.platform == "darwin"
            else "pwrctrl_rom_enable.so"
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
        cls.reset_fixture = cls.loaded.open_cfw_test_rom_enable_reset
        cls.reset_fixture.argtypes = []
        cls.reset_fixture.restype = None
        cls.enable = cls.loaded.open_cfw_pwrctrl_rom_enable
        cls.enable.argtypes = []
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
            f"open_cfw_test_rom_enable_{name}",
        )

    @classmethod
    def word_array(cls, name: str, count: int = 64) -> ctypes.Array:
        return (ctypes.c_uint * count).in_dll(
            cls.loaded,
            f"open_cfw_test_rom_enable_{name}",
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

                self.assertEqual(self.enable(), 0)

                self.assertEqual(self.word("memory_enable").value, 0xA5A5A5A5)
                self.assertEqual(self.word("memory_status").value, 0x5A5A5A5A)
                self.assertEqual(self.word("spot_calls").value, 0)
                self.assertEqual(self.word("poll_reads").value, 0)
                self.assertEqual(
                    self.trace(),
                    [(self.MODE_READ, mode & 0xFF)],
                )

    def test_immediate_ready_path_has_exact_operation_order(self) -> None:
        self.word("mode").value = 1
        self.word("memory_enable").value = 0xA5A50004
        self.word("memory_status").value = 0x123456F8

        self.assertEqual(self.enable(), 0)

        self.assertEqual(self.word("memory_enable").value, 0xA5A50024)
        self.assertEqual(self.word("poll_reads").value, 1)
        self.assertEqual(self.word("spot_calls").value, 1)
        self.assertEqual(self.word("spot_stimulus").value, 5)
        self.assertEqual(self.word("spot_enabled").value, 1)
        self.assertEqual(self.word("spot_value").value, 0x123456F8)
        self.assertEqual(
            self.trace(),
            [
                (self.MODE_READ, 1),
                (self.STATUS_READ, 0x123456F8),
                (self.SPOT_UPDATE, 0x123456F8),
                (self.ENABLE_READ, 0xA5A50004),
                (self.ENABLE_WRITE, 0xA5A50024),
                (self.STATUS_READ, 0x123456F8),
            ],
        )

    def test_delayed_ready_poll_count_is_exact(self) -> None:
        self.word("mode").value = 1
        self.word("memory_status").value = 0x12
        self.word("ready_after_polls").value = 3

        self.assertEqual(self.enable(), 0)

        self.assertEqual(self.word("poll_reads").value, 4)
        self.assertEqual(self.word("memory_status").value, 0x92)
        self.assertEqual(
            [event for event, _ in self.trace()][-4:],
            [self.STATUS_READ] * 4,
        )

    def test_ten_thousand_failed_polls_return_timeout(self) -> None:
        self.word("mode").value = 1
        self.word("memory_enable").value = 0xCAFEBABE
        self.word("memory_status").value = 0x42
        self.word("ready_after_polls").value = 10000

        self.assertEqual(self.enable(), 4)

        self.assertEqual(self.word("poll_reads").value, 10000)
        self.assertEqual(self.word("memory_enable").value, 0xCAFEBABE | 0x20)
        self.assertEqual(self.word("spot_calls").value, 1)

    def test_spot_error_is_deliberately_ignored(self) -> None:
        self.word("mode").value = 1
        self.word("memory_status").value = 0x80
        self.word("spot_result").value = 0xDEADBEEF

        self.assertEqual(self.enable(), 0)

        self.assertEqual(self.word("spot_calls").value, 1)
        self.assertEqual(self.word("poll_reads").value, 1)
        self.assertEqual(self.word("memory_enable").value, 0x20)

    def test_enable_and_spot_values_preserve_unrelated_bits(self) -> None:
        self.word("mode").value = 1
        self.word("memory_enable").value = 0xFFFFFFDF
        self.word("memory_status").value = 0xA5A50001
        self.word("ready_after_polls").value = 0

        self.assertEqual(self.enable(), 0)

        self.assertEqual(self.word("memory_enable").value, 0xFFFFFFFF)
        self.assertEqual(self.word("spot_value").value, 0xA5A50081)
        self.assertEqual(self.word("memory_status").value, 0xA5A50081)

    def test_randomized_stock_model(self) -> None:
        generator = random.Random(0x47F3C6)

        for _ in range(1000):
            self.reset_fixture()
            mode = generator.randrange(256)
            memory_enable = generator.getrandbits(32)
            memory_status = generator.getrandbits(32)
            ready_after = generator.randrange(10001)
            spot_result = generator.getrandbits(32)
            self.word("mode").value = mode
            self.word("memory_enable").value = memory_enable
            self.word("memory_status").value = memory_status
            self.word("ready_after_polls").value = ready_after
            self.word("spot_result").value = spot_result

            result = self.enable()

            if mode != 1:
                self.assertEqual(result, 0)
                self.assertEqual(self.word("memory_enable").value, memory_enable)
                self.assertEqual(self.word("poll_reads").value, 0)
                self.assertEqual(self.word("spot_calls").value, 0)
                continue

            expected_enable = memory_enable | 0x20
            initially_ready = (memory_status & 0x80) != 0
            expected_polls = (
                1
                if initially_ready
                else min(ready_after + 1, 10000)
            )
            expected_result = (
                4
                if not initially_ready and ready_after == 10000
                else 0
            )
            self.assertEqual(result, expected_result)
            self.assertEqual(self.word("memory_enable").value, expected_enable)
            self.assertEqual(self.word("spot_calls").value, 1)
            self.assertEqual(self.word("spot_stimulus").value, 5)
            self.assertEqual(self.word("spot_enabled").value, 1)
            self.assertEqual(
                self.word("spot_value").value,
                memory_status | 0x80,
            )
            self.assertEqual(self.word("poll_reads").value, expected_polls)

    def test_sources_are_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "c9d5eddab00853a8d5d2b95f31cc0cbf01c3272d645e58f2f8a2b31951ccc00c",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "2f31f848f529ddcbc9c9fc4406641ca18530ef7d881314757134c45d9f91280b",
        )


if __name__ == "__main__":
    unittest.main()
