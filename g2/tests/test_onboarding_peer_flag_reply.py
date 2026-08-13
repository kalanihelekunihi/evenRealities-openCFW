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
SOURCE = COMPONENT_ROOT / "onboarding_peer_flag_reply.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "onboarding_peer_flag_reply_host.c"
)


class OnboardingPeerFlagReplyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "onboarding_peer_flag_reply.dylib"
            if sys.platform == "darwin"
            else "onboarding_peer_flag_reply.so"
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
        cls.reset_fixture = cls.loaded.open_cfw_test_onboarding_peer_reply_reset
        cls.reset_fixture.argtypes = []
        cls.reset_fixture.restype = None
        cls.reply = cls.loaded.open_cfw_onboarding_flag_reply_to_peer
        cls.reply.argtypes = [ctypes.c_uint]
        cls.reply.restype = None

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset_fixture()

    @classmethod
    def word(cls, suffix: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_onboarding_peer_reply_{suffix}",
        )

    @classmethod
    def signed_word(cls, suffix: str) -> ctypes.c_int:
        return ctypes.c_int.in_dll(
            cls.loaded,
            f"open_cfw_test_onboarding_peer_reply_{suffix}",
        )

    @classmethod
    def array(
        cls,
        suffix: str,
        length: int,
    ) -> ctypes.Array[ctypes.c_uint]:
        return (ctypes.c_uint * length).in_dll(
            cls.loaded,
            f"open_cfw_test_onboarding_peer_reply_{suffix}",
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

    def test_builds_exact_reply_payload_and_transport_tuple(self) -> None:
        self.reply(0xA5)
        self.assertEqual(self.events(), [1, 2, 3, 3, 3])
        self.assertEqual(list(self.array("zero_fields", 2)), [2, 0])
        fields = list(self.array("send_fields", 5))
        self.assertEqual(fields[:1] + fields[2:], [0x10, 2, 0, 5])
        self.assertEqual(list(self.array("payload", 2)), [0x0E, 0xA5])

    def test_flag_is_truncated_to_byte_everywhere(self) -> None:
        self.set_levels(2, 1)
        self.reply(0x123456AB)
        self.assertEqual(list(self.array("payload", 2)), [0x0E, 0xAB])
        self.assertEqual(self.array("log_fields", 7)[6], 0xAB)
        self.assertEqual(self.array("trace_fields", 4)[3], 0xAB)

    def test_structured_diagnostic_preserves_stock_metadata(self) -> None:
        self.set_levels(2, 0, 0)
        self.reply(7)
        self.assertEqual(
            list(self.array("log_fields", 7)),
            [
                4,
                0x00781570,
                0x006E8ECC,
                0x00762B90,
                0x8C,
                0x00779D24,
                7,
            ],
        )

    def test_trace_gates_preserve_primary_and_fallback_reads(self) -> None:
        self.set_levels(0, 1, 4)
        self.reply(9)
        self.assertEqual(self.word("level_calls").value, 2)
        self.assertEqual(
            list(self.array("trace_fields", 4)),
            [0x10400000, 0x00740CB4, 0x00740CB4, 9],
        )

        self.reset_fixture()
        self.set_levels(0, 0, 4)
        self.reply(3)
        self.assertEqual(self.word("level_calls").value, 3)
        self.assertEqual(self.word("trace_calls").value, 1)

    def test_send_result_is_ignored_and_diagnostics_still_run(self) -> None:
        self.signed_word("send_result").value = -1
        self.set_levels(2, 1)
        self.reply(4)
        self.assertEqual(self.events(), [1, 2, 3, 4, 3, 5])
        self.assertEqual(self.word("log_calls").value, 1)
        self.assertEqual(self.word("trace_calls").value, 1)

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "701b6bf8c227e955aa0636ffd561819380b4ecb42742b5c1daaa20829da3807d",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "265f24bcad3f2633bdd94dc61ebe9bb37dcea7d5eb847e80afb9336e246818ed",
        )


if __name__ == "__main__":
    unittest.main()
