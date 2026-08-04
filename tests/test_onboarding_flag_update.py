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
SOURCE = COMPONENT_ROOT / "onboarding_flag_update.c"
FIXTURE = (
    OPENCFW_ROOT / "tests" / "fixtures" / "onboarding_flag_update_host.c"
)
UINT_MASK = (1 << 32) - 1


class OnboardingFlagUpdateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "onboarding_flag_update.dylib"
            if sys.platform == "darwin"
            else "onboarding_flag_update.so"
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
        cls.reset_fixture = (
            cls.loaded.open_cfw_test_onboarding_flag_update_reset
        )
        cls.reset_fixture.argtypes = []
        cls.reset_fixture.restype = None
        cls.update = cls.loaded.open_cfw_onboarding_flag_update
        cls.update.argtypes = [ctypes.c_uint]
        cls.update.restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset_fixture()

    @classmethod
    def byte(cls, suffix: str) -> ctypes.c_ubyte:
        return ctypes.c_ubyte.in_dll(
            cls.loaded,
            f"open_cfw_test_onboarding_flag_update_{suffix}",
        )

    @classmethod
    def word(cls, suffix: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_onboarding_flag_update_{suffix}",
        )

    @classmethod
    def array(
        cls,
        suffix: str,
        length: int,
    ) -> ctypes.Array[ctypes.c_uint]:
        return (ctypes.c_uint * length).in_dll(
            cls.loaded,
            f"open_cfw_test_onboarding_flag_update_{suffix}",
        )

    @classmethod
    def events(cls) -> list[int]:
        count = cls.word("event_count").value
        return list(cls.array("events", 12)[:count])

    def test_equal_low_byte_is_a_side_effect_free_noop(self) -> None:
        self.byte("stored").value = 0xA5
        value = 0x123456A5
        self.assertEqual(self.update(value), value)
        self.assertEqual(self.events(), [1])
        self.assertEqual(self.word("get_calls").value, 1)
        self.assertEqual(self.word("get_index").value, 0)
        self.assertEqual(self.word("set_calls").value, 0)
        self.assertEqual(self.word("event_calls").value, 0)
        self.assertEqual(self.word("pending").value, 0)

    def test_changed_byte_updates_marks_pending_then_sets_event(self) -> None:
        self.byte("stored").value = 0x11
        value = 0x89ABCDEF
        self.assertEqual(self.update(value), value)
        self.assertEqual(self.events(), [1, 2, 3])
        self.assertEqual(self.word("set_index").value, 0)
        self.assertEqual(self.word("set_value").value, value)
        self.assertEqual(self.byte("stored").value, 0xEF)
        self.assertEqual(self.word("pending_seen_by_set").value, 0)
        self.assertEqual(self.word("pending").value, 1)
        self.assertEqual(self.word("pending_seen_by_event").value, 1)
        self.assertEqual(self.word("event_handle_seen").value, 0x12345678)
        self.assertEqual(self.word("event_flags").value, 4)

    def test_missing_provider_treats_current_value_as_zero(self) -> None:
        self.word("provider_present").value = 0
        value = 0xFFFFFF00
        self.assertEqual(self.update(value), value)
        self.assertEqual(self.events(), [1])
        self.assertEqual(self.word("set_calls").value, 0)
        self.assertEqual(self.word("event_calls").value, 0)

        self.reset_fixture()
        self.word("provider_present").value = 0
        value = 0xFFFFFF01
        self.assertEqual(self.update(value), value)
        self.assertEqual(self.events(), [1, 2, 3])
        self.assertEqual(self.byte("stored").value, 1)

    def test_full_input_word_is_returned_but_only_low_byte_compares(
        self,
    ) -> None:
        for value in (0, 0x100, 0xFFFFFF00, UINT_MASK):
            with self.subTest(value=value):
                self.reset_fixture()
                self.byte("stored").value = value & 0xFF
                self.assertEqual(self.update(value), value)
                self.assertEqual(self.events(), [1])

    def test_set_and_event_results_are_ignored(self) -> None:
        self.byte("stored").value = 1
        self.word("set_result").value = UINT_MASK
        self.word("event_result").value = 0xDEADBEEF
        value = 2
        self.assertEqual(self.update(value), value)
        self.assertEqual(self.events(), [1, 2, 3])
        self.assertEqual(self.word("pending").value, 1)

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "1bf521807e6604d3fc163a0cbb4285100"
            "a9f189c32971556b95f4a10d8336cc2",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "fe9e5b4e2ad10daaf25d572b52bda5b"
            "f20357909e2a4b4ac345c287ec654d7ae",
        )


if __name__ == "__main__":
    unittest.main()
