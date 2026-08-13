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
SOURCE = COMPONENT_ROOT / "rtos_timer_query.c"
FIXTURE = OPENCFW_ROOT / "tests" / "fixtures" / "rtos_timer_query_host.c"


class RtosTimerQueryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "rtos_timer_query.dylib"
            if sys.platform == "darwin"
            else "rtos_timer_query.so"
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
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.loaded = ctypes.CDLL(str(library))
        cls.reset_fixture = cls.loaded.open_cfw_test_rtos_timer_query_reset
        cls.reset_fixture.argtypes = []
        cls.reset_fixture.restype = None
        cls.query = cls.loaded.open_cfw_rtos_timer_query
        cls.query.argtypes = [ctypes.POINTER(ctypes.c_uint)]
        cls.query.restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset_fixture()

    @classmethod
    def uint(cls, suffix: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_rtos_timer_query_{suffix}",
        )

    @classmethod
    def events(cls) -> list[int]:
        count = cls.uint("event_count").value
        values = (ctypes.c_uint * 8).in_dll(
            cls.loaded,
            "open_cfw_test_rtos_timer_query_events",
        )
        return list(values)[:count]

    def run_query(
        self,
        *,
        item_count: int,
        head_expiry: int,
        initial_empty: int = 0xA5A5A5A5,
    ) -> tuple[int, int]:
        self.uint("item_count").value = item_count
        self.uint("head_expiry").value = head_expiry
        empty = ctypes.c_uint(initial_empty)
        expiry = self.query(ctypes.byref(empty))
        return expiry, empty.value

    def test_empty_list_writes_one_and_returns_zero(self) -> None:
        self.assertEqual(
            self.run_query(item_count=0, head_expiry=0x12345678),
            (0, 1),
        )
        self.assertEqual(self.events(), [10])
        self.assertEqual(self.uint("item_count_reads").value, 1)
        self.assertEqual(self.uint("head_expiry_reads").value, 0)

    def test_nonempty_list_writes_zero_and_returns_head_expiry(self) -> None:
        self.assertEqual(
            self.run_query(item_count=1, head_expiry=0x12345678),
            (0x12345678, 0),
        )
        self.assertEqual(self.events(), [10, 20])
        self.assertEqual(self.uint("item_count_reads").value, 1)
        self.assertEqual(self.uint("head_expiry_reads").value, 1)

    def test_every_nonzero_item_count_is_nonempty(self) -> None:
        for item_count in (1, 2, 0x80000000, 0xFFFFFFFF):
            with self.subTest(item_count=item_count):
                self.reset_fixture()
                self.assertEqual(
                    self.run_query(
                        item_count=item_count,
                        head_expiry=73,
                    ),
                    (73, 0),
                )
                self.assertEqual(self.events(), [10, 20])

    def test_output_is_normalized_regardless_of_initial_value(self) -> None:
        for item_count, expected in ((0, 1), (7, 0)):
            for initial in (0, 1, 0xFFFFFFFF):
                with self.subTest(item_count=item_count, initial=initial):
                    self.reset_fixture()
                    _, empty = self.run_query(
                        item_count=item_count,
                        head_expiry=9,
                        initial_empty=initial,
                    )
                    self.assertEqual(empty, expected)

    def test_head_expiry_preserves_all_32_bits(self) -> None:
        for expiry in (0, 1, 0x80000000, 0xFFFFFFFF):
            with self.subTest(expiry=expiry):
                self.reset_fixture()
                self.assertEqual(
                    self.run_query(item_count=1, head_expiry=expiry),
                    (expiry, 0),
                )

    def test_head_is_not_read_until_after_nonempty_count(self) -> None:
        self.run_query(item_count=3, head_expiry=44)
        self.assertEqual(self.events(), [10, 20])

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "8225c684a70280cda35e2ff26bf7842873aedb64a20e97445ce1a15cddf014f1",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "f3d1c0e47f81702938b32bc5a5e75927f09b6b3f53f8c410d3a9d432e4aa0893",
        )


if __name__ == "__main__":
    unittest.main()
