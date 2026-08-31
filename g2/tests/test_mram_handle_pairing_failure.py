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
SOURCE = COMPONENT_ROOT / "mram_handle_pairing_failure.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "mram_handle_pairing_failure_host.c"
)
CAPTURE_COUNT = 128
CAPTURE_WIDTH = 16


class MramHandlePairingFailureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "mram_handle_pairing_failure.dylib"
            if sys.platform == "darwin"
            else "mram_handle_pairing_failure.so"
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
        cls.reset = cls.loaded.open_cfw_test_mram_pairing_failure_reset
        cls.reset.argtypes = []
        cls.reset.restype = None
        cls.handle = cls.loaded.open_cfw_mram_handle_pairing_failure
        cls.handle.argtypes = [ctypes.c_uint, ctypes.c_uint]
        cls.handle.restype = None

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset()

    def word(self, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(self.loaded, name)

    def pointer(self, name: str) -> ctypes.c_void_p:
        return ctypes.c_void_p.in_dll(self.loaded, name)

    def words(self, name: str, count: int) -> ctypes.Array:
        return (ctypes.c_uint * count).in_dll(self.loaded, name)

    def addresses(self, name: str, count: int) -> ctypes.Array:
        return (ctypes.c_size_t * count).in_dll(self.loaded, name)

    def record(self) -> ctypes.Array:
        return (ctypes.c_ubyte * 256).in_dll(
            self.loaded,
            "open_cfw_test_mram_pairing_failure_record",
        )

    def use_record(self) -> ctypes.Array:
        record = self.record()
        self.pointer(
            "open_cfw_test_mram_pairing_failure_lookup_result"
        ).value = ctypes.addressof(record)
        return record

    def captures(self, name: str, count_name: str) -> list[list[int]]:
        count = self.word(count_name).value
        values = self.addresses(name, CAPTURE_COUNT * CAPTURE_WIDTH)
        return [
            list(
                values[
                    index * CAPTURE_WIDTH:
                    (index + 1) * CAPTURE_WIDTH
                ]
            )
            for index in range(count)
        ]

    def logs(self) -> list[list[int]]:
        return self.captures(
            "open_cfw_test_mram_pairing_failure_logs",
            "open_cfw_test_mram_pairing_failure_log_count",
        )

    def traces(self) -> list[list[int]]:
        return self.captures(
            "open_cfw_test_mram_pairing_failure_traces",
            "open_cfw_test_mram_pairing_failure_trace_count",
        )

    def order(self) -> list[int]:
        count = self.word(
            "open_cfw_test_mram_pairing_failure_order_count"
        ).value
        return list(
            self.words(
                "open_cfw_test_mram_pairing_failure_order",
                CAPTURE_COUNT,
            )[:count]
        )

    def test_always_reports_then_shows_nvm_before_connection_lookup(
        self,
    ) -> None:
        self.word(
            "open_cfw_test_mram_pairing_failure_level_default"
        ).value = 7

        self.handle(0x105, 0x104)

        self.assertEqual(
            self.word(
                "open_cfw_test_mram_pairing_failure_show_count"
            ).value,
            1,
        )
        self.assertEqual(
            self.word(
                "open_cfw_test_mram_pairing_failure_lookup_count"
            ).value,
            1,
        )
        self.assertEqual(
            self.word(
                "open_cfw_test_mram_pairing_failure_lookup_connection"
            ).value,
            5,
        )
        self.assertLess(self.order().index(4), self.order().index(5))
        self.assertEqual([record[4] for record in self.logs()], [0x872, 0x8A6])
        self.assertEqual(self.logs()[0][7:9], [5, 4])
        self.assertEqual(self.logs()[1][7], 5)
        self.assertEqual(
            [record[0] for record in self.traces()],
            [0x10800000, 0x10400000],
        )

    def test_qualifying_record_reports_address_reason_and_clears(
        self,
    ) -> None:
        reasons = {
            0x0B: (1, 0x885, 0x006E6478, 0x04000000, 0x006DC574),
            4: (2, 0x88A, 0x00700568, 0x08000000, 0x006EB718),
            1: (2, 0x88E, 0x007005AC, 0x08000000, 0x006EB768),
            3: (2, 0x892, 0x006E64CC, 0x08000000, 0x006DF714),
            0x42: (2, 0x896, 0x006EB7B8, 0x08400000, 0x006E25F0),
        }
        for status, expected in reasons.items():
            with self.subTest(status=status):
                self.reset()
                record = self.use_record()
                record[:6] = b"\x10\x20\x30\x40\x50\x60"
                record[0x2E] = 5
                record[0x2F] = 9
                record[0x30] = 7
                self.word(
                    "open_cfw_test_mram_pairing_failure_level_default"
                ).value = 7

                before = bytes(record)
                self.handle(0x123, status)

                self.assertEqual(bytes(record), before)
                self.assertEqual(
                    self.word(
                        "open_cfw_test_mram_pairing_failure_clear_count"
                    ).value,
                    1,
                )
                self.assertEqual(
                    self.word(
                        "open_cfw_test_mram_pairing_failure_clear_connection"
                    ).value,
                    0x23,
                )
                self.assertEqual(
                    self.word(
                        "open_cfw_test_mram_pairing_failure_clear_valid"
                    ).value,
                    7,
                )
                self.assertEqual(
                    self.word(
                        "open_cfw_test_mram_pairing_failure_clear_in_use"
                    ).value,
                    9,
                )
                address = self.logs()[1]
                self.assertEqual(
                    address[:13],
                    [
                        2,
                        0x0078A0D0,
                        0x006D84BC,
                        0x00769484,
                        0x880,
                        0x006D9F6C,
                        6,
                        0x60,
                        0x50,
                        0x40,
                        0x30,
                        0x20,
                        0x10,
                    ],
                )
                reason = self.logs()[2]
                self.assertEqual(
                    (reason[0], reason[4], reason[5]),
                    expected[:3],
                )
                trace = self.traces()[2]
                self.assertEqual(
                    (trace[0], trace[1], trace[2]),
                    (expected[3], expected[4], expected[4]),
                )
                if status == 0x42:
                    self.assertEqual(reason[7], 0x42)
                    self.assertEqual(trace[4], 0x42)

    def test_invalid_or_unkeyed_record_clears_only_flags(self) -> None:
        for valid, key_mask in ((0, 5), (3, 0), (2, 2)):
            with self.subTest(valid=valid, key_mask=key_mask):
                self.reset()
                record = self.use_record()
                record[:] = bytes(range(256))
                record[0x2E] = key_mask
                record[0x2F] = 0xA5
                record[0x30] = valid
                before = bytearray(record)
                self.word(
                    "open_cfw_test_mram_pairing_failure_level_default"
                ).value = 7

                self.handle(9, 1)

                before[0x2F] = 0
                before[0x30] = 0
                self.assertEqual(bytes(record), bytes(before))
                self.assertEqual(
                    self.word(
                        "open_cfw_test_mram_pairing_failure_clear_count"
                    ).value,
                    0,
                )
                diagnostic = self.logs()[-1]
                self.assertEqual(
                    diagnostic[:10],
                    [
                        4,
                        0x0078A0D0,
                        0x006D84BC,
                        0x00769484,
                        0x89F,
                        0x006A7814,
                        3,
                        9,
                        valid,
                        key_mask,
                    ],
                )
                self.assertEqual(
                    self.traces()[-1][:7],
                    [
                        0x10C00000,
                        0x0069E604,
                        0x0069E604,
                        3,
                        9,
                        valid,
                        key_mask,
                    ],
                )

    def test_complete_initial_and_missing_record_metadata(self) -> None:
        self.word(
            "open_cfw_test_mram_pairing_failure_level_default"
        ).value = 7

        self.handle(7, 0x0B)

        self.assertEqual(
            self.logs()[0][:9],
            [
                4,
                0x0078A0D0,
                0x006D84BC,
                0x00769484,
                0x872,
                0x006E6424,
                2,
                7,
                0x0B,
            ],
        )
        self.assertEqual(
            self.traces()[0][:6],
            [
                0x10800000,
                0x006DC514,
                0x006DC514,
                2,
                7,
                0x0B,
            ],
        )
        self.assertEqual(
            self.logs()[1][:8],
            [
                4,
                0x0078A0D0,
                0x006D84BC,
                0x00769484,
                0x8A6,
                0x006DF770,
                1,
                7,
            ],
        )
        self.assertEqual(
            self.traces()[1][:5],
            [
                0x10400000,
                0x006D9FD0,
                0x006D9FD0,
                1,
                7,
            ],
        )

    def test_structured_and_trace_gates_remain_independent(self) -> None:
        record = self.use_record()
        record[0x2E] = 1
        record[0x2F] = 1
        record[0x30] = 1
        self.word(
            "open_cfw_test_mram_pairing_failure_level_default"
        ).value = 2
        self.handle(1, 4)
        self.assertEqual(len(self.logs()), 3)
        self.assertEqual(self.traces(), [])

        self.reset()
        record = self.use_record()
        record[0x2E] = 1
        record[0x2F] = 1
        record[0x30] = 1
        self.word(
            "open_cfw_test_mram_pairing_failure_level_default"
        ).value = 4
        self.handle(1, 4)
        self.assertEqual(self.logs(), [])
        self.assertEqual(len(self.traces()), 3)

        self.reset()
        self.word(
            "open_cfw_test_mram_pairing_failure_level_default"
        ).value = 1
        self.handle(1, 4)
        self.assertEqual(self.logs(), [])
        self.assertEqual(len(self.traces()), 2)

    def test_randomized_control_model_and_byte_truncation(self) -> None:
        generator = random.Random(0x47C568)
        for _ in range(500):
            self.reset()
            has_record = generator.choice((False, True))
            connection = generator.getrandbits(32)
            status = generator.getrandbits(32)
            valid = generator.randrange(256)
            key_mask = generator.randrange(256)
            in_use = generator.randrange(256)
            if has_record:
                record = self.use_record()
                record[:] = generator.randbytes(256)
                record[0x2E] = key_mask
                record[0x2F] = in_use
                record[0x30] = valid
                before = bytearray(record)

            self.handle(connection, status)

            self.assertEqual(
                self.word(
                    "open_cfw_test_mram_pairing_failure_show_count"
                ).value,
                1,
            )
            self.assertEqual(
                self.word(
                    "open_cfw_test_mram_pairing_failure_lookup_connection"
                ).value,
                connection & 0xFF,
            )
            qualifies = (
                has_record
                and valid != 0
                and (key_mask & 5) != 0
            )
            self.assertEqual(
                self.word(
                    "open_cfw_test_mram_pairing_failure_clear_count"
                ).value,
                int(qualifies),
            )
            if has_record:
                if qualifies:
                    self.assertEqual(bytes(record), bytes(before))
                    self.assertEqual(
                        self.word(
                            "open_cfw_test_mram_pairing_failure_clear_connection"
                        ).value,
                        connection & 0xFF,
                    )
                else:
                    before[0x2F] = 0
                    before[0x30] = 0
                    self.assertEqual(bytes(record), bytes(before))

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "64b71edfafd134817f49af4833245eaa2d8a505f1ec080dfcc934c3031877c4a",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "31eceffd6a4115fecba478333d44f6b8d0031c52837e478d33bbd6075bfb1dfe",
        )


if __name__ == "__main__":
    unittest.main()
