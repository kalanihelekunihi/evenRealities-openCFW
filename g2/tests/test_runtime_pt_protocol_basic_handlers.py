# SPDX-License-Identifier: MIT
from __future__ import annotations

import ctypes
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "components/apollo_main/core_overlay/pt_protocol_procsr.c"
HANDLERS = ROOT / "components/apollo_main/core_overlay/pt_protocol_handlers_basic.c"
FIXTURE = ROOT / "tests/fixtures/pt_protocol_basic_handlers_host.c"
INCLUDE = ROOT / "components/apollo_main/core_overlay"


class PtProtocolBasicHandlersTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory(prefix="g2-pt-basic-")
        library = Path(cls.temp.name) / "pt_basic.dylib"
        subprocess.run([
            "clang", "-std=c11", "-Wall", "-Wextra", "-Werror",
            "-dynamiclib", "-I", str(INCLUDE), str(CORE), str(HANDLERS),
            str(FIXTURE), "-o", str(library),
        ], check=True)
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.fixture_pt_basic_dispatch.argtypes = [
            ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint8,
            ctypes.POINTER(ctypes.c_uint8), ctypes.c_ulong,
            ctypes.POINTER(ctypes.c_uint8),
        ]
        cls.lib.fixture_pt_basic_dispatch.restype = ctypes.c_int

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def setUp(self) -> None:
        self.lib.fixture_pt_basic_initialize()

    def dispatch(self, data: bytes):
        request = (ctypes.c_uint8 * len(data))(*data)
        response = (ctypes.c_uint8 * 256)()
        length = ctypes.c_uint8()
        result = self.lib.fixture_pt_basic_dispatch(
            request, len(data), response, 256, ctypes.byref(length))
        return result, bytes(response[:length.value])

    def assert_payload(self, request: bytes, expected: bytes) -> None:
        result, frame = self.dispatch(request)
        self.assertEqual(result, 0)
        self.assertEqual(frame[4:-1], expected)
        self.assertEqual(frame[-1], sum(frame[:-1]) & 0xFF)

    def test_box_command_chain(self) -> None:
        self.assert_payload(bytes((0x06, 0, 0, 0)), bytes((0x07, 1, 3, 1, 0)))
        self.assertEqual(self.lib.fixture_pt_basic_box_value(), 0)
        self.assert_payload(bytes((0x07, 0, 0, 0)), bytes((0x08, 1, 3, 1, 0)))
        self.assertEqual(self.lib.fixture_pt_basic_box_value(), 1)
        self.assert_payload(bytes((0x08, 0, 0, 0)), bytes((0x0B, 1, 3, 1, 0)))

    def test_codec_and_input_actions(self) -> None:
        self.assert_payload(bytes((0x57, 0, 0, 0)), bytes((0x57, 1, 3, 1, 0)))
        self.assertEqual(self.lib.fixture_pt_basic_codec_calls(), 1)
        self.assert_payload(bytes((0xF3,)), bytes((0x77, 1, 3, 1, 0)))
        self.assertEqual(self.lib.fixture_pt_basic_input_calls(), 1)

    def test_terminal_mode_store_and_load(self) -> None:
        result, frame = self.dispatch(bytes((0x61, 0, 0, 0, 0x9A)))
        self.assertEqual(result, 0)
        self.assertEqual(frame[3], 0)
        self.assertEqual(len(frame), 5)
        self.assert_payload(bytes((0x65,)), bytes((0x64, 1, 3, 1, 0x9A)))

    def test_minimum_lengths_are_enforced(self) -> None:
        self.assertEqual(self.dispatch(bytes((0x06,)))[0], -5)
        self.assertEqual(self.dispatch(bytes((0x61, 0, 0, 0)))[0], -5)

    def test_both_sources_compile_for_apollo510(self) -> None:
        compiler = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        for source in (CORE, HANDLERS):
            output = Path(self.temp.name) / (source.stem + ".o")
            subprocess.run([
                compiler, "--target=arm-none-eabi", "-mcpu=cortex-m55",
                "-mthumb", "-std=c11", "-Oz", "-ffreestanding",
                "-fno-builtin", "-ffunction-sections", "-fdata-sections",
                "-Wall", "-Wextra", "-Werror", "-I", str(INCLUDE),
                "-c", str(source), "-o", str(output),
            ], check=True, capture_output=True, text=True)


if __name__ == "__main__":
    unittest.main()
