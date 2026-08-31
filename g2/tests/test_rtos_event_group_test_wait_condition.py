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
SOURCE = COMPONENT_ROOT / "rtos_event_group_test_wait_condition.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "rtos_event_group_test_wait_condition_host.c"
)


class RtosEventGroupTestWaitConditionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "rtos_event_group_test_wait_condition.dylib"
            if sys.platform == "darwin"
            else "rtos_event_group_test_wait_condition.so"
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
        cls.predicate = (
            cls.loaded.open_cfw_rtos_event_group_test_wait_condition
        )
        cls.predicate.argtypes = [
            ctypes.c_uint,
            ctypes.c_uint,
            ctypes.c_uint,
        ]
        cls.predicate.restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_any_bit_wait_uses_nonempty_intersection(self) -> None:
        cases = (
            (0x00000000, 0x00000000, 0),
            (0xFFFFFFFF, 0x00000000, 0),
            (0x00000000, 0xFFFFFFFF, 0),
            (0x00000008, 0x0000000C, 1),
            (0x80000000, 0x80000001, 1),
            (0x40000000, 0x80000000, 0),
        )
        for current, waited, expected in cases:
            with self.subTest(current=current, waited=waited):
                self.assertEqual(
                    self.predicate(current, waited, 0),
                    expected,
                )

    def test_all_bit_wait_requires_the_complete_mask(self) -> None:
        cases = (
            (0x00000000, 0x00000000, 1),
            (0xFFFFFFFF, 0x00000000, 1),
            (0x0000000C, 0x0000000C, 1),
            (0xFFFFFFFF, 0x80000001, 1),
            (0x00000008, 0x0000000C, 0),
            (0x7FFFFFFF, 0x80000000, 0),
        )
        for current, waited, expected in cases:
            with self.subTest(current=current, waited=waited):
                self.assertEqual(
                    self.predicate(current, waited, 1),
                    expected,
                )

    def test_every_nonzero_selector_uses_all_bit_policy(self) -> None:
        for selector in (1, 2, 0x80000000, 0xFFFFFFFF):
            with self.subTest(selector=selector):
                self.assertEqual(
                    self.predicate(0x00000001, 0x00000003, selector),
                    0,
                )
                self.assertEqual(
                    self.predicate(0x00000003, 0x00000003, selector),
                    1,
                )

    def test_randomized_full_width_truth_table(self) -> None:
        generator = random.Random(0x47EE30)
        for _ in range(4096):
            current = generator.getrandbits(32)
            waited = generator.getrandbits(32)
            selector = generator.getrandbits(32)
            intersection = current & waited
            expected = (
                intersection != 0
                if selector == 0
                else intersection == waited
            )
            self.assertEqual(
                self.predicate(current, waited, selector),
                int(expected),
            )

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "27621b23bc5d90a5d0b5b764963f70dbf5a07829f201d0b8f680bab22fcf3204",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "1cedb9774e989e1899bb068e8da7ae3506c75471fdaa5ae63e08457a251a15ab",
        )


if __name__ == "__main__":
    unittest.main()
