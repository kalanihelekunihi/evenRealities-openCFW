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
SOURCE = COMPONENT_ROOT / "status_packets.c"
FIXTURE = OPENCFW_ROOT / "tests" / "fixtures" / "status_packets_host.c"


class StatusPacketTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "status_packets.dylib"
            if sys.platform == "darwin"
            else "status_packets.so"
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
        cls.functions = {
            3: cls.loaded.open_cfw_status_packet_template3,
            6: cls.loaded.open_cfw_status_packet_template6,
            5: cls.loaded.open_cfw_status_packet_template5,
        }
        for function in cls.functions.values():
            function.argtypes = []
            function.restype = ctypes.c_uint
        cls.lens_values = (
            ctypes.c_uint * 2
        ).in_dll(
            cls.loaded,
            "open_cfw_test_status_packet_lens_values",
        )
        cls.lens_calls = ctypes.c_uint.in_dll(
            cls.loaded,
            "open_cfw_test_status_packet_lens_calls",
        )
        cls.state = ctypes.c_ubyte.in_dll(
            cls.loaded,
            "open_cfw_test_status_packet_state",
        )
        cls.send_calls = ctypes.c_uint.in_dll(
            cls.loaded,
            "open_cfw_test_status_packet_send_calls",
        )
        cls.command = ctypes.c_uint.in_dll(
            cls.loaded,
            "open_cfw_test_status_packet_command",
        )
        cls.size = ctypes.c_uint.in_dll(
            cls.loaded,
            "open_cfw_test_status_packet_size",
        )
        cls.option = ctypes.c_uint.in_dll(
            cls.loaded,
            "open_cfw_test_status_packet_option",
        )
        cls.send_result = ctypes.c_int.in_dll(
            cls.loaded,
            "open_cfw_test_status_packet_send_result",
        )
        cls.payload = (ctypes.c_ubyte * 8).in_dll(
            cls.loaded,
            "open_cfw_test_status_packet_payload",
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def invoke(
        self,
        template: int,
        first_side: int,
        second_side: int,
        state: int,
        send_result: int = 0,
    ) -> tuple[int, bytes]:
        self.lens_values[:] = [first_side, second_side]
        self.lens_calls.value = 0
        self.state.value = state
        self.send_calls.value = 0
        self.send_result.value = send_result

        result = self.functions[template]()

        self.assertEqual(self.lens_calls.value, 2)
        self.assertEqual(self.send_calls.value, 1)
        self.assertEqual(self.command.value, 0x103)
        self.assertEqual(self.size.value, 8)
        self.assertEqual(self.option.value, 0)
        return result, bytes(self.payload)

    def test_template3_reports_state_bit_two(self) -> None:
        self.assertEqual(
            self.invoke(3, 1, 1, 0x04),
            (0x00010003, bytes([3, 0, 1, 0, 1, 2, 1, 0])),
        )
        self.assertEqual(
            self.invoke(3, 2, 2, 0xFB),
            (0x00010003, bytes([3, 0, 1, 0, 2, 1, 0, 0])),
        )

    def test_template6_maps_state_bit_four_to_two_or_three(self) -> None:
        self.assertEqual(
            self.invoke(6, 2, 1, 0x10),
            (0x00010006, bytes([6, 0, 1, 0, 2, 2, 3, 0])),
        )
        self.assertEqual(
            self.invoke(6, 1, 2, 0xEF),
            (0x00010006, bytes([6, 0, 1, 0, 1, 1, 2, 0])),
        )

    def test_template5_preserves_zero_status_byte(self) -> None:
        self.assertEqual(
            self.invoke(5, 3, 3, 0xFF),
            (0x00010005, bytes([5, 0, 1, 0, 3, 1, 0, 0])),
        )

    def test_randomized_model_and_send_result_is_ignored(self) -> None:
        generator = random.Random(0x0047CE90)
        for _ in range(600):
            template = generator.choice([3, 6, 5])
            first_side = generator.getrandbits(32)
            second_side = generator.getrandbits(32)
            state = generator.getrandbits(8)
            result, payload = self.invoke(
                template,
                first_side,
                second_side,
                state,
                generator.randrange(-(1 << 31), 1 << 31),
            )
            expected_status = {
                3: (state >> 2) & 1,
                6: 3 if state & 0x10 else 2,
                5: 0,
            }[template]
            self.assertEqual(result, 0x00010000 | template)
            self.assertEqual(
                payload,
                bytes(
                    [
                        template,
                        0,
                        1,
                        0,
                        first_side & 0xFF,
                        2 if second_side == 1 else 1,
                        expected_status,
                        0,
                    ]
                ),
            )

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "468f8eb73551418cacf7d3a97c14113e93300e7f2feb389a47320001ba1b3d1b",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "2591527cd1bac9f2f8d8b185a0ff0cf69ce5f2bf9f98a0dd9fc218de89eab73c",
        )


if __name__ == "__main__":
    unittest.main()
