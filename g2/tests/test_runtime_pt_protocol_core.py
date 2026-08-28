# SPDX-License-Identifier: MIT
"""Host behavior and target-compilation tests for the PT protocol core."""

from __future__ import annotations

import ctypes
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/pt_protocol_procsr.c"
FIXTURE = ROOT / "tests/fixtures/pt_protocol_core_host.c"
INCLUDE = ROOT / "components/apollo_main/core_overlay"


class PtProtocolCoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory(prefix="g2-pt-core-")
        cls.library = Path(cls.temp.name) / "pt_protocol.dylib"
        subprocess.run([
            "clang", "-std=c11", "-Wall", "-Wextra", "-Werror",
            "-dynamiclib", "-I", str(INCLUDE), str(SOURCE), str(FIXTURE),
            "-o", str(cls.library),
        ], check=True)
        cls.lib = ctypes.CDLL(str(cls.library))
        cls.lib.fixture_pt_initialize()
        cls.lib.fixture_pt_dispatch.argtypes = [
            ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint8,
            ctypes.POINTER(ctypes.c_uint8), ctypes.c_ulong,
            ctypes.POINTER(ctypes.c_uint8),
        ]
        cls.lib.fixture_pt_dispatch.restype = ctypes.c_int

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def dispatch(self, request: bytes, capacity: int = 256):
        request_array = (ctypes.c_uint8 * len(request))(*request)
        response = (ctypes.c_uint8 * 256)()
        length = ctypes.c_uint8()
        result = self.lib.fixture_pt_dispatch(
            request_array, len(request), response, capacity, ctypes.byref(length))
        return result, bytes(response[:length.value])

    def test_bound_handler_is_framed_and_checksummed(self) -> None:
        result, frame = self.dispatch(bytes((0x01, 0x44)))
        self.assertEqual(result, 0)
        self.assertEqual(frame[:-1], bytes.fromhex("5aa5ff0301c744"))
        self.assertEqual(frame[-1], sum(frame[:-1]) & 0xFF)

    def test_unbound_known_and_unknown_commands_fail_closed(self) -> None:
        for command in (0x06, 0xFE):
            result, frame = self.dispatch(bytes((command,)))
            self.assertEqual(result, 0)
            self.assertEqual(frame[0:4], bytes.fromhex("5aa5ff05"))
            self.assertEqual(frame[4:9], bytes((command, 1, 3, 1, 2)))
            self.assertEqual(frame[-1], sum(frame[:-1]) & 0xFF)

    def test_capacity_and_handler_failures_are_explicit(self) -> None:
        self.assertEqual(self.dispatch(bytes((0xFE,)), 9)[0], -3)
        self.assertEqual(self.dispatch(bytes((0x01,)), 256)[0], -5)

    def test_one_byte_frame_length_cannot_wrap_at_256_bytes(self) -> None:
        result, frame = self.dispatch(bytes((0x05,)), 256)
        self.assertEqual(result, -3)
        self.assertEqual(frame, b"")

    def test_armv8m_target_compiles_strictly(self) -> None:
        compiler = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        output = Path(self.temp.name) / "pt_protocol.o"
        subprocess.run([
            compiler, "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
            "-std=c11", "-Oz", "-ffreestanding", "-fno-builtin",
            "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra",
            "-Werror", "-I", str(INCLUDE), "-c", str(SOURCE), "-o", str(output),
        ], check=True, capture_output=True, text=True)
        self.assertTrue(output.is_file())


if __name__ == "__main__":
    unittest.main()
