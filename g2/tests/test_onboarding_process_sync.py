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
SOURCE = COMPONENT_ROOT / "onboarding_process_sync.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "onboarding_process_sync_host.c"
)


class OnboardingProcessSyncTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "onboarding_process_sync.dylib"
            if sys.platform == "darwin"
            else "onboarding_process_sync.so"
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
            cls.loaded.open_cfw_test_onboarding_process_sync_reset
        )
        cls.reset_fixture.argtypes = []
        cls.reset_fixture.restype = None
        cls.sync = cls.loaded.open_cfw_onboarding_process_sync_to_peer
        cls.sync.argtypes = []
        cls.sync.restype = None

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset_fixture()

    @classmethod
    def word(cls, suffix: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_onboarding_process_sync_{suffix}",
        )

    @classmethod
    def signed_word(cls, suffix: str) -> ctypes.c_int:
        return ctypes.c_int.in_dll(
            cls.loaded,
            f"open_cfw_test_onboarding_process_sync_{suffix}",
        )

    @classmethod
    def array(
        cls,
        suffix: str,
        length: int,
    ) -> ctypes.Array[ctypes.c_uint]:
        return (ctypes.c_uint * length).in_dll(
            cls.loaded,
            f"open_cfw_test_onboarding_process_sync_{suffix}",
        )

    @classmethod
    def bytes_array(
        cls,
        suffix: str,
        length: int,
    ) -> ctypes.Array[ctypes.c_ubyte]:
        return (ctypes.c_ubyte * length).in_dll(
            cls.loaded,
            f"open_cfw_test_onboarding_process_sync_{suffix}",
        )

    @classmethod
    def events(cls) -> list[int]:
        count = cls.word("event_count").value
        return list(cls.array("events", 16)[:count])

    def set_levels(self, *values: int) -> None:
        levels = self.array("level_values", 8)
        for index, value in enumerate(values):
            levels[index] = value
        self.word("level_value_count").value = len(values)

    def set_state(self, process_id: int, substep: int) -> None:
        state = self.bytes_array("state", 2)
        state[0] = process_id
        state[1] = substep

    def test_builds_exact_process_sync_payload_and_transport_tuple(
        self,
    ) -> None:
        self.set_state(0xA5, 0x6C)
        self.sync()
        self.assertEqual(self.events(), [1, 2, 3, 3, 3])
        self.assertEqual(list(self.array("zero_fields", 2)), [3, 0])
        fields = list(self.array("send_fields", 5))
        self.assertEqual(fields[:1] + fields[2:], [0x10, 3, 0, 5])
        self.assertEqual(list(self.array("payload", 3)), [0x09, 0xA5, 0x6C])

    def test_diagnostics_refresh_state_after_transport(self) -> None:
        self.set_state(1, 2)
        send_state = self.bytes_array("send_state", 2)
        send_state[0] = 0x81
        send_state[1] = 0xFE
        self.word("mutate_on_send").value = 1
        self.set_levels(2, 1)
        self.sync()
        self.assertEqual(list(self.array("payload", 3)), [0x09, 1, 2])
        self.assertEqual(list(self.array("log_fields", 8))[6:], [0x81, 0xFE])
        self.assertEqual(
            list(self.array("trace_fields", 5))[3:],
            [0x81, 0xFE],
        )

    def test_structured_diagnostic_preserves_stock_metadata(self) -> None:
        self.set_state(4, 9)
        self.set_levels(2, 0, 0)
        self.sync()
        self.assertEqual(
            list(self.array("log_fields", 8)),
            [
                4,
                0x00781570,
                0x006E8ECC,
                0x00762BB0,
                0x9A,
                0x0074BD74,
                4,
                9,
            ],
        )

    def test_trace_gates_preserve_primary_and_fallback_reads(self) -> None:
        self.set_state(7, 8)
        self.set_levels(0, 1, 4)
        self.sync()
        self.assertEqual(self.word("level_calls").value, 2)
        self.assertEqual(
            list(self.array("trace_fields", 5)),
            [0x10800000, 0x00716F9C, 0x00716F9C, 7, 8],
        )

        self.reset_fixture()
        self.set_state(2, 3)
        self.set_levels(0, 0, 4)
        self.sync()
        self.assertEqual(self.word("level_calls").value, 3)
        self.assertEqual(self.word("trace_calls").value, 1)

    def test_send_result_is_ignored_and_diagnostics_still_run(self) -> None:
        self.signed_word("send_result").value = -1
        self.set_levels(2, 1)
        self.sync()
        self.assertEqual(self.events(), [1, 2, 3, 4, 3, 5])
        self.assertEqual(self.word("log_calls").value, 1)
        self.assertEqual(self.word("trace_calls").value, 1)

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "1a14dfebeac2c055633ecd9eb0d94e045062d39d2f53b1a4ed148109671a97bc",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "14c492cd869e46efc12564d4d80d9aa566c8ae6eb9c7871dd110f93a239df93c",
        )


if __name__ == "__main__":
    unittest.main()
