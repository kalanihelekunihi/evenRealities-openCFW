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
SOURCE = COMPONENT_ROOT / "mram_clear_record_by_mac.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "mram_clear_record_by_mac_host.c"
)
CAPTURE_COUNT = 64


class MramClearRecordByMacTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "mram_clear_record_by_mac.dylib"
            if sys.platform == "darwin"
            else "mram_clear_record_by_mac.so"
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
        cls.reset = cls.loaded.open_cfw_test_mram_clear_reset
        cls.reset.argtypes = []
        cls.reset.restype = None
        cls.clear = (
            cls.loaded.open_cfw_mram_clear_record_by_mac_address
        )
        cls.clear.argtypes = [ctypes.c_uint, ctypes.c_void_p]
        cls.clear.restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset()

    def word(self, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(self.loaded, name)

    def pointer(self, name: str) -> ctypes.c_size_t:
        return ctypes.c_size_t.in_dll(self.loaded, name)

    def words(self, name: str, count: int) -> ctypes.Array:
        return (ctypes.c_uint * count).in_dll(self.loaded, name)

    def addresses(self, name: str, count: int) -> ctypes.Array:
        return (ctypes.c_size_t * count).in_dll(self.loaded, name)

    def order(self) -> list[int]:
        count = self.word(
            "open_cfw_test_mram_clear_order_count"
        ).value
        return list(
            self.words(
                "open_cfw_test_mram_clear_order",
                CAPTURE_COUNT,
            )[:count]
        )

    def configure_full_logging(self) -> None:
        self.word(
            "open_cfw_test_mram_clear_level_default"
        ).value = 7

    def test_null_address_reports_invalid_pointer_without_lookup(
        self,
    ) -> None:
        self.configure_full_logging()

        result = self.clear(3, None)

        self.assertEqual(result, 0)
        self.assertEqual(self.order(), [1, 2, 1, 3])
        self.assertEqual(
            self.word("open_cfw_test_mram_clear_find_count").value,
            0,
        )
        logs = self.addresses(
            "open_cfw_test_mram_clear_logs",
            CAPTURE_COUNT * 6,
        )
        self.assertEqual(
            list(logs[:6]),
            [
                1,
                0x0078A0D0,
                0x006D84BC,
                0x00769414,
                0x74C,
                0x0071C0E0,
            ],
        )
        traces = self.addresses(
            "open_cfw_test_mram_clear_traces",
            CAPTURE_COUNT * 3,
        )
        self.assertEqual(
            list(traces[:3]),
            [0x04000000, 0x007003D0, 0x007003D0],
        )

    def test_missing_record_reports_failure(self) -> None:
        self.configure_full_logging()
        address = (ctypes.c_ubyte * 6)(1, 2, 3, 4, 5, 6)

        result = self.clear(2, address)

        self.assertEqual(result, 0)
        self.assertEqual(self.order(), [4, 1, 2, 1, 3])
        self.assertEqual(
            self.pointer(
                "open_cfw_test_mram_clear_find_address"
            ).value,
            ctypes.addressof(address),
        )
        logs = self.addresses(
            "open_cfw_test_mram_clear_logs",
            CAPTURE_COUNT * 6,
        )
        self.assertEqual(
            list(logs[:6]),
            [
                4,
                0x0078A0D0,
                0x006D84BC,
                0x00769414,
                0x765,
                0x00726E58,
            ],
        )
        traces = self.addresses(
            "open_cfw_test_mram_clear_traces",
            CAPTURE_COUNT * 3,
        )
        self.assertEqual(
            list(traces[:3]),
            [0x10000000, 0x00709364, 0x00709364],
        )

    def test_matching_record_deactivates_releases_and_reports_success(
        self,
    ) -> None:
        self.configure_full_logging()
        address = (ctypes.c_ubyte * 6)(6, 5, 4, 3, 2, 1)
        record = (ctypes.c_ubyte * 200)()
        record[6] = 0xA5
        self.pointer(
            "open_cfw_test_mram_clear_find_result"
        ).value = ctypes.addressof(record)
        self.word(
            "open_cfw_test_mram_clear_deactivate_result"
        ).value = 0xDEADBEEF

        result = self.clear(1, address)

        self.assertEqual(result, 1)
        self.assertEqual(
            self.order(),
            [4, 1, 2, 1, 3, 5, 6, 1, 2, 1, 3],
        )
        self.assertEqual(
            self.pointer(
                "open_cfw_test_mram_clear_deactivate_record"
            ).value,
            ctypes.addressof(record),
        )
        self.assertEqual(
            self.word(
                "open_cfw_test_mram_clear_release_owner"
            ).value,
            0xA5,
        )
        self.assertEqual(
            self.pointer(
                "open_cfw_test_mram_clear_release_record"
            ).value,
            ctypes.addressof(record),
        )
        self.assertEqual(
            self.word(
                "open_cfw_test_mram_clear_release_flags"
            ).value,
            0,
        )
        logs = self.addresses(
            "open_cfw_test_mram_clear_logs",
            CAPTURE_COUNT * 6,
        )
        self.assertEqual(
            list(logs[:12]),
            [
                4, 0x0078A0D0, 0x006D84BC,
                0x00769414, 0x755, 0x006F85AC,
                4, 0x0078A0D0, 0x006D84BC,
                0x00769414, 0x760, 0x00700414,
            ],
        )
        traces = self.addresses(
            "open_cfw_test_mram_clear_traces",
            CAPTURE_COUNT * 3,
        )
        self.assertEqual(
            list(traces[:6]),
            [
                0x10000000, 0x006E6328, 0x006E6328,
                0x10000000, 0x006EB628, 0x006EB628,
            ],
        )

    def test_owner_is_truncated_to_one_byte_before_lookup(self) -> None:
        address = (ctypes.c_ubyte * 6)()

        self.clear(0x1234AB, address)

        self.assertEqual(
            self.word(
                "open_cfw_test_mram_clear_find_owner"
            ).value,
            0xAB,
        )

    def test_structured_logging_does_not_imply_trace(self) -> None:
        self.word(
            "open_cfw_test_mram_clear_level_default"
        ).value = 2

        result = self.clear(0, None)

        self.assertEqual(result, 0)
        self.assertEqual(
            self.word(
                "open_cfw_test_mram_clear_log_count"
            ).value,
            1,
        )
        self.assertEqual(
            self.word(
                "open_cfw_test_mram_clear_trace_count"
            ).value,
            0,
        )
        self.assertEqual(self.order(), [1, 2, 1, 1])

    def test_trace_primary_and_fallback_gates_match_stock_reads(
        self,
    ) -> None:
        for level, expected_order in (
            (1, [1, 1, 3]),
            (4, [1, 1, 1, 3]),
        ):
            with self.subTest(level=level):
                self.reset()
                self.word(
                    "open_cfw_test_mram_clear_level_default"
                ).value = level

                self.clear(0, None)

                self.assertEqual(
                    self.word(
                        "open_cfw_test_mram_clear_log_count"
                    ).value,
                    0,
                )
                self.assertEqual(
                    self.word(
                        "open_cfw_test_mram_clear_trace_count"
                    ).value,
                    1,
                )
                self.assertEqual(self.order(), expected_order)

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "b10b4c971e336bc4bee55eb8fa8dec4cfb32da3191b3a5b59faf6f5bcd4aee4f",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "c70b1021e1550c17e3e3d69cc8fb959865846cb768681fb61143fb99b3f63419",
        )


if __name__ == "__main__":
    unittest.main()
