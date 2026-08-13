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
SOURCE = COMPONENT_ROOT / "pwrctrl_gpu_mode_status.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "pwrctrl_gpu_mode_status_host.c"
)


class PwrctrlGpuModeStatusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "pwrctrl_gpu_mode_status.dylib"
            if sys.platform == "darwin"
            else "pwrctrl_gpu_mode_status.so"
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
        cls.reset_fixture = cls.loaded.open_cfw_test_gpu_status_reset
        cls.reset_fixture.argtypes = []
        cls.reset_fixture.restype = None
        cls.status = cls.loaded.open_cfw_pwrctrl_gpu_mode_status
        cls.status.argtypes = [ctypes.POINTER(ctypes.c_ubyte)]
        cls.status.restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset_fixture()

    @classmethod
    def word(cls, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_gpu_status_{name}",
        )

    def test_null_output_returns_six_without_reading_cache(self) -> None:
        self.word("current_mode").value = 3

        self.assertEqual(self.status(None), 6)
        self.assertEqual(self.word("read_calls").value, 0)

    def test_success_copies_cached_low_byte(self) -> None:
        self.word("current_mode").value = 0xA5A50103
        output = ctypes.c_ubyte(0xFF)

        self.assertEqual(self.status(ctypes.byref(output)), 0)
        self.assertEqual(output.value, 3)
        self.assertEqual(self.word("read_calls").value, 1)

    def test_copy_writes_exactly_one_byte(self) -> None:
        self.word("current_mode").value = 0x5A
        output = (ctypes.c_ubyte * 3)(0x11, 0x22, 0x33)
        middle = ctypes.cast(
            ctypes.byref(output, 1),
            ctypes.POINTER(ctypes.c_ubyte),
        )

        self.assertEqual(self.status(middle), 0)
        self.assertEqual(list(output), [0x11, 0x5A, 0x33])

    def test_all_cached_byte_values_are_preserved(self) -> None:
        for value in range(256):
            with self.subTest(value=value):
                self.word("current_mode").value = value
                output = ctypes.c_ubyte(value ^ 0xFF)

                self.assertEqual(self.status(ctypes.byref(output)), 0)
                self.assertEqual(output.value, value)

    def test_randomized_full_width_cache_values_use_low_byte(self) -> None:
        randomizer = random.Random(0x47F108)

        for _ in range(1000):
            value = randomizer.randrange(0, 1 << 32)
            self.word("current_mode").value = value
            output = ctypes.c_ubyte(0)

            self.assertEqual(self.status(ctypes.byref(output)), 0)
            self.assertEqual(output.value, value & 0xFF)

    def test_sources_are_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "17476d09ef111c2ab2068d43ec7aba65e4d5746b0caa0a891991bc639b0edc7c",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "afba4cec8b6e506402c46712c99c8cb2e6bc8e8ead360562dfcb1129cefeef23",
        )


if __name__ == "__main__":
    unittest.main()
