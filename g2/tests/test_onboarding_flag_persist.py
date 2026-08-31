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
SOURCE = COMPONENT_ROOT / "onboarding_flag_persist.c"
FIXTURE = (
    OPENCFW_ROOT / "tests" / "fixtures" / "onboarding_flag_persist_host.c"
)
UINT_MASK = (1 << 32) - 1


class OnboardingFlagPersistTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "onboarding_flag_persist.dylib"
            if sys.platform == "darwin"
            else "onboarding_flag_persist.so"
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
        cls.reset_fixture = cls.loaded.open_cfw_test_onboarding_flag_reset
        cls.reset_fixture.argtypes = []
        cls.reset_fixture.restype = None
        cls.persist = cls.loaded.open_cfw_onboarding_flag_save_to_flash
        cls.persist.argtypes = []
        cls.persist.restype = None

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset_fixture()

    @classmethod
    def word(cls, suffix: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_onboarding_flag_{suffix}",
        )

    @classmethod
    def signed_word(cls, suffix: str) -> ctypes.c_int:
        return ctypes.c_int.in_dll(
            cls.loaded,
            f"open_cfw_test_onboarding_flag_{suffix}",
        )

    @classmethod
    def array(
        cls,
        suffix: str,
        length: int,
    ) -> ctypes.Array[ctypes.c_uint]:
        return (ctypes.c_uint * length).in_dll(
            cls.loaded,
            f"open_cfw_test_onboarding_flag_{suffix}",
        )

    @classmethod
    def events(cls) -> list[int]:
        count = cls.word("event_count").value
        return list(cls.array("events", 24)[:count])

    def set_levels(self, *values: int) -> None:
        levels = self.array("level_values", 12)
        for index, value in enumerate(values):
            levels[index] = value
        self.word("level_value_count").value = len(values)

    def test_only_pending_value_one_runs_persistence(self) -> None:
        for pending in (0, 2, UINT_MASK):
            with self.subTest(pending=pending):
                self.reset_fixture()
                self.word("pending").value = pending
                self.persist()
                self.assertEqual(self.events(), [])
                self.assertEqual(self.word("save_calls").value, 0)
                self.assertEqual(self.word("pending").value, pending)

    def test_success_saves_before_clearing_pending_flag(self) -> None:
        self.persist()
        self.assertEqual(self.events(), [1, 1, 1, 4])
        self.assertEqual(self.word("save_calls").value, 1)
        self.assertEqual(self.word("pending_seen_by_save").value, 1)
        self.assertEqual(self.word("pending").value, 0)

    def test_success_diagnostic_metadata_and_trace_short_circuit(
        self,
    ) -> None:
        self.set_levels(2, 1, 4)
        self.persist()
        self.assertEqual(self.events(), [1, 2, 1, 3, 4])
        self.assertEqual(self.word("level_calls").value, 2)
        self.assertEqual(
            list(self.array("log_fields", 6)),
            [
                4,
                0x00781570,
                0x006E8ECC,
                0x0076E964,
                0x5C,
                0x0076E980,
            ],
        )
        self.assertEqual(
            list(self.array("trace_fields", 3)),
            [0x10000000, 0x007361C4, 0x007361C4],
        )

    def test_failure_preserves_pending_and_emits_failure_metadata(
        self,
    ) -> None:
        self.signed_word("save_result").value = -7
        self.set_levels(0, 1, 2, 0, 4)
        self.persist()
        self.assertEqual(
            self.events(),
            [1, 1, 3, 4, 1, 2, 1, 1, 3],
        )
        self.assertEqual(self.word("pending").value, 1)
        self.assertEqual(
            list(self.array("log_fields", 6)),
            [
                1,
                0x00781570,
                0x006E8ECC,
                0x0076E964,
                0x61,
                0x0075732C,
            ],
        )
        self.assertEqual(
            list(self.array("trace_fields", 3)),
            [0x04000000, 0x00720DE0, 0x00720DE0],
        )

    def test_failure_without_diagnostics_still_preserves_pending(self) -> None:
        self.signed_word("save_result").value = 9
        self.persist()
        self.assertEqual(
            self.events(),
            [1, 1, 1, 4, 1, 1, 1],
        )
        self.assertEqual(self.word("log_calls").value, 0)
        self.assertEqual(self.word("trace_calls").value, 0)
        self.assertEqual(self.word("pending").value, 1)

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "3397bbefb379f1771cb596e8f4a97ea3"
            "359356b301fc39ed4b8705374ed927e3",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "1b81637e6541d9c4248fb197b80bfec5"
            "91790d64d683ca0bcca6be030bfa5f51",
        )


if __name__ == "__main__":
    unittest.main()
