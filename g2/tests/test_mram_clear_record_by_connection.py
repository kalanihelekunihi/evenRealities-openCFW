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
SOURCE = COMPONENT_ROOT / "mram_clear_record_by_connection.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "mram_clear_record_by_connection_host.c"
)
CAPTURE_COUNT = 128
CAPTURE_WIDTH = 16


class MramClearRecordByConnectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "mram_clear_record_by_connection.dylib"
            if sys.platform == "darwin"
            else "mram_clear_record_by_connection.so"
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
        cls.reset = cls.loaded.open_cfw_test_mram_clear_connection_reset
        cls.reset.argtypes = []
        cls.reset.restype = None
        cls.clear = cls.loaded.open_cfw_mram_clear_record_by_connection
        cls.clear.argtypes = [ctypes.c_uint]
        cls.clear.restype = None

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
            "open_cfw_test_mram_clear_connection_record",
        )

    def use_record(self) -> ctypes.Array:
        record = self.record()
        self.pointer(
            "open_cfw_test_mram_clear_connection_lookup_result"
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
            "open_cfw_test_mram_clear_connection_logs",
            "open_cfw_test_mram_clear_connection_log_count",
        )

    def traces(self) -> list[list[int]]:
        return self.captures(
            "open_cfw_test_mram_clear_connection_traces",
            "open_cfw_test_mram_clear_connection_trace_count",
        )

    def order(self) -> list[int]:
        count = self.word(
            "open_cfw_test_mram_clear_connection_order_count"
        ).value
        return list(
            self.words(
                "open_cfw_test_mram_clear_connection_order",
                CAPTURE_COUNT,
            )[:count]
        )

    def configure_full_logging(self) -> None:
        self.word(
            "open_cfw_test_mram_clear_connection_level_default"
        ).value = 7

    def test_missing_record_reports_connection_and_truncates_handle(
        self,
    ) -> None:
        self.configure_full_logging()

        self.clear(0x123456AB)

        self.assertEqual(
            self.word(
                "open_cfw_test_mram_clear_connection_lookup_connection"
            ).value,
            0xAB,
        )
        self.assertEqual(self.order(), [4, 1, 2, 1, 3])
        self.assertEqual(
            self.logs()[0][:8],
            [
                4,
                0x0078A0D0,
                0x006D84BC,
                0x007694A0,
                0x8D0,
                0x006E6520,
                1,
                0xAB,
            ],
        )
        self.assertEqual(
            self.traces()[0][:5],
            [
                0x10400000,
                0x006DC634,
                0x006DC634,
                1,
                0xAB,
            ],
        )
        self.assertEqual(
            self.word(
                "open_cfw_test_mram_clear_connection_clear_count"
            ).value,
            0,
        )
        self.assertEqual(
            self.word(
                "open_cfw_test_mram_clear_connection_reload_count"
            ).value,
            0,
        )

    def test_qualifying_record_clears_by_address_then_reloads(
        self,
    ) -> None:
        record = self.use_record()
        record[:7] = b"\x10\x20\x30\x40\x50\x60\xA5"
        record[0x2E] = 5
        record[0x2F] = 9
        record[0x30] = 7
        before = bytes(record)
        self.configure_full_logging()

        self.clear(0x101)

        self.assertEqual(bytes(record), before)
        self.assertEqual(
            self.word(
                "open_cfw_test_mram_clear_connection_clear_count"
            ).value,
            1,
        )
        self.assertEqual(
            self.word(
                "open_cfw_test_mram_clear_connection_clear_owner"
            ).value,
            0xA5,
        )
        self.assertEqual(
            ctypes.c_size_t.in_dll(
                self.loaded,
                "open_cfw_test_mram_clear_connection_clear_address",
            ).value,
            ctypes.addressof(record),
        )
        self.assertEqual(
            self.word(
                "open_cfw_test_mram_clear_connection_reload_count"
            ).value,
            1,
        )
        self.assertLess(self.order().index(5), self.order().index(6))
        self.assertEqual(
            self.logs()[0][:13],
            [
                2,
                0x0078A0D0,
                0x006D84BC,
                0x007694A0,
                0x8BB,
                0x006DC5D4,
                6,
                0x60,
                0x50,
                0x40,
                0x30,
                0x20,
                0x10,
            ],
        )
        self.assertEqual(
            self.traces()[0][:10],
            [
                0x09800000,
                0x006D858C,
                0x006D858C,
                6,
                0x60,
                0x50,
                0x40,
                0x30,
                0x20,
                0x10,
            ],
        )
        self.assertEqual(
            self.logs()[1][:7],
            [
                1,
                0x0078A0D0,
                0x006D84BC,
                0x007694A0,
                0x8C2,
                0x007005F0,
                0,
            ],
        )
        self.assertEqual(
            self.traces()[1][:4],
            [0x04000000, 0x006EB808, 0x006EB808, 0],
        )

    def test_clear_failure_is_reported_and_still_reloads(self) -> None:
        record = self.use_record()
        record[6] = 0x42
        record[0x2E] = 1
        record[0x30] = 1
        self.word(
            "open_cfw_test_mram_clear_connection_clear_result"
        ).value = 0x101
        self.configure_full_logging()

        self.clear(9)

        self.assertEqual(
            self.word(
                "open_cfw_test_mram_clear_connection_reload_count"
            ).value,
            1,
        )
        self.assertEqual(
            self.logs()[1][:7],
            [
                4,
                0x0078A0D0,
                0x006D84BC,
                0x007694A0,
                0x8C0,
                0x006F1AAC,
                0,
            ],
        )
        self.assertEqual(
            self.traces()[1][:4],
            [0x10000000, 0x006E2648, 0x006E2648, 0],
        )
        self.assertEqual(self.order()[-1], 6)

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
                self.configure_full_logging()

                self.clear(0x109)

                before[0x2F] = 0
                before[0x30] = 0
                self.assertEqual(bytes(record), bytes(before))
                self.assertEqual(
                    self.word(
                        "open_cfw_test_mram_clear_connection_clear_count"
                    ).value,
                    0,
                )
                self.assertEqual(
                    self.word(
                        "open_cfw_test_mram_clear_connection_reload_count"
                    ).value,
                    0,
                )
                self.assertEqual(
                    self.logs()[0][:10],
                    [
                        4,
                        0x0078A0D0,
                        0x006D84BC,
                        0x007694A0,
                        0x8C9,
                        0x006DA034,
                        3,
                        9,
                        valid,
                        key_mask,
                    ],
                )
                self.assertEqual(
                    self.traces()[0][:7],
                    [
                        0x10C00000,
                        0x006D6BE0,
                        0x006D6BE0,
                        3,
                        9,
                        valid,
                        key_mask,
                    ],
                )

    def test_structured_and_trace_gates_remain_independent(self) -> None:
        record = self.use_record()
        record[0x2E] = 1
        record[0x30] = 1
        self.word(
            "open_cfw_test_mram_clear_connection_level_default"
        ).value = 2
        self.clear(1)
        self.assertEqual(len(self.logs()), 2)
        self.assertEqual(self.traces(), [])

        self.reset()
        record = self.use_record()
        record[0x2E] = 1
        record[0x30] = 1
        self.word(
            "open_cfw_test_mram_clear_connection_level_default"
        ).value = 4
        self.clear(1)
        self.assertEqual(self.logs(), [])
        self.assertEqual(len(self.traces()), 2)

        self.reset()
        self.word(
            "open_cfw_test_mram_clear_connection_level_default"
        ).value = 1
        self.clear(1)
        self.assertEqual(self.logs(), [])
        self.assertEqual(len(self.traces()), 1)

    def test_randomized_control_model_and_byte_truncation(self) -> None:
        generator = random.Random(0x47C8CC)
        for _ in range(500):
            self.reset()
            has_record = generator.choice((False, True))
            connection = generator.getrandbits(32)
            valid = generator.randrange(256)
            key_mask = generator.randrange(256)
            clear_result = generator.getrandbits(32)
            if has_record:
                record = self.use_record()
                record[:] = generator.randbytes(256)
                record[0x2E] = key_mask
                record[0x30] = valid
                before = bytearray(record)
            self.word(
                "open_cfw_test_mram_clear_connection_clear_result"
            ).value = clear_result

            self.clear(connection)

            self.assertEqual(
                self.word(
                    "open_cfw_test_mram_clear_connection_lookup_connection"
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
                    "open_cfw_test_mram_clear_connection_clear_count"
                ).value,
                int(qualifies),
            )
            self.assertEqual(
                self.word(
                    "open_cfw_test_mram_clear_connection_reload_count"
                ).value,
                int(qualifies),
            )
            if has_record:
                if qualifies:
                    self.assertEqual(bytes(record), bytes(before))
                else:
                    before[0x2F] = 0
                    before[0x30] = 0
                    self.assertEqual(bytes(record), bytes(before))

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "413a5788e04dc584f859f36b408053eaafed505173843efdac59193da65dcd86",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "f89ef24388b8df7efa8bb6191642b84e2bd5c79c7e76a6000cdd98acfb92473f",
        )


if __name__ == "__main__":
    unittest.main()
