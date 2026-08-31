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
SOURCE = COMPONENT_ROOT / "wall_time.c"
FIXTURE = OPENCFW_ROOT / "tests" / "fixtures" / "wall_time_host.c"
UINT_MASK = (1 << 32) - 1
VALID_BEGIN = 1_704_067_200
VALID_SPAN = 2_398_377_600


class WallTimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "wall_time.dylib" if sys.platform == "darwin" else "wall_time.so"
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
        cls.wall_time = cls.loaded.open_cfw_wall_time_seconds
        cls.wall_time.argtypes = [ctypes.POINTER(ctypes.c_ubyte)]
        cls.wall_time.restype = ctypes.c_uint
        cls.trace = (
            ctypes.c_uint * 4
        ).in_dll(cls.loaded, "open_cfw_test_wall_time_trace")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @classmethod
    def word(cls, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(cls.loaded, name)

    def reset(self, *, mode: int, seconds: int) -> None:
        self.word("open_cfw_test_wall_time_mode").value = mode & UINT_MASK
        self.word("open_cfw_test_wall_time_seconds").value = (
            seconds & UINT_MASK
        )
        for name in (
            "open_cfw_test_wall_time_mode_calls",
            "open_cfw_test_wall_time_seconds_calls",
            "open_cfw_test_wall_time_trace_count",
        ):
            self.word(name).value = 0
        self.trace[:] = [0] * 4

    def run_helper(self, initial_valid: int = 0xA5) -> tuple[int, int]:
        valid = ctypes.c_ubyte(initial_valid)
        result = self.wall_time(ctypes.byref(valid))
        return result, valid.value

    def test_non_clock_modes_return_zero_without_reading_seconds(self) -> None:
        for mode in (0, 1, 3, UINT_MASK):
            with self.subTest(mode=mode):
                self.reset(mode=mode, seconds=0x12345678)
                self.assertEqual(self.run_helper(), (0, 0))
                self.assertEqual(
                    self.word("open_cfw_test_wall_time_mode_calls").value,
                    1,
                )
                self.assertEqual(
                    self.word("open_cfw_test_wall_time_seconds_calls").value,
                    0,
                )
                self.assertEqual(
                    self.trace[
                        :self.word(
                            "open_cfw_test_wall_time_trace_count"
                        ).value
                    ],
                    [1],
                )

    def test_validity_window_is_2024_through_2099(self) -> None:
        cases = (
            (VALID_BEGIN - 1, 0),
            (VALID_BEGIN, 1),
            (VALID_BEGIN + VALID_SPAN - 1, 1),
            (VALID_BEGIN + VALID_SPAN, 0),
        )
        for seconds, expected_valid in cases:
            with self.subTest(seconds=seconds):
                self.reset(mode=2, seconds=seconds)
                self.assertEqual(
                    self.run_helper(),
                    (seconds & UINT_MASK, expected_valid),
                )

    def test_clock_mode_returns_raw_seconds_and_queries_in_order(self) -> None:
        self.reset(mode=2, seconds=0xFFFFFFFF)
        self.assertEqual(self.run_helper(), (UINT_MASK, 0))
        self.assertEqual(
            self.word("open_cfw_test_wall_time_mode_calls").value,
            1,
        )
        self.assertEqual(
            self.word("open_cfw_test_wall_time_seconds_calls").value,
            1,
        )
        self.assertEqual(
            self.trace[
                :self.word("open_cfw_test_wall_time_trace_count").value
            ],
            [1, 2],
        )

    def test_randomized_unsigned_window_model(self) -> None:
        generator = random.Random(0x0047DCB4)
        for _ in range(500):
            seconds = generator.getrandbits(32)
            self.reset(mode=2, seconds=seconds)
            expected_valid = int(
                ((seconds - VALID_BEGIN) & UINT_MASK) < VALID_SPAN
            )
            self.assertEqual(
                self.run_helper(),
                (seconds, expected_valid),
            )

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "935b9df00b5918816bb5fcb76452edfd9e163558b38f4fcc2e7bb8499af1d30a",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "6342648f1ed466b7e3db2d23ca2676e36db34796c047977bb2257e938384ece8",
        )


if __name__ == "__main__":
    unittest.main()
