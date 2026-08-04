from __future__ import annotations

import os

import ctypes
import hashlib
import random
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


OPENCFW_ROOT = Path(__file__).resolve().parent.parent
COMPONENT_ROOT = OPENCFW_ROOT / "components" / "apollo_main" / "core_overlay"
SOURCE = COMPONENT_ROOT / "sarc_state.c"
FIXTURE = OPENCFW_ROOT / "tests" / "fixtures" / "sarc_state_host.c"

MAGIC = 0x43524153
STATE_BYTES = 4524
REPORT_BUFFER_BYTES = 4600
VFORMAT_NATIVE = -(1 << 31)
UINT_MAX = (1 << 32) - 1

TRACE_SNPRINTF = 1
TRACE_OPEN = 2
TRACE_SEEK = 3
TRACE_TELL = 4
TRACE_CLOSE = 5
TRACE_REMOVE = 6
TRACE_WRITE = 7
TRACE_FLUSH = 8
TRACE_LOG = 9
TRACE_CLEAR = 10


class SarcStateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "sarc_state.dylib"
            if sys.platform == "darwin"
            else "sarc_state.so"
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
        cls.checksum = cls.loaded.open_cfw_sarc_header_checksum
        cls.checksum.argtypes = [ctypes.c_void_p]
        cls.checksum.restype = ctypes.c_uint
        cls.valid = cls.loaded.open_cfw_sarc_state_valid
        cls.valid.argtypes = []
        cls.valid.restype = ctypes.c_uint
        cls.initialize = cls.loaded.open_cfw_sarc_state_initialize
        cls.initialize.argtypes = []
        cls.initialize.restype = None
        cls.append0 = cls.loaded.open_cfw_test_sarc_report_append0
        cls.append0.argtypes = [ctypes.c_char_p]
        cls.append0.restype = None
        cls.append1 = cls.loaded.open_cfw_test_sarc_report_append1
        cls.append1.argtypes = [ctypes.c_char_p, ctypes.c_uint]
        cls.append1.restype = None
        cls.append2 = cls.loaded.open_cfw_test_sarc_report_append2
        cls.append2.argtypes = [
            ctypes.c_char_p,
            ctypes.c_uint,
            ctypes.c_uint,
        ]
        cls.append2.restype = None
        cls.finalize = cls.loaded.open_cfw_sarc_report_finalize
        cls.finalize.argtypes = []
        cls.finalize.restype = None
        cls.persist = cls.loaded.open_cfw_sarc_report_persist
        cls.persist.argtypes = [ctypes.c_char_p]
        cls.persist.restype = ctypes.c_uint

        cls.state = (ctypes.c_ubyte * STATE_BYTES).in_dll(
            cls.loaded,
            "open_cfw_test_sarc_state",
        )
        cls.report_buffer = (
            ctypes.c_ubyte * REPORT_BUFFER_BYTES
        ).in_dll(
            cls.loaded,
            "open_cfw_test_sarc_report_buffer",
        )
        cls.report_length = cls.uint(
            "open_cfw_test_sarc_report_length"
        )
        cls.vformat_result = cls.sint(
            "open_cfw_test_sarc_vformat_result"
        )
        cls.vformat_calls = cls.uint(
            "open_cfw_test_sarc_vformat_calls"
        )
        cls.vformat_destination = cls.ulong(
            "open_cfw_test_sarc_vformat_destination"
        )
        cls.vformat_size = cls.uint(
            "open_cfw_test_sarc_vformat_size"
        )
        cls.copy_calls = cls.uint("open_cfw_test_sarc_copy_calls")
        cls.copy_destination = cls.ulong(
            "open_cfw_test_sarc_copy_destination"
        )
        cls.copy_source = cls.ulong(
            "open_cfw_test_sarc_copy_source"
        )
        cls.copy_size = cls.uint("open_cfw_test_sarc_copy_size")
        cls.path_buffer = (ctypes.c_char * 128).in_dll(
            cls.loaded,
            "open_cfw_test_sarc_path_buffer",
        )
        cls.header_buffer = (ctypes.c_char * 512).in_dll(
            cls.loaded,
            "open_cfw_test_sarc_header_buffer",
        )
        cls.footer_buffer = (ctypes.c_char * 256).in_dll(
            cls.loaded,
            "open_cfw_test_sarc_footer_buffer",
        )
        cls.trace_codes = (ctypes.c_uint * 128).in_dll(
            cls.loaded,
            "open_cfw_test_sarc_trace",
        )
        cls.trace_args = (ctypes.c_ulong * (128 * 4)).in_dll(
            cls.loaded,
            "open_cfw_test_sarc_trace_args",
        )
        cls.trace_count = cls.uint("open_cfw_test_sarc_trace_count")
        cls.open_results = (ctypes.c_ulong * 2).in_dll(
            cls.loaded,
            "open_cfw_test_sarc_open_results",
        )
        cls.open_calls = cls.uint("open_cfw_test_sarc_open_calls")
        cls.tell_result = cls.sint("open_cfw_test_sarc_tell_result")
        cls.write_results = (ctypes.c_uint * 3).in_dll(
            cls.loaded,
            "open_cfw_test_sarc_write_results",
        )
        cls.write_calls = cls.uint("open_cfw_test_sarc_write_calls")
        cls.snprintf_results = (ctypes.c_int * 3).in_dll(
            cls.loaded,
            "open_cfw_test_sarc_snprintf_results",
        )
        cls.snprintf_calls = cls.uint(
            "open_cfw_test_sarc_snprintf_calls"
        )
        cls.checksum_result = cls.uint(
            "open_cfw_test_sarc_checksum_result"
        )
        cls.checksum_calls = cls.uint(
            "open_cfw_test_sarc_checksum_calls"
        )
        cls.checksum_data = cls.ulong(
            "open_cfw_test_sarc_checksum_data"
        )
        cls.checksum_size = cls.uint(
            "open_cfw_test_sarc_checksum_size"
        )
        cls.checksum_seed = cls.uint(
            "open_cfw_test_sarc_checksum_seed"
        )
        cls.clear_calls = cls.uint("open_cfw_test_sarc_clear_calls")
        cls.clear_destination = cls.ulong(
            "open_cfw_test_sarc_clear_destination"
        )
        cls.clear_size = cls.uint("open_cfw_test_sarc_clear_size")
        cls.clear_value = cls.uint("open_cfw_test_sarc_clear_value")

    @classmethod
    def uint(cls, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(cls.loaded, name)

    @classmethod
    def sint(cls, name: str) -> ctypes.c_int:
        return ctypes.c_int.in_dll(cls.loaded, name)

    @classmethod
    def ulong(cls, name: str) -> ctypes.c_ulong:
        return ctypes.c_ulong.in_dll(cls.loaded, name)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def reset(self, fill: int = 0) -> None:
        self.state[:] = bytes([fill & 0xFF]) * STATE_BYTES
        self.report_buffer[:] = bytes([0xCC]) * REPORT_BUFFER_BYTES
        self.report_length.value = 0
        self.vformat_result.value = VFORMAT_NATIVE
        self.vformat_calls.value = 0
        self.copy_calls.value = 0
        self.path_buffer[:] = bytes(128)
        self.header_buffer[:] = bytes(512)
        self.footer_buffer[:] = bytes(256)
        self.trace_codes[:] = [0] * 128
        self.trace_args[:] = [0] * (128 * 4)
        self.trace_count.value = 0
        self.open_results[:] = [0, 0]
        self.open_calls.value = 0
        self.tell_result.value = 0
        self.write_results[:] = [UINT_MAX] * 3
        self.write_calls.value = 0
        self.snprintf_results[:] = [VFORMAT_NATIVE] * 3
        self.snprintf_calls.value = 0
        self.checksum_result.value = 0
        self.checksum_calls.value = 0
        self.clear_calls.value = 0

    def word(self, offset: int, value: int) -> None:
        struct.pack_into("<I", self.state, offset, value & 0xFFFFFFFF)

    def make_valid_state(
        self,
        *,
        sequence: int = 1,
        payload: bytes = b"payload",
        flags: int = 0,
        checksum: int = 0x12345678,
    ) -> None:
        self.word(0, MAGIC)
        self.word(4, 1)
        self.word(8, sequence)
        self.word(12, len(payload))
        self.word(16, flags)
        self.word(20, checksum)
        self.state[24:24 + len(payload)] = payload
        self.checksum_result.value = checksum

    def trace(self) -> list[tuple[int, tuple[int, int, int, int]]]:
        return [
            (
                self.trace_codes[index],
                tuple(
                    self.trace_args[index * 4 + item]
                    for item in range(4)
                ),
            )
            for index in range(self.trace_count.value)
        ]

    def test_header_checksum_threshold_and_arguments(self) -> None:
        for length, expected_calls in (
            (0, 1),
            (1, 1),
            (4500, 1),
            (4501, 0),
            (0xFFFFFFFF, 0),
        ):
            self.reset()
            self.word(12, length)
            self.checksum_result.value = 0xA5A55A5A
            expected = 0xA5A55A5A if expected_calls else 0
            self.assertEqual(self.checksum(ctypes.byref(self.state)), expected)
            self.assertEqual(self.checksum_calls.value, expected_calls)
            if expected_calls:
                self.assertEqual(
                    self.checksum_data.value,
                    ctypes.addressof(self.state),
                )
                self.assertEqual(self.checksum_size.value, 20)
                self.assertEqual(self.checksum_seed.value, 0)

    def test_validator_accepts_only_complete_matching_header(self) -> None:
        self.reset()
        self.word(0, MAGIC)
        self.word(4, 1)
        self.word(12, 4500)
        self.word(20, 0x12345678)
        self.checksum_result.value = 0x12345678
        self.assertEqual(self.valid(), 1)
        self.assertEqual(self.checksum_calls.value, 1)

        self.checksum_calls.value = 0
        self.checksum_result.value = 0x87654321
        self.assertEqual(self.valid(), 0)
        self.assertEqual(self.checksum_calls.value, 1)

    def test_validator_short_circuits_invalid_fields(self) -> None:
        cases = [
            (0, 1, 1),
            (MAGIC, 0, 1),
            (MAGIC, 2, 1),
            (MAGIC, 1, 0),
            (MAGIC, 1, 4501),
            (MAGIC, 1, 0xFFFFFFFF),
        ]
        for magic, valid, length in cases:
            self.reset()
            self.word(0, magic)
            self.word(4, valid)
            self.word(12, length)
            self.assertEqual(self.valid(), 0)
            self.assertEqual(self.checksum_calls.value, 0)

    def test_initializer_preserves_magic_or_clears_exact_state(self) -> None:
        self.reset(0xA5)
        self.word(0, MAGIC)
        before = bytes(self.state)
        self.initialize()
        self.assertEqual(bytes(self.state), before)
        self.assertEqual(self.clear_calls.value, 0)

        self.reset(0xA5)
        self.word(0, MAGIC ^ 1)
        self.word(8, 0xFFFFFFFF)
        self.initialize()
        self.assertEqual(self.clear_calls.value, 1)
        self.assertEqual(
            self.clear_destination.value,
            ctypes.addressof(self.state),
        )
        self.assertEqual(self.clear_size.value, STATE_BYTES)
        self.assertEqual(self.clear_value.value, 0)
        self.assertEqual(bytes(self.state), bytes(STATE_BYTES))

    def test_randomized_validator_model(self) -> None:
        generator = random.Random(0x0047DA16)
        for _ in range(500):
            self.reset()
            magic = generator.getrandbits(32)
            valid = generator.getrandbits(32)
            length = generator.getrandbits(32)
            stored = generator.getrandbits(32)
            calculated = generator.getrandbits(32)
            self.word(0, magic)
            self.word(4, valid)
            self.word(12, length)
            self.word(20, stored)
            self.checksum_result.value = calculated
            expected = int(
                magic == MAGIC
                and valid == 1
                and 0 < length <= 4500
                and stored == calculated
            )
            self.assertEqual(self.valid(), expected)
            self.assertEqual(
                self.checksum_calls.value,
                int(magic == MAGIC and valid == 1 and 0 < length <= 4500),
            )

    def test_report_append_null_full_and_corrupt_length_gates(self) -> None:
        self.reset()
        before = bytes(self.report_buffer)
        self.report_length.value = 37
        self.append0(None)
        self.assertEqual(self.vformat_calls.value, 0)
        self.assertEqual(self.report_length.value, 37)
        self.assertEqual(bytes(self.report_buffer), before)

        self.report_length.value = 4499
        self.append0(b"ignored")
        self.assertEqual(self.vformat_calls.value, 0)
        self.assertEqual(self.report_length.value, 4499)
        self.assertEqual(bytes(self.report_buffer), before)

        self.report_length.value = 4500
        self.vformat_result.value = -1
        self.append0(b"corrupt")
        self.assertEqual(self.vformat_calls.value, 1)
        self.assertEqual(
            self.vformat_destination.value,
            ctypes.addressof(self.report_buffer) + 4500,
        )
        self.assertEqual(self.vformat_size.value, 0)
        self.assertEqual(self.report_length.value, 4500)
        self.assertEqual(self.report_buffer[4500], 0)

    def test_report_append_formats_variadic_arguments(self) -> None:
        self.reset()
        self.report_buffer[:4] = b"pre:"
        self.report_length.value = 4
        self.append2(b"%u/%02x", 17, 0x2A)
        self.assertEqual(self.vformat_calls.value, 1)
        self.assertEqual(
            self.vformat_destination.value,
            ctypes.addressof(self.report_buffer) + 4,
        )
        self.assertEqual(self.vformat_size.value, 4496)
        self.assertEqual(self.report_length.value, 9)
        self.assertEqual(bytes(self.report_buffer[:10]), b"pre:17/2a\0")

        self.append1(b"-%u", 99)
        self.assertEqual(self.vformat_calls.value, 2)
        self.assertEqual(self.vformat_size.value, 4491)
        self.assertEqual(self.report_length.value, 12)
        self.assertEqual(bytes(self.report_buffer[:13]), b"pre:17/2a-99\0")

    def test_report_append_clamps_and_terminates_all_results(self) -> None:
        cases = [
            (10, -7, 10),
            (10, 0, 10),
            (10, 1, 11),
            (10, 33, 43),
            (4490, 9, 4499),
            (4490, 10, 4499),
            (4490, 0x7FFFFFFF, 4499),
        ]
        for current, result, expected in cases:
            self.reset()
            self.report_length.value = current
            self.vformat_result.value = result
            self.append0(b"x")
            self.assertEqual(self.vformat_calls.value, 1)
            self.assertEqual(self.vformat_size.value, 4500 - current)
            self.assertEqual(self.report_length.value, expected)
            self.assertEqual(self.report_buffer[expected], 0)

    def test_randomized_report_append_length_model(self) -> None:
        generator = random.Random(0x0047DA78)
        for _ in range(500):
            self.reset()
            current = generator.randrange(0, 4499)
            result = generator.choice(
                [
                    -generator.randrange(1, 100),
                    0,
                    generator.randrange(1, 10000),
                ]
            )
            remaining = 4499 - current
            expected = current
            if result > 0:
                expected += min(result, remaining)
            self.report_length.value = current
            self.vformat_result.value = result
            self.append0(b"x")
            self.assertEqual(self.report_length.value, expected)
            self.assertEqual(self.report_buffer[expected], 0)

    def test_report_finalize_builds_exact_state_or_is_noop(self) -> None:
        self.reset(0xA5)
        before = bytes(self.state)
        self.finalize()
        self.assertEqual(bytes(self.state), before)
        self.assertEqual(self.copy_calls.value, 0)
        self.assertEqual(self.checksum_calls.value, 0)

        self.reset(0xA5)
        payload = b"payload"
        self.report_buffer[:len(payload)] = payload
        self.report_length.value = len(payload)
        self.word(8, 0xFFFFFFFF)
        self.checksum_result.value = 0xA1B2C3D4
        self.finalize()
        self.assertEqual(
            struct.unpack_from("<6I", self.state),
            (
                MAGIC,
                1,
                0,
                len(payload),
                0,
                0xA1B2C3D4,
            ),
        )
        self.assertEqual(
            bytes(self.state[24:24 + len(payload) + 1]),
            payload + b"\0",
        )
        self.assertEqual(self.state[24 + len(payload) + 1], 0xA5)
        self.assertEqual(self.copy_calls.value, 1)
        self.assertEqual(
            self.copy_destination.value,
            ctypes.addressof(self.state) + 24,
        )
        self.assertEqual(
            self.copy_source.value,
            ctypes.addressof(self.report_buffer),
        )
        self.assertEqual(self.copy_size.value, len(payload))
        self.assertEqual(self.checksum_calls.value, 1)
        self.assertEqual(
            self.checksum_data.value,
            ctypes.addressof(self.state),
        )
        self.assertEqual(self.checksum_size.value, 20)
        self.assertEqual(self.checksum_seed.value, 0)

    def test_report_persist_rejects_invalid_state_without_io(self) -> None:
        self.reset()
        before = bytes(self.state)
        self.assertEqual(self.persist(b"/log"), 0)
        self.assertEqual(self.trace(), [])
        self.assertEqual(self.checksum_calls.value, 0)
        self.assertEqual(bytes(self.state), before)

    def test_report_persist_open_failure_clears_but_preserves_sequence(
        self,
    ) -> None:
        self.reset()
        self.make_valid_state(sequence=3)
        self.assertEqual(self.persist(b"/log"), 1)
        self.assertEqual(
            [code for code, _args in self.trace()],
            [
                TRACE_SNPRINTF,
                TRACE_OPEN,
                TRACE_OPEN,
                TRACE_LOG,
                TRACE_CLEAR,
            ],
        )
        self.assertEqual(self.path_buffer.value, b"/log/hardfault.txt")
        events = self.trace()
        self.assertEqual(ctypes.string_at(events[1][1][1]), b"r")
        self.assertEqual(ctypes.string_at(events[2][1][1]), b"a+")
        self.assertEqual(events[3][1][:3], (3, events[3][1][1], 0))
        self.assertEqual(
            events[3][1][1],
            ctypes.addressof(self.path_buffer),
        )
        self.assertEqual(
            struct.unpack_from("<6I", self.state),
            (0, 0, 3, 0, 0, 0),
        )
        self.assertEqual(bytes(self.state[24:]), bytes(4500))
        self.assertEqual(self.checksum_calls.value, 1)

    def test_report_persist_existing_size_threshold(self) -> None:
        for size, removed in (
            (-1, False),
            (102400, False),
            (102401, True),
            (0x7FFFFFFF, True),
        ):
            self.reset()
            self.make_valid_state(sequence=4)
            self.open_results[:] = [0x1111, 0]
            self.tell_result.value = size
            self.assertEqual(self.persist(b"/log"), 1)
            codes = [code for code, _args in self.trace()]
            self.assertEqual(
                codes[:6],
                [
                    TRACE_SNPRINTF,
                    TRACE_OPEN,
                    TRACE_SEEK,
                    TRACE_TELL,
                    TRACE_CLOSE,
                    TRACE_REMOVE if removed else TRACE_OPEN,
                ],
            )
            self.assertEqual(TRACE_REMOVE in codes, removed)
            size_logs = [
                args
                for code, args in self.trace()
                if code == TRACE_LOG and args[0] == 2
            ]
            self.assertEqual(len(size_logs), int(removed))
            seek = self.trace()[2][1]
            self.assertEqual(seek[:3], (0x1111, 0, 2))

    def test_report_persist_writes_exact_header_payload_and_footer(
        self,
    ) -> None:
        for flags, availability in ((0, "N/A"), (1, "Available")):
            self.reset()
            payload = b"abc"
            self.make_valid_state(
                sequence=7,
                payload=payload,
                flags=flags,
                checksum=0xA1B2C3D4,
            )
            self.open_results[:] = [0, 0x2222]
            self.assertEqual(self.persist(b"/log"), 1)
            self.assertEqual(
                [code for code, _args in self.trace()],
                [
                    TRACE_SNPRINTF,
                    TRACE_OPEN,
                    TRACE_OPEN,
                    TRACE_SNPRINTF,
                    TRACE_WRITE,
                    TRACE_WRITE,
                    TRACE_SNPRINTF,
                    TRACE_WRITE,
                    TRACE_FLUSH,
                    TRACE_CLOSE,
                    TRACE_LOG,
                    TRACE_CLEAR,
                ],
            )
            expected_header = (
                "\n========================================\n"
                "===== CRASH #7 =====\n"
                f"Timestamp: {availability}\n"
                "Data Length: 3 bytes\n"
                "CRC32: 0xA1B2C3D4\n"
                "----------------------------------------\n\n"
            ).encode()
            expected_footer = (
                "\n========================================\n"
                "===== END CRASH #7 =====\n"
                "========================================\n\n"
            ).encode()
            self.assertEqual(self.header_buffer.value, expected_header)
            self.assertEqual(self.footer_buffer.value, expected_footer)
            writes = [
                args
                for code, args in self.trace()
                if code == TRACE_WRITE
            ]
            self.assertEqual(
                writes,
                [
                    (
                        ctypes.addressof(self.header_buffer),
                        1,
                        len(expected_header),
                        0x2222,
                    ),
                    (
                        ctypes.addressof(self.state) + 24,
                        1,
                        len(payload),
                        0x2222,
                    ),
                    (
                        ctypes.addressof(self.footer_buffer),
                        1,
                        len(expected_footer),
                        0x2222,
                    ),
                ],
            )
            recovered = [
                args
                for code, args in self.trace()
                if code == TRACE_LOG and args[0] == 5
            ]
            self.assertEqual(
                recovered,
                [(5, 7, ctypes.addressof(self.path_buffer), recovered[0][3])],
            )
            self.assertEqual(
                struct.unpack_from("<6I", self.state),
                (0, 0, 7, 0, 0, 0),
            )

    def test_report_persist_warns_only_for_short_payload_write(self) -> None:
        self.reset()
        self.make_valid_state(sequence=8, payload=b"12345")
        self.open_results[:] = [0, 0x3333]
        self.write_results[:] = [UINT_MAX, 2, UINT_MAX]
        self.assertEqual(self.persist(b"/log"), 1)
        warnings = [
            args
            for code, args in self.trace()
            if code == TRACE_LOG and args[0] == 4
        ]
        self.assertEqual(len(warnings), 1)
        self.assertEqual(warnings[0][1:3], (2, 5))

    def test_report_persist_nonpositive_formats_skip_wrapper_writes(
        self,
    ) -> None:
        self.reset()
        self.make_valid_state(sequence=9, payload=b"data")
        self.open_results[:] = [0, 0x4444]
        self.snprintf_results[:] = [VFORMAT_NATIVE, 0, -1]
        self.assertEqual(self.persist(b"/log"), 1)
        writes = [
            args
            for code, args in self.trace()
            if code == TRACE_WRITE
        ]
        self.assertEqual(
            writes,
            [
                (
                    ctypes.addressof(self.state) + 24,
                    1,
                    4,
                    0x4444,
                ),
            ],
        )

    def test_report_persist_logs_sequence_above_ten_first(self) -> None:
        self.reset()
        self.make_valid_state(sequence=11)
        self.assertEqual(self.persist(b"/log"), 1)
        self.assertEqual(self.trace()[0][0], TRACE_LOG)
        self.assertEqual(self.trace()[0][1][0:2], (1, 11))
        self.assertEqual(struct.unpack_from("<I", self.state, 8)[0], 11)

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "51da9eb678b1a9bf4232ba50cc1d8eefa168cba0200729d669c6b378f4bf0211",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "74191c6409531f484e5d60564f68f5d3d3db71941abf17ab0ba12d37ec0aeb80",
        )


if __name__ == "__main__":
    unittest.main()
