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
SOURCE = COMPONENT_ROOT / "efs_crc32c_msb.c"
FIXTURE = (
    OPENCFW_ROOT / "tests" / "fixtures" / "efs_crc32c_msb_host.c"
)


def crc32c_msb(data: bytes, initial: int) -> int:
    crc = initial
    for value in data:
        crc ^= value << 24
        for _ in range(8):
            crc = ((crc << 1) & 0xFFFFFFFF) ^ (
                0x1EDC6F41 if crc & 0x80000000 else 0
            )
    return crc


class EfsCrc32cMsbTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "efs_crc32c_msb.dylib"
            if sys.platform == "darwin"
            else "efs_crc32c_msb.so"
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
        subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.loaded = ctypes.CDLL(str(library))
        cls.update = cls.loaded.open_cfw_efs_crc32c_msb_update
        cls.update.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint,
            ctypes.POINTER(ctypes.c_uint),
        ]
        cls.update.restype = None

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def calculate(self, data: bytes, initial: int) -> int:
        buffer = (ctypes.c_ubyte * len(data)).from_buffer_copy(data)
        state = ctypes.c_uint(initial)
        self.update(buffer, len(data), ctypes.byref(state))
        return state.value

    def test_standard_check_input_matches_nonreflected_castagnoli(self) -> None:
        self.assertEqual(self.calculate(b"123456789", 0), 0xC052A8C8)
        self.assertEqual(
            self.calculate(b"123456789", 0xFFFFFFFF),
            0xFABBF0EA,
        )

    def test_zero_length_preserves_state_without_reading_data(self) -> None:
        state = ctypes.c_uint(0xA5A55A5A)

        self.update(None, 0, ctypes.byref(state))

        self.assertEqual(state.value, 0xA5A55A5A)

    def test_incremental_updates_equal_one_shot_update(self) -> None:
        data = bytes(range(256)) * 3
        state = ctypes.c_uint(0x12345678)
        first = (ctypes.c_ubyte * 311).from_buffer_copy(data[:311])
        second = (ctypes.c_ubyte * (len(data) - 311)).from_buffer_copy(
            data[311:]
        )

        self.update(first, len(first), ctypes.byref(state))
        self.update(second, len(second), ctypes.byref(state))

        self.assertEqual(state.value, crc32c_msb(data, 0x12345678))

    def test_randomized_model_and_input_immutability(self) -> None:
        generator = random.Random(0x47CBC4)
        for _ in range(500):
            data = generator.randbytes(generator.randrange(513))
            initial = generator.getrandbits(32)
            buffer = (ctypes.c_ubyte * len(data)).from_buffer_copy(data)
            state = ctypes.c_uint(initial)

            self.update(buffer, len(data), ctypes.byref(state))

            self.assertEqual(state.value, crc32c_msb(data, initial))
            self.assertEqual(bytes(buffer), data)

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "b88d5ca2f7825bb8d5dc180840b4c81af96033b66d912f0cf89ab33a2111c4c6",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "4dd9dc8e008331a21a2f41792fe9953336e8882403dfe8a2e6ed2bb9dd29c8ee",
        )


if __name__ == "__main__":
    unittest.main()
