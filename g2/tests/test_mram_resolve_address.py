from __future__ import annotations

import os

import ctypes
import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


OPENCFW_ROOT = Path(__file__).resolve().parent.parent
COMPONENT_ROOT = OPENCFW_ROOT / "components" / "apollo_main" / "core_overlay"
SOURCE = COMPONENT_ROOT / "mram_resolve_address.c"
FIXTURE = (
    OPENCFW_ROOT / "tests" / "fixtures" / "mram_resolve_address_host.c"
)
CAPTURE_COUNT = 32
CAPTURE_WIDTH = 12
RECORD_SIZE = 200
RECORD_COUNT = 10


class MramResolveAddressTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "mram_resolve_address.dylib"
            if sys.platform == "darwin"
            else "mram_resolve_address.so"
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
        cls.reset = cls.loaded.open_cfw_test_mram_resolve_reset
        cls.reset.argtypes = []
        cls.reset.restype = None
        cls.resolve = (
            cls.loaded.open_cfw_mram_resolve_and_connect_by_address
        )
        cls.resolve.argtypes = [ctypes.c_uint, ctypes.c_void_p]
        cls.resolve.restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset()
        self.records = (
            ctypes.c_ubyte * (RECORD_COUNT * RECORD_SIZE)
        ).in_dll(
            self.loaded,
            "open_cfw_test_mram_resolve_records",
        )
        self.order = (ctypes.c_uint * CAPTURE_COUNT).in_dll(
            self.loaded,
            "open_cfw_test_mram_resolve_order",
        )
        self.levels = (ctypes.c_uint * CAPTURE_COUNT).in_dll(
            self.loaded,
            "open_cfw_test_mram_resolve_levels",
        )
        self.logs = (
            ctypes.c_size_t * (CAPTURE_COUNT * CAPTURE_WIDTH)
        ).in_dll(
            self.loaded,
            "open_cfw_test_mram_resolve_logs",
        )
        self.log_widths = (ctypes.c_uint * CAPTURE_COUNT).in_dll(
            self.loaded,
            "open_cfw_test_mram_resolve_log_widths",
        )
        self.traces = (
            ctypes.c_size_t * (CAPTURE_COUNT * CAPTURE_WIDTH)
        ).in_dll(
            self.loaded,
            "open_cfw_test_mram_resolve_traces",
        )
        self.trace_widths = (ctypes.c_uint * CAPTURE_COUNT).in_dll(
            self.loaded,
            "open_cfw_test_mram_resolve_trace_widths",
        )

    def word(self, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(self.loaded, name)

    def signed_word(self, name: str) -> ctypes.c_int:
        return ctypes.c_int.in_dll(self.loaded, name)

    def pointer(self, name: str) -> ctypes.c_void_p:
        return ctypes.c_void_p.in_dll(self.loaded, name)

    def record_address(self, index: int) -> int:
        return ctypes.addressof(self.records) + index * RECORD_SIZE

    def set_record(
        self,
        index: int,
        *,
        allocated: int = 1,
        confirmed: int = 1,
        irk: int = 0,
        owner: int = 0,
    ) -> None:
        base = index * RECORD_SIZE
        self.records[base + 0x2F] = allocated
        self.records[base + 0x30] = confirmed
        self.records[base + 0x2E] = 4 if irk else 0
        self.records[base + 6] = owner

    def set_levels(self, values: list[int]) -> None:
        for index, value in enumerate(values):
            self.levels[index] = value
        self.word(
            "open_cfw_test_mram_resolve_level_count"
        ).value = len(values)

    def captured(
        self,
        values: ctypes.Array[ctypes.c_size_t],
        widths: ctypes.Array[ctypes.c_uint],
        count_name: str,
    ) -> list[list[int]]:
        count = self.word(count_name).value
        return [
            list(
                values[
                    index * CAPTURE_WIDTH:
                    index * CAPTURE_WIDTH + widths[index]
                ]
            )
            for index in range(count)
        ]

    def observed_order(self) -> list[int]:
        return list(self.order)[
            :self.word(
                "open_cfw_test_mram_resolve_order_count"
            ).value
        ]

    def test_null_address_is_rejected_before_owner_mapping(self) -> None:
        self.set_levels([3, 3])

        result = self.resolve(0x12345678, None)

        self.assertEqual(result, 0)
        self.assertEqual(self.word(
            "open_cfw_test_mram_resolve_map_argument"
        ).value, 0)
        self.assertEqual(self.word(
            "open_cfw_test_mram_resolve_compare_count"
        ).value, 0)
        self.assertEqual(self.word(
            "open_cfw_test_mram_resolve_queue_count"
        ).value, 0)
        self.assertEqual(self.observed_order(), [1, 2, 1, 3])
        self.assertEqual(
            self.captured(
                self.logs,
                self.log_widths,
                "open_cfw_test_mram_resolve_log_count",
            ),
            [[
                1,
                0x0078A0D0,
                0x006D84BC,
                0x0075DE50,
                0x3E6,
                0x007126B8,
            ]],
        )
        self.assertEqual(
            self.captured(
                self.traces,
                self.trace_widths,
                "open_cfw_test_mram_resolve_trace_count",
            ),
            [[0x04000000, 0x006F851C, 0x006F851C]],
        )

    def test_resolvable_random_address_queues_first_valid_irk(self) -> None:
        address = (ctypes.c_ubyte * 6)(1, 2, 3, 4, 5, 0x7F)
        self.set_record(0, allocated=0, confirmed=1, irk=1)
        self.set_record(1, allocated=1, confirmed=0, irk=1)
        self.set_record(2, allocated=1, confirmed=1, irk=0)
        self.set_record(3, allocated=1, confirmed=1, irk=1)
        self.set_record(4, allocated=1, confirmed=1, irk=1)
        self.set_levels([3, 3, 3, 3])

        result = self.resolve(0x101, address)

        self.assertEqual(result, 1)
        self.assertEqual(self.word(
            "open_cfw_test_mram_resolve_queue_count"
        ).value, 1)
        self.assertEqual(
            self.pointer(
                "open_cfw_test_mram_resolve_queue_address"
            ).value,
            ctypes.addressof(address),
        )
        self.assertEqual(
            self.pointer("open_cfw_test_mram_resolve_queue_irk").value,
            self.record_address(3) + 7,
        )
        self.assertEqual(self.word(
            "open_cfw_test_mram_resolve_queue_index"
        ).value, 3)
        self.assertEqual(self.word(
            "open_cfw_test_mram_resolve_compare_count"
        ).value, 0)
        self.assertEqual(
            self.observed_order(),
            [1, 2, 1, 3, 1, 2, 1, 3, 6],
        )
        self.assertEqual(
            self.captured(
                self.logs,
                self.log_widths,
                "open_cfw_test_mram_resolve_log_count",
            ),
            [
                [
                    4,
                    0x0078A0D0,
                    0x006D84BC,
                    0x0075DE50,
                    0x3EE,
                    0x006DC454,
                    0x7F,
                    5,
                    4,
                    3,
                    2,
                    1,
                ],
                [
                    4,
                    0x0078A0D0,
                    0x006D84BC,
                    0x0075DE50,
                    0x3F8,
                    0x006EB588,
                    3,
                ],
            ],
        )
        self.assertEqual(
            self.captured(
                self.traces,
                self.trace_widths,
                "open_cfw_test_mram_resolve_trace_count",
            ),
            [
                [
                    0x11800000,
                    0x006A6EE4,
                    0x006A6EE4,
                    0x7F,
                    5,
                    4,
                    3,
                    2,
                    1,
                ],
                [0x10400000, 0x006DF600, 0x006DF600, 3],
            ],
        )

    def test_resolvable_random_address_without_irk_fails(self) -> None:
        address = (ctypes.c_ubyte * 6)(6, 5, 4, 3, 2, 0x40)
        self.set_record(0, allocated=1, confirmed=0, irk=1)
        self.set_record(9, allocated=1, confirmed=1, irk=0)
        self.set_levels([3, 3, 3, 3])

        result = self.resolve(1, address)

        self.assertEqual(result, 0)
        self.assertEqual(self.word(
            "open_cfw_test_mram_resolve_queue_count"
        ).value, 0)
        self.assertEqual(
            self.captured(
                self.logs,
                self.log_widths,
                "open_cfw_test_mram_resolve_log_count",
            )[-1],
            [
                2,
                0x0078A0D0,
                0x006D84BC,
                0x0075DE50,
                0x404,
                0x006F197C,
            ],
        )
        self.assertEqual(
            self.captured(
                self.traces,
                self.trace_widths,
                "open_cfw_test_mram_resolve_trace_count",
            )[-1],
            [0x08000000, 0x006E2490, 0x006E2490],
        )

    def test_nonrandom_address_maps_low_owner_byte_and_matches(self) -> None:
        address = (ctypes.c_ubyte * 6)(10, 20, 30, 40, 50, 0x80)
        self.word(
            "open_cfw_test_mram_resolve_map_result"
        ).value = 0x1234
        self.set_record(0, allocated=0, owner=0x34)
        self.set_record(1, confirmed=0, owner=0x34)
        self.set_record(2, owner=0x35)
        self.set_record(3, owner=0x34)
        self.set_record(5, owner=0x34)
        self.signed_word(
            "open_cfw_test_mram_resolve_compare_match_index"
        ).value = 5
        self.set_levels([3, 3])

        result = self.resolve(0xABCD0102, address)

        self.assertEqual(result, 1)
        self.assertEqual(self.word(
            "open_cfw_test_mram_resolve_map_argument"
        ).value, 2)
        self.assertEqual(self.word(
            "open_cfw_test_mram_resolve_compare_count"
        ).value, 2)
        self.assertEqual(
            self.pointer(
                "open_cfw_test_mram_resolve_compare_record"
            ).value,
            self.record_address(5),
        )
        self.assertEqual(
            self.pointer(
                "open_cfw_test_mram_resolve_compare_address"
            ).value,
            ctypes.addressof(address),
        )
        self.assertEqual(
            self.captured(
                self.logs,
                self.log_widths,
                "open_cfw_test_mram_resolve_log_count",
            ),
            [[
                4,
                0x0078A0D0,
                0x006D84BC,
                0x0075DE50,
                0x419,
                0x006F19C8,
            ]],
        )
        self.assertEqual(
            self.captured(
                self.traces,
                self.trace_widths,
                "open_cfw_test_mram_resolve_trace_count",
            ),
            [[0x10000000, 0x006E24E8, 0x006E24E8]],
        )

    def test_nonrandom_address_without_match_scans_all_candidates(
        self,
    ) -> None:
        address = (ctypes.c_ubyte * 6)(10, 20, 30, 40, 50, 0xC0)
        self.word(
            "open_cfw_test_mram_resolve_map_result"
        ).value = 0x77
        self.set_record(0, owner=0x77)
        self.set_record(9, owner=0x77)
        self.set_levels([3, 3])

        result = self.resolve(3, address)

        self.assertEqual(result, 0)
        self.assertEqual(self.word(
            "open_cfw_test_mram_resolve_compare_count"
        ).value, 2)
        self.assertEqual(self.word(
            "open_cfw_test_mram_resolve_queue_count"
        ).value, 0)
        self.assertEqual(
            self.captured(
                self.logs,
                self.log_widths,
                "open_cfw_test_mram_resolve_log_count",
            ),
            [[
                2,
                0x0078A0D0,
                0x006D84BC,
                0x0075DE50,
                0x41F,
                0x0071C000,
            ]],
        )
        self.assertEqual(
            self.captured(
                self.traces,
                self.trace_widths,
                "open_cfw_test_mram_resolve_trace_count",
            ),
            [[0x08000000, 0x007092A4, 0x007092A4]],
        )

    def test_resolvable_random_gate_requires_both_address_conditions(
        self,
    ) -> None:
        for owner, final_byte in ((1, 0x80), (2, 0x40)):
            with self.subTest(owner=owner, final_byte=final_byte):
                self.reset()
                address = (
                    ctypes.c_ubyte * 6
                )(1, 2, 3, 4, 5, final_byte)
                self.word(
                    "open_cfw_test_mram_resolve_map_result"
                ).value = 0x22
                self.set_record(0, owner=0x22, irk=1)
                self.signed_word(
                    "open_cfw_test_mram_resolve_compare_match_index"
                ).value = 0

                self.assertEqual(self.resolve(owner, address), 1)

                self.assertEqual(self.word(
                    "open_cfw_test_mram_resolve_map_argument"
                ).value, owner)
                self.assertEqual(self.word(
                    "open_cfw_test_mram_resolve_compare_count"
                ).value, 1)
                self.assertEqual(self.word(
                    "open_cfw_test_mram_resolve_queue_count"
                ).value, 0)

    def test_trace_fallback_uses_second_level_read(self) -> None:
        self.set_levels([0, 0, 4])

        self.assertEqual(self.resolve(0, None), 0)

        self.assertEqual(self.word(
            "open_cfw_test_mram_resolve_log_count"
        ).value, 0)
        self.assertEqual(self.word(
            "open_cfw_test_mram_resolve_level_index"
        ).value, 3)
        self.assertEqual(self.observed_order(), [1, 1, 1, 3])
        self.assertEqual(
            self.captured(
                self.traces,
                self.trace_widths,
                "open_cfw_test_mram_resolve_trace_count",
            ),
            [[0x04000000, 0x006F851C, 0x006F851C]],
        )

    def test_sources_are_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "ca1c9dd34f276a24c9d2bcd39b9ee1ee706d88e9a29e17c676dc940e20594761",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "25c87c424c0703d3b2cf5ca60bc90a9bdaed538a17af3d3cb751ec164024af69",
        )


if __name__ == "__main__":
    unittest.main()
