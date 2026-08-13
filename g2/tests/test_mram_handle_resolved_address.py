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
SOURCE = COMPONENT_ROOT / "mram_handle_resolved_address.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "mram_handle_resolved_address_host.c"
)
CAPTURE_COUNT = 24
CAPTURE_WIDTH = 13
RECORD_SIZE = 200
RECORD_COUNT = 10


class MramHandleResolvedAddressTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "mram_handle_resolved_address.dylib"
            if sys.platform == "darwin"
            else "mram_handle_resolved_address.so"
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
        cls.reset = cls.loaded.open_cfw_test_mram_resolved_reset
        cls.reset.argtypes = []
        cls.reset.restype = None
        cls.handle = cls.loaded.open_cfw_mram_handle_resolved_address
        cls.handle.argtypes = [ctypes.c_void_p, ctypes.c_uint]
        cls.handle.restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset()
        self.records = (
            ctypes.c_ubyte * (RECORD_COUNT * RECORD_SIZE)
        ).in_dll(
            self.loaded,
            "open_cfw_test_mram_resolved_records",
        )
        self.order = (ctypes.c_uint * CAPTURE_COUNT).in_dll(
            self.loaded,
            "open_cfw_test_mram_resolved_order",
        )
        self.levels = (ctypes.c_uint * CAPTURE_COUNT).in_dll(
            self.loaded,
            "open_cfw_test_mram_resolved_levels",
        )
        self.logs = (
            ctypes.c_size_t * (CAPTURE_COUNT * CAPTURE_WIDTH)
        ).in_dll(
            self.loaded,
            "open_cfw_test_mram_resolved_logs",
        )
        self.log_widths = (ctypes.c_uint * CAPTURE_COUNT).in_dll(
            self.loaded,
            "open_cfw_test_mram_resolved_log_widths",
        )
        self.traces = (
            ctypes.c_size_t * (CAPTURE_COUNT * CAPTURE_WIDTH)
        ).in_dll(
            self.loaded,
            "open_cfw_test_mram_resolved_traces",
        )
        self.trace_widths = (ctypes.c_uint * CAPTURE_COUNT).in_dll(
            self.loaded,
            "open_cfw_test_mram_resolved_trace_widths",
        )

    def word(self, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(self.loaded, name)

    def set_record(
        self,
        index: int,
        *,
        allocated: int = 1,
        confirmed: int = 1,
        key_mask: int = 0,
    ) -> None:
        base = index * RECORD_SIZE
        self.records[base + 0x2F] = allocated
        self.records[base + 0x30] = confirmed
        self.records[base + 0x2E] = key_mask

    def set_levels(self, values: list[int]) -> None:
        for index, value in enumerate(values):
            self.levels[index] = value
        self.word(
            "open_cfw_test_mram_resolved_level_count"
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
                "open_cfw_test_mram_resolved_order_count"
            ).value
        ]

    def test_invalid_index_or_record_is_rejected_before_address_use(
        self,
    ) -> None:
        cases = (
            ("index", 10, 0, 0),
            ("allocated", 9, 0, 1),
            ("confirmed", 9, 1, 0),
        )
        for name, index, allocated, confirmed in cases:
            with self.subTest(name=name):
                self.reset()
                self.set_record(
                    9,
                    allocated=allocated,
                    confirmed=confirmed,
                    key_mask=1,
                )
                self.set_levels([3, 3])

                self.assertEqual(self.handle(None, index), 0)

                self.assertEqual(
                    self.captured(
                        self.logs,
                        self.log_widths,
                        "open_cfw_test_mram_resolved_log_count",
                    ),
                    [[
                        1,
                        0x0078A0D0,
                        0x006D84BC,
                        0x0077511C,
                        0x435,
                        0x0071C038,
                    ]],
                )
                self.assertEqual(
                    self.captured(
                        self.traces,
                        self.trace_widths,
                        "open_cfw_test_mram_resolved_trace_count",
                    ),
                    [[0x04000000, 0x00700304, 0x00700304]],
                )

    def test_valid_ltk_reports_resolved_address_and_returns_one(self) -> None:
        address = (ctypes.c_ubyte * 6)(1, 2, 3, 4, 5, 0xA6)
        self.set_record(3, key_mask=0xA5)
        self.set_levels([3, 3, 3, 3])

        result = self.handle(address, 3)

        self.assertEqual(result, 1)
        self.assertEqual(
            self.observed_order(),
            [1, 2, 1, 3, 1, 2, 1, 3],
        )
        self.assertEqual(
            self.captured(
                self.logs,
                self.log_widths,
                "open_cfw_test_mram_resolved_log_count",
            ),
            [
                [
                    4,
                    0x0078A0D0,
                    0x006D84BC,
                    0x0077511C,
                    0x43B,
                    0x006D5ED0,
                    3,
                    0xA6,
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
                    0x0077511C,
                    0x440,
                    0x006EB5D8,
                ],
            ],
        )
        self.assertEqual(
            self.captured(
                self.traces,
                self.trace_widths,
                "open_cfw_test_mram_resolved_trace_count",
            ),
            [
                [
                    0x11C00000,
                    0x006D4B20,
                    0x006D4B20,
                    3,
                    0xA6,
                    5,
                    4,
                    3,
                    2,
                    1,
                ],
                [0x10000000, 0x006E2540, 0x006E2540],
            ],
        )

    def test_missing_ltk_bit_returns_zero_with_failure_diagnostic(
        self,
    ) -> None:
        address = (ctypes.c_ubyte * 6)(6, 5, 4, 3, 2, 1)
        self.set_record(7, key_mask=0xFE)
        self.set_levels([3, 3, 3, 3])

        result = self.handle(address, 7)

        self.assertEqual(result, 0)
        self.assertEqual(
            self.captured(
                self.logs,
                self.log_widths,
                "open_cfw_test_mram_resolved_log_count",
            )[-1],
            [
                2,
                0x0078A0D0,
                0x006D84BC,
                0x0077511C,
                0x449,
                0x006E62D4,
            ],
        )
        self.assertEqual(
            self.captured(
                self.traces,
                self.trace_widths,
                "open_cfw_test_mram_resolved_trace_count",
            )[-1],
            [0x08000000, 0x006DC4B4, 0x006DC4B4],
        )

    def test_index_is_truncated_to_sixteen_bits_without_null_guard(
        self,
    ) -> None:
        self.set_record(1, key_mask=1)

        result = self.handle(None, 0xABCD0001)

        self.assertEqual(result, 1)
        self.assertEqual(self.word(
            "open_cfw_test_mram_resolved_log_count"
        ).value, 0)
        self.assertEqual(self.word(
            "open_cfw_test_mram_resolved_trace_count"
        ).value, 0)

    def test_trace_fallback_uses_second_level_read(self) -> None:
        self.set_levels([0, 0, 4])

        self.assertEqual(self.handle(None, 10), 0)

        self.assertEqual(self.word(
            "open_cfw_test_mram_resolved_log_count"
        ).value, 0)
        self.assertEqual(self.word(
            "open_cfw_test_mram_resolved_level_index"
        ).value, 3)
        self.assertEqual(self.observed_order(), [1, 1, 1, 3])
        self.assertEqual(
            self.captured(
                self.traces,
                self.trace_widths,
                "open_cfw_test_mram_resolved_trace_count",
            ),
            [[0x04000000, 0x00700304, 0x00700304]],
        )

    def test_sources_are_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "d5747f9ba54780c0d23a10fac78da5169961fe61682bcbf2552b84a0e71c58ba",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "fdcc0a92089a051cc77c568d7b6a7f561fc259e087d26eeeefe0a5144c7266f6",
        )


if __name__ == "__main__":
    unittest.main()
