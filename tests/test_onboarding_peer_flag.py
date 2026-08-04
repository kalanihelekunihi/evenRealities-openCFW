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
SOURCE = COMPONENT_ROOT / "onboarding_peer_flag.c"
FIXTURE = (
    OPENCFW_ROOT / "tests" / "fixtures" / "onboarding_peer_flag_host.c"
)


class OnboardingPeerFlagTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "onboarding_peer_flag.dylib"
            if sys.platform == "darwin"
            else "onboarding_peer_flag.so"
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
        cls.reset_fixture = cls.loaded.open_cfw_test_onboarding_peer_flag_reset
        cls.reset_fixture.argtypes = []
        cls.reset_fixture.restype = None
        cls.send = cls.loaded.open_cfw_onboarding_flag_send_to_peer
        cls.send.argtypes = []
        cls.send.restype = None

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset_fixture()

    @classmethod
    def word(cls, suffix: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_onboarding_peer_flag_{suffix}",
        )

    @classmethod
    def signed_word(cls, suffix: str) -> ctypes.c_int:
        return ctypes.c_int.in_dll(
            cls.loaded,
            f"open_cfw_test_onboarding_peer_flag_{suffix}",
        )

    @classmethod
    def array(
        cls,
        suffix: str,
        length: int,
    ) -> ctypes.Array[ctypes.c_uint]:
        return (ctypes.c_uint * length).in_dll(
            cls.loaded,
            f"open_cfw_test_onboarding_peer_flag_{suffix}",
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

    def test_builds_exact_two_byte_rpc_payload(self) -> None:
        self.word("value").value = 0xA5
        self.send()
        self.assertEqual(self.events(), [1, 2, 3, 4, 4, 4])
        self.assertEqual(self.word("get_calls").value, 1)
        self.assertEqual(self.word("zero_calls").value, 1)
        self.assertEqual(self.word("zero_size").value, 2)
        self.assertEqual(self.word("zero_value").value, 0)
        self.assertEqual(self.word("send_calls").value, 1)
        self.assertEqual(
            list(self.array("send_fields", 5))[:1]
            + list(self.array("send_fields", 5))[2:],
            [0x10, 2, 0, 5],
        )
        self.assertEqual(list(self.array("payload", 2)), [0x0D, 0xA5])

    def test_payload_and_diagnostics_truncate_flag_to_byte(self) -> None:
        self.word("value").value = 0x123456AB
        self.set_levels(2, 1)
        self.send()
        self.assertEqual(list(self.array("payload", 2)), [0x0D, 0xAB])
        self.assertEqual(self.array("log_fields", 7)[6], 0xAB)
        self.assertEqual(self.array("trace_fields", 4)[3], 0xAB)

    def test_structured_diagnostic_preserves_stock_metadata(self) -> None:
        self.word("value").value = 7
        self.set_levels(2, 0, 0)
        self.send()
        self.assertEqual(self.word("log_calls").value, 1)
        self.assertEqual(
            list(self.array("log_fields", 7)),
            [
                4,
                0x00781570,
                0x006E8ECC,
                0x00762B70,
                0x7F,
                0x00779D0C,
                7,
            ],
        )

    def test_trace_primary_gate_short_circuits_fallback_read(self) -> None:
        self.word("value").value = 9
        self.set_levels(0, 1, 4)
        self.send()
        self.assertEqual(self.word("level_calls").value, 2)
        self.assertEqual(
            list(self.array("trace_fields", 4)),
            [0x10400000, 0x00740C88, 0x00740C88, 9],
        )

    def test_trace_fallback_gate_uses_second_level_read(self) -> None:
        self.word("value").value = 3
        self.set_levels(0, 0, 4)
        self.send()
        self.assertEqual(self.word("level_calls").value, 3)
        self.assertEqual(self.word("trace_calls").value, 1)

    def test_send_result_is_ignored_and_diagnostics_still_run(self) -> None:
        self.signed_word("send_result").value = -1
        self.set_levels(2, 1)
        self.send()
        self.assertEqual(self.events(), [1, 2, 3, 4, 5, 4, 6])
        self.assertEqual(self.word("log_calls").value, 1)
        self.assertEqual(self.word("trace_calls").value, 1)

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "45dd5b794f2b81b0d9cc1076a8d6f123"
            "9273cf3941876cac921ed2e66d138761",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "cc313876debb303f7ef4df6c5f4e752c"
            "de323771febe947843bcb779207485ea",
        )


if __name__ == "__main__":
    unittest.main()
