from __future__ import annotations

import os

import ctypes
import random
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


OPENCFW_ROOT = Path(__file__).resolve().parent.parent
COMPONENT_ROOT = OPENCFW_ROOT / "components" / "apollo_main" / "core_overlay"
FIXTURE = OPENCFW_ROOT / "tests" / "fixtures" / "mram_set_key_host.c"
RECORD_SIZE = 200
EVENT_SIZE = 32
CAPTURE_COUNT = 512
DIAGNOSTIC_COUNT = 64
DIAGNOSTIC_WIDTH = 24


class MramSetKeyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "mram_set_key.dylib"
            if sys.platform == "darwin"
            else "mram_set_key.so"
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
        cls.reset = cls.loaded.open_cfw_test_mram_set_key_reset
        cls.reset.argtypes = []
        cls.reset.restype = None
        cls.set_key = cls.loaded.open_cfw_mram_set_key
        cls.set_key.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        cls.set_key.restype = None

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset()
        self.record = (ctypes.c_ubyte * RECORD_SIZE)()
        self.event = (ctypes.c_ubyte * EVENT_SIZE)()
        self.record_address = ctypes.addressof(self.record)

    def word(self, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(self.loaded, name)

    def address(self, name: str) -> ctypes.c_ulong:
        return ctypes.c_ulong.in_dll(self.loaded, name)

    def words(self, name: str, count: int) -> ctypes.Array:
        return (ctypes.c_uint * count).in_dll(self.loaded, name)

    def addresses(self, name: str, count: int) -> ctypes.Array:
        return (ctypes.c_ulong * count).in_dll(self.loaded, name)

    def invoke(self) -> None:
        self.set_key(
            ctypes.addressof(self.record),
            ctypes.addressof(self.event),
        )

    def seed_buffers(self, seed: int) -> tuple[bytes, bytes]:
        generator = random.Random(seed)
        record = bytes(generator.randrange(256) for _ in range(RECORD_SIZE))
        event = bytes(generator.randrange(256) for _ in range(EVENT_SIZE))
        self.record[:] = record
        self.event[:] = event
        self.record[0x30] = 0
        return bytes(self.record), bytes(self.event)

    def captured_logs(self) -> list[list[int]]:
        count = self.word("open_cfw_test_mram_set_key_log_count").value
        records = self.addresses(
            "open_cfw_test_mram_set_key_log_records",
            DIAGNOSTIC_COUNT * DIAGNOSTIC_WIDTH,
        )
        return [
            list(
                records[
                    index * DIAGNOSTIC_WIDTH:
                    (index + 1) * DIAGNOSTIC_WIDTH
                ]
            )
            for index in range(count)
        ]

    def captured_traces(self) -> list[list[int]]:
        count = self.word("open_cfw_test_mram_set_key_trace_count").value
        records = self.addresses(
            "open_cfw_test_mram_set_key_trace_records",
            DIAGNOSTIC_COUNT * DIAGNOSTIC_WIDTH,
        )
        return [
            list(
                records[
                    index * DIAGNOSTIC_WIDTH:
                    (index + 1) * DIAGNOSTIC_WIDTH
                ]
            )
            for index in range(count)
        ]

    @staticmethod
    def expected_mutation(
        record: bytes,
        event: bytes,
    ) -> bytes:
        result = bytearray(record)
        key_type = event[0x1E]
        if key_type == 1:
            result[0x4E] = event[0x1F]
            result[0x34:0x4E] = event[4:0x1E]
            result[0x2E] |= 1
        elif key_type == 2:
            result[0x6A] = event[0x1F]
            result[0x50:0x6A] = event[4:0x1E]
            result[0x2E] |= 2
        elif key_type == 4:
            result[7:0x1E] = event[4:0x1B]
            result[0x2E] |= 4
            result[6] = event[0x1A]
            result[0:6] = event[0x14:0x1A]
        elif key_type == 8:
            result[0x1E:0x2E] = event[4:0x14]
            result[0x2E] |= 8
            result[0x80:0x84] = b"\0\0\0\0"
        return bytes(result)

    def test_all_key_types_match_exact_record_layout(self) -> None:
        for key_type in (1, 2, 4, 8, 0, 3, 0xFF):
            with self.subTest(key_type=key_type):
                self.reset()
                before, event = self.seed_buffers(0x47AED4 + key_type)
                self.event[0x1E] = key_type
                event = bytes(self.event)

                self.invoke()

                self.assertEqual(
                    bytes(self.record),
                    self.expected_mutation(before, event),
                )

    def test_local_and_peer_ltk_copy_all_26_bytes(self) -> None:
        for key_type, offset, level_offset in (
            (1, 0x34, 0x4E),
            (2, 0x50, 0x6A),
        ):
            with self.subTest(key_type=key_type):
                self.reset()
                self.record[:] = b"\xA5" * RECORD_SIZE
                self.record[0x30] = 0
                self.record[0x2E] = 0x80
                self.event[:] = bytes(range(EVENT_SIZE))
                self.event[0x1E] = key_type
                self.event[0x1F] = 0xD7

                self.invoke()

                self.assertEqual(
                    bytes(self.record[offset:offset + 0x1A]),
                    bytes(self.event[4:0x1E]),
                )
                self.assertEqual(self.record[level_offset], 0xD7)
                self.assertEqual(self.record[0x2E], 0x80 | key_type)

    def test_irk_normalizes_address_and_csrk_resets_counter(self) -> None:
        self.record[:] = b"\xCC" * RECORD_SIZE
        self.record[0x30] = 0
        self.event[:] = bytes((index * 9 + 3) & 0xFF for index in range(32))
        self.event[0x1E] = 4

        self.invoke()

        self.assertEqual(bytes(self.record[0:6]), bytes(self.event[0x14:0x1A]))
        self.assertEqual(self.record[6], self.event[0x1A])
        self.assertEqual(bytes(self.record[7:0x1E]), bytes(self.event[4:0x1B]))

        self.reset()
        self.record[:] = b"\xA7" * RECORD_SIZE
        self.record[0x30] = 0
        self.event[:] = bytes((index * 5 + 1) & 0xFF for index in range(32))
        self.event[0x1E] = 8
        self.invoke()

        self.assertEqual(bytes(self.record[0x1E:0x2E]), bytes(self.event[4:0x14]))
        self.assertEqual(bytes(self.record[0x80:0x84]), b"\0\0\0\0")

    def test_persistence_requires_confirmation_byte_exactly_one(self) -> None:
        for confirmation in (0, 1, 2, 0xFF):
            with self.subTest(confirmation=confirmation):
                self.reset()
                self.record[0x30] = confirmation
                self.event[0x1E] = 0x33
                self.word(
                    "open_cfw_test_mram_set_key_update_result"
                ).value = 0xA5
                self.word(
                    "open_cfw_test_mram_set_key_verify_result"
                ).value = 0x5A

                self.invoke()

                expected = 1 if confirmation == 1 else 0
                self.assertEqual(
                    self.word(
                        "open_cfw_test_mram_set_key_update_calls"
                    ).value,
                    expected,
                )
                self.assertEqual(
                    self.word(
                        "open_cfw_test_mram_set_key_verify_calls"
                    ).value,
                    expected,
                )
                if expected:
                    self.assertEqual(
                        self.address(
                            "open_cfw_test_mram_set_key_update_record"
                        ).value,
                        self.record_address,
                    )
                    self.assertEqual(
                        self.address(
                            "open_cfw_test_mram_set_key_verify_record"
                        ).value,
                        self.record_address,
                    )
                    order_count = self.word(
                        "open_cfw_test_mram_set_key_order_count"
                    ).value
                    order = self.words(
                        "open_cfw_test_mram_set_key_order",
                        CAPTURE_COUNT,
                    )
                    self.assertEqual(
                        list(order[:order_count])[-2:],
                        [4, 5],
                    )

    def test_structured_metadata_covers_every_branch(self) -> None:
        cases = {
            1: (
                (0x506, 0x007693C0, [1]),
                (0x50F, 0x007126F4, [0xB7, 0xA15C]),
                (0x514, 0x006A71F4, list(range(0x30, 0x40))),
                (0x53C, 0x00731844, [0x81]),
            ),
            2: (
                (0x506, 0x007693C0, [2]),
                (0x51C, 0x0071C070, [0xB7, 0xA15C]),
                (0x521, 0x006A7504, list(range(0x30, 0x40))),
                (0x53C, 0x00731844, [0x82]),
            ),
            4: (
                (0x506, 0x007693C0, [4]),
                (0x52A, 0x0074788C, [0x66]),
                (
                    0x52D,
                    0x0071C0A8,
                    [0x65, 0x64, 0x63, 0x62, 0x61, 0x60],
                ),
                (0x53C, 0x00731844, [0x84]),
            ),
            8: (
                (0x506, 0x007693C0, [8]),
                (0x535, 0x007693DC, []),
                (0x53C, 0x00731844, [0x88]),
            ),
            0x33: (
                (0x506, 0x007693C0, [0x33]),
                (0x539, 0x007478B4, [0x33]),
                (0x53C, 0x00731844, [0x80]),
            ),
        }
        for key_type, expected in cases.items():
            with self.subTest(key_type=key_type):
                self.reset()
                self.word(
                    "open_cfw_test_mram_set_key_level_default"
                ).value = 2
                self.record[0x2E] = 0x80
                self.record[0x30] = 0
                for index in range(16):
                    self.event[4 + index] = 0x30 + index
                self.event[0x14:0x1A] = bytes(range(0x60, 0x66))
                self.event[0x1A] = 0x66
                self.event[0x1C] = 0x5C
                self.event[0x1D] = 0xA1
                self.event[0x1E] = key_type
                self.event[0x1F] = 0xB7

                self.invoke()

                logs = self.captured_logs()
                self.assertEqual(len(logs), len(expected))
                for row, (line, identity, arguments) in zip(logs, expected):
                    severity = 2 if line == 0x539 else 4
                    self.assertEqual(
                        row[:6],
                        [
                            severity,
                            0x0078A0D0,
                            0x006D84BC,
                            0x0078A10C,
                            line,
                            identity,
                        ],
                    )
                    self.assertEqual(row[6:6 + len(arguments)], arguments)
                self.assertEqual(self.captured_traces(), [])

    def test_trace_metadata_and_dynamic_key_event_match_stock(self) -> None:
        cases = {
            1: (
                (0x10400000, 0x00747864, [1]),
                (0x10800000, 0x00700348, [0xB7, 0xA15C]),
                (0x12800000, 0x006D5F48, list(range(0x30, 0x40))),
                (0x10400000, 0x00712730, [0x81]),
            ),
            2: (
                (0x10400000, 0x00747864, [2]),
                (0x10800000, 0x0070038C, [0xB7, 0xA15C]),
                (0x12800000, 0x006D5FC0, list(range(0x30, 0x40))),
                (0x10400000, 0x00712730, [0x82]),
            ),
            4: (
                (0x10400000, 0x00747864, [4]),
                (0x10400000, 0x00726DBC, [0x66]),
                (
                    0x11800000,
                    0x007092E4,
                    [0x65, 0x64, 0x63, 0x62, 0x61, 0x60],
                ),
                (0x10400000, 0x00712730, [0x84]),
            ),
            8: (
                (0x10400000, 0x00747864, [8]),
                (0x10000000, 0x00751EF0, []),
                (0x10400000, 0x00712730, [0x88]),
            ),
            0x33: (
                (0x10400000, 0x00747864, [0x33]),
                (0x08400000, 0x00726DF0, [0x33]),
                (0x10400000, 0x00712730, [0x80]),
            ),
        }
        for key_type, expected in cases.items():
            with self.subTest(key_type=key_type):
                self.reset()
                self.word(
                    "open_cfw_test_mram_set_key_level_default"
                ).value = 1
                self.record[0x2E] = 0x80
                self.record[0x30] = 0
                for index in range(16):
                    self.event[4 + index] = 0x30 + index
                self.event[0x14:0x1A] = bytes(range(0x60, 0x66))
                self.event[0x1A] = 0x66
                self.event[0x1C] = 0x5C
                self.event[0x1D] = 0xA1
                self.event[0x1E] = key_type
                self.event[0x1F] = 0xB7

                self.invoke()

                traces = self.captured_traces()
                self.assertEqual(len(traces), len(expected))
                for row, (event, identity, arguments) in zip(
                    traces,
                    expected,
                ):
                    self.assertEqual(row[:3], [event, identity, identity])
                    self.assertEqual(row[3:3 + len(arguments)], arguments)
                self.assertEqual(self.captured_logs(), [])
                self.assertEqual(
                    self.word(
                        "open_cfw_test_mram_set_key_level_index"
                    ).value,
                    2 * len(expected),
                )

    def test_trace_fallback_rereads_level_and_gates_independently(self) -> None:
        levels = self.words(
            "open_cfw_test_mram_set_key_levels",
            CAPTURE_COUNT,
        )
        sequence = [
            2, 0, 4,
            0, 1,
            0, 0, 0,
        ]
        levels[:len(sequence)] = sequence
        self.word("open_cfw_test_mram_set_key_level_count").value = len(
            sequence
        )
        self.event[0x1E] = 0x55
        self.record[0x30] = 0

        self.invoke()

        logs = self.captured_logs()
        traces = self.captured_traces()
        self.assertEqual([row[4] for row in logs], [0x506])
        self.assertEqual(
            [(row[0], row[1]) for row in traces],
            [
                (0x10400000, 0x00747864),
                (0x08400000, 0x00726DF0),
            ],
        )
        self.assertEqual(
            self.word("open_cfw_test_mram_set_key_level_index").value,
            len(sequence),
        )

    def test_randomized_model_preserves_all_unrelated_bytes(self) -> None:
        generator = random.Random(0x47B3AD)
        for _ in range(500):
            self.reset()
            record = bytes(
                generator.randrange(256)
                for _ in range(RECORD_SIZE)
            )
            event = bytes(
                generator.randrange(256)
                for _ in range(EVENT_SIZE)
            )
            self.record[:] = record
            self.event[:] = event
            self.record[0x30] = generator.choice((0, 2, 0xFF))
            record = bytes(self.record)
            event = bytes(self.event)

            self.invoke()

            self.assertEqual(
                bytes(self.record),
                self.expected_mutation(record, event),
            )
            self.assertEqual(
                self.word(
                    "open_cfw_test_mram_set_key_update_calls"
                ).value,
                0,
            )
            self.assertEqual(
                self.word(
                    "open_cfw_test_mram_set_key_verify_calls"
                ).value,
                0,
            )


if __name__ == "__main__":
    unittest.main()
