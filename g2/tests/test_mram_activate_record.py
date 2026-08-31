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
SOURCE = COMPONENT_ROOT / "mram_activate_record.c"
FIXTURE = (
    OPENCFW_ROOT / "tests" / "fixtures" / "mram_activate_record_host.c"
)
CAPTURE_COUNT = 32
CAPTURE_WIDTH = 12


class MramActivateRecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "mram_activate_record.dylib"
            if sys.platform == "darwin"
            else "mram_activate_record.so"
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
        cls.reset = cls.loaded.open_cfw_test_mram_activate_reset
        cls.reset.argtypes = []
        cls.reset.restype = None
        cls.activate = cls.loaded.open_cfw_mram_activate_record
        cls.activate.argtypes = [ctypes.c_void_p, ctypes.c_uint]
        cls.activate.restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset()
        self.record = (ctypes.c_ubyte * 256)()
        self.order = (ctypes.c_uint * CAPTURE_COUNT).in_dll(
            self.loaded,
            "open_cfw_test_mram_activate_order",
        )
        self.update_state = (ctypes.c_uint * 4).in_dll(
            self.loaded,
            "open_cfw_test_mram_activate_update_state",
        )
        self.verify_state = (ctypes.c_uint * 4).in_dll(
            self.loaded,
            "open_cfw_test_mram_activate_verify_state",
        )
        self.levels = (ctypes.c_uint * CAPTURE_COUNT).in_dll(
            self.loaded,
            "open_cfw_test_mram_activate_levels",
        )
        self.logs = (
            ctypes.c_size_t * (CAPTURE_COUNT * CAPTURE_WIDTH)
        ).in_dll(
            self.loaded,
            "open_cfw_test_mram_activate_logs",
        )
        self.traces = (
            ctypes.c_size_t * (CAPTURE_COUNT * CAPTURE_WIDTH)
        ).in_dll(
            self.loaded,
            "open_cfw_test_mram_activate_traces",
        )

    def word(self, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(self.loaded, name)

    def pointer(self, name: str) -> ctypes.c_size_t:
        return ctypes.c_size_t.in_dll(self.loaded, name)

    def set_levels(self, values: list[int]) -> None:
        for index, value in enumerate(values):
            self.levels[index] = value
        self.word(
            "open_cfw_test_mram_activate_level_count"
        ).value = len(values)

    def captures(
        self,
        values: ctypes.Array[ctypes.c_size_t],
        count_name: str,
    ) -> list[list[int]]:
        count = self.word(count_name).value
        return [
            list(
                values[
                    index * CAPTURE_WIDTH:
                    (index + 1) * CAPTURE_WIDTH
                ]
            )
            for index in range(count)
        ]

    def test_mutates_record_in_stock_order_then_updates_and_verifies(
        self,
    ) -> None:
        self.record[0x2E] = 0x11
        self.record[0x2F] = 0x22
        self.record[0x30] = 0x33
        self.word("open_cfw_test_mram_activate_counter").value = 41
        self.word(
            "open_cfw_test_mram_activate_update_result"
        ).value = 0
        self.word(
            "open_cfw_test_mram_activate_verify_result"
        ).value = 0xDEADBEEF

        result = self.activate(self.record, 0x123456AB)

        self.assertEqual(result, 0x123456AB)
        self.assertEqual(
            (self.record[0x30], self.record[0x2F], self.record[0x2E]),
            (1, 1, 0xAB),
        )
        self.assertEqual(
            self.word("open_cfw_test_mram_activate_counter").value,
            42,
        )
        self.assertEqual(
            list(self.order)[
                :self.word(
                    "open_cfw_test_mram_activate_order_count"
                ).value
            ],
            [1, 2],
        )
        self.assertEqual(list(self.update_state), [1, 1, 0xAB, 42])
        self.assertEqual(list(self.verify_state), [1, 1, 0xAB, 42])
        self.assertEqual(
            (
                self.pointer(
                    "open_cfw_test_mram_activate_update_record"
                ).value,
                self.pointer(
                    "open_cfw_test_mram_activate_verify_record"
                ).value,
            ),
            (ctypes.addressof(self.record), ctypes.addressof(self.record)),
        )

    def test_counter_wraps_as_unsigned_32_bit_value(self) -> None:
        self.word(
            "open_cfw_test_mram_activate_counter"
        ).value = 0xFFFFFFFF

        self.activate(self.record, 0x5A)

        timestamp = ctypes.c_uint.from_buffer(
            self.record,
            0xC4,
        ).value
        self.assertEqual(
            self.word("open_cfw_test_mram_activate_counter").value,
            0,
        )
        self.assertEqual(timestamp, 0)
        self.assertEqual(list(self.update_state), [1, 1, 0x5A, 0])
        self.assertEqual(list(self.verify_state), [1, 1, 0x5A, 0])

    def test_verifier_always_runs_and_its_result_is_ignored(self) -> None:
        self.word(
            "open_cfw_test_mram_activate_update_result"
        ).value = 0xFFFFFFFF
        self.word(
            "open_cfw_test_mram_activate_verify_result"
        ).value = 0

        result = self.activate(self.record, 0xCAFEBE7E)

        self.assertEqual(result, 0xCAFEBE7E)
        self.assertEqual(
            list(self.order)[
                :self.word(
                    "open_cfw_test_mram_activate_order_count"
                ).value
            ],
            [1, 2],
        )
        self.assertEqual(
            self.pointer(
                "open_cfw_test_mram_activate_verify_record"
            ).value,
            ctypes.addressof(self.record),
        )

    def test_success_diagnostic_requires_update_result_exactly_one(
        self,
    ) -> None:
        self.set_levels([7] * CAPTURE_COUNT)
        self.word(
            "open_cfw_test_mram_activate_update_result"
        ).value = 2

        self.activate(self.record, 0x44)

        self.assertEqual(
            self.word("open_cfw_test_mram_activate_log_count").value,
            2,
        )
        self.assertEqual(
            self.word("open_cfw_test_mram_activate_trace_count").value,
            2,
        )

    def test_all_enabled_diagnostics_match_stock_metadata(self) -> None:
        self.set_levels([7] * CAPTURE_COUNT)
        self.word(
            "open_cfw_test_mram_activate_update_result"
        ).value = 1

        self.activate(self.record, 0x123456AB)

        logs = self.captures(
            self.logs,
            "open_cfw_test_mram_activate_log_count",
        )
        traces = self.captures(
            self.traces,
            "open_cfw_test_mram_activate_trace_count",
        )
        self.assertEqual(
            [row[:7] for row in logs],
            [
                [
                    4,
                    0x0078A0D0,
                    0x006D84BC,
                    0x0077DDE4,
                    0x2C5,
                    0x0071267C,
                    0xAB,
                ],
                [
                    4,
                    0x0078A0D0,
                    0x006D84BC,
                    0x0077DDE4,
                    0x2CC,
                    0x006EB538,
                    0xAB,
                ],
                [
                    4,
                    0x0078A0D0,
                    0x006D84BC,
                    0x0077DDE4,
                    0x2D3,
                    0x0071BF90,
                    0,
                ],
            ],
        )
        self.assertEqual(
            [row[:4] for row in traces],
            [
                [0x10400000, 0x006F84D4, 0x006F84D4, 0xAB],
                [0x10400000, 0x006DF5A4, 0x006DF5A4, 0xAB],
                [0x10000000, 0x0070027C, 0x0070027C, 0],
            ],
        )

    def test_structured_only_gate_suppresses_trace(self) -> None:
        self.set_levels([2] * 6)

        self.activate(self.record, 0xA5)

        self.assertEqual(
            self.word("open_cfw_test_mram_activate_log_count").value,
            2,
        )
        self.assertEqual(
            self.word("open_cfw_test_mram_activate_trace_count").value,
            0,
        )

    def test_trace_fallback_gate_uses_second_level_sample_bit_two(
        self,
    ) -> None:
        self.set_levels([0, 0, 4, 0, 0, 4])

        self.activate(self.record, 0xA5)

        self.assertEqual(
            self.word("open_cfw_test_mram_activate_log_count").value,
            0,
        )
        traces = self.captures(
            self.traces,
            "open_cfw_test_mram_activate_trace_count",
        )
        self.assertEqual(
            [row[:4] for row in traces],
            [
                [0x10400000, 0x006F84D4, 0x006F84D4, 0xA5],
                [0x10400000, 0x006DF5A4, 0x006DF5A4, 0xA5],
            ],
        )

    def test_source_and_fixture_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "757e896aabc1b640efdf4292c506d356d857e62a3e92404242343bcd13704336",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "3a93b6a3290e5ed84c73c668cd6e47ce34869adc53154f28afda799c9cd223cf",
        )


if __name__ == "__main__":
    unittest.main()
