# SPDX-License-Identifier: MIT

from __future__ import annotations

import ctypes
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = (
    ROOT / "research/candidates/g2_pt_protocol_dispatch_candidate.c"
)
FIXTURE = (
    ROOT / "tests/fixtures/g2_pt_protocol_dispatch_candidate_host.c"
)
COMMANDS = (
    0x01, 0x05, 0x06, 0x07, 0x08, 0x0B, 0x11, 0x13,
    0x17, 0x18, 0x19, 0x1A, 0x1B, 0x1C, 0x20, 0x22,
    0x24, 0x25, 0x26, 0x29, 0x2A, 0x2D, 0x2E, 0x30,
    0x31, 0x35, 0x38, 0x39, 0x3A, 0x3D, 0x3E, 0x42,
    0x43, 0x44, 0x45, 0x46, 0x47, 0x48, 0x49, 0x52,
    0x53, 0x54, 0x55, 0x57, 0x58, 0x59, 0x5A, 0x5B,
    0x60, 0x61, 0x62, 0x63, 0x64, 0x65, 0x66, 0x67,
    0x69, 0x6A, 0x6B, 0x6C, 0x6D, 0x6E, 0x74, 0x75,
    0x77, 0xF3,
)
TARGET_FLAGS = (
    "--target=thumbv7em-none-eabi",
    "-mthumb",
    "-mcpu=cortex-m55",
    "-O2",
    "-ffreestanding",
    "-fno-jump-tables",
    "-fomit-frame-pointer",
    "-fno-builtin",
    "-mno-unaligned-access",
    "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables",
    "-fropi",
    "-ffunction-sections",
    "-fdata-sections",
    "-Wall",
    "-Wextra",
    "-Werror",
)


class G2PtProtocolDispatchCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)
        library = temporary / (
            "g2_pt_protocol_dispatch_candidate.dylib"
            if sys.platform == "darwin"
            else "g2_pt_protocol_dispatch_candidate.so"
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
            command.extend(("-dynamiclib", "-o", str(library)))
        else:
            command.extend(("-shared", "-fPIC", "-o", str(library)))
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.loaded = ctypes.CDLL(str(library))

        cls.count = cls.loaded.open_cfw_test_pt_command_count
        cls.count.argtypes = []
        cls.count.restype = ctypes.c_uint
        cls.command_at = cls.loaded.open_cfw_test_pt_command_at
        cls.command_at.argtypes = [ctypes.c_uint, ctypes.POINTER(ctypes.c_ubyte)]
        cls.command_at.restype = ctypes.c_int
        cls.policy = cls.loaded.open_cfw_test_pt_command_policy
        cls.policy.argtypes = [ctypes.c_uint]
        cls.policy.restype = ctypes.c_int
        cls.dispatch = cls.loaded.open_cfw_test_pt_dispatch
        cls.dispatch.argtypes = [
            ctypes.POINTER(ctypes.c_ubyte),
            ctypes.c_uint,
            ctypes.POINTER(ctypes.c_ubyte),
            ctypes.c_uint,
            ctypes.POINTER(ctypes.c_uint),
        ]
        cls.dispatch.restype = ctypes.c_int

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_exact_authenticated_66_command_surface(self) -> None:
        self.assertEqual(self.count(), 66)
        actual = []
        for index in range(self.count()):
            command = ctypes.c_ubyte(0)
            self.assertEqual(self.command_at(index, ctypes.byref(command)), 1)
            actual.append(command.value)
        self.assertEqual(tuple(actual), COMMANDS)
        command = ctypes.c_ubyte(0xA5)
        self.assertEqual(self.command_at(66, ctypes.byref(command)), 0)
        self.assertEqual(command.value, 0xA5)

    def test_all_known_commands_are_explicitly_withheld(self) -> None:
        known = set(COMMANDS)
        for command in range(256):
            with self.subTest(command=command):
                self.assertEqual(
                    self.policy(command),
                    1 if command in known else 0,
                )

    def test_every_command_fails_closed_with_evidenced_frame(self) -> None:
        for command in range(256):
            with self.subTest(command=command):
                request = (ctypes.c_ubyte * 1)(command)
                response = (ctypes.c_ubyte * 10)(*[0xCC] * 10)
                length = ctypes.c_uint(0)
                result = self.dispatch(
                    request, 1, response, len(response), ctypes.byref(length)
                )
                self.assertEqual(result, 1)
                self.assertEqual(length.value, 10)
                expected = [
                    0x5A, 0xA5, 0xFF, 0x05, command,
                    0x01, 0x03, 0x01, 0x02,
                ]
                expected.append(sum(expected) & 0xFF)
                self.assertEqual(list(response), expected)

    def test_invalid_and_short_output_paths_do_not_emit_a_frame(self) -> None:
        request = (ctypes.c_ubyte * 1)(0x24)
        response = (ctypes.c_ubyte * 10)(*[0xCC] * 10)
        length = ctypes.c_uint(99)
        self.assertEqual(
            self.dispatch(
                request, 1, response, 9, ctypes.byref(length)
            ),
            -2,
        )
        self.assertEqual(length.value, 0)
        self.assertEqual(list(response), [0xCC] * 10)

        length.value = 99
        self.assertEqual(
            self.dispatch(
                None, 0, response, 10, ctypes.byref(length)
            ),
            -1,
        )
        self.assertEqual(length.value, 0)
        self.assertEqual(list(response), [0xCC] * 10)

    def test_unrouted_candidate_compiles_for_cortex_m55(self) -> None:
        object_path = Path(self.temporary.name) / "candidate.o"
        subprocess.run(
            [
                os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
                *TARGET_FLAGS,
                "-c",
                str(CANDIDATE),
                "-o",
                str(object_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertGreater(object_path.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
