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
SOURCE = COMPONENT_ROOT / "onboarding_wear_status.c"
FIXTURE = (
    OPENCFW_ROOT / "tests" / "fixtures" / "onboarding_wear_status_host.c"
)
UINT_MASK = (1 << 32) - 1


class OnboardingWearStatusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "onboarding_wear_status.dylib"
            if sys.platform == "darwin"
            else "onboarding_wear_status.so"
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
        cls.reset_fixture = cls.loaded.open_cfw_test_onboarding_wear_reset
        cls.reset_fixture.argtypes = []
        cls.reset_fixture.restype = None
        cls.notify = (
            cls.loaded.open_cfw_onboarding_notify_wear_status_to_app
        )
        cls.notify.argtypes = [ctypes.c_uint]
        cls.notify.restype = None

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset_fixture()

    @classmethod
    def word(cls, suffix: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_onboarding_wear_{suffix}",
        )

    @classmethod
    def signed_word(cls, suffix: str) -> ctypes.c_int:
        return ctypes.c_int.in_dll(
            cls.loaded,
            f"open_cfw_test_onboarding_wear_{suffix}",
        )

    @classmethod
    def array(
        cls,
        suffix: str,
        length: int,
    ) -> ctypes.Array[ctypes.c_uint]:
        return (ctypes.c_uint * length).in_dll(
            cls.loaded,
            f"open_cfw_test_onboarding_wear_{suffix}",
        )

    @classmethod
    def events(cls) -> list[int]:
        count = cls.word("event_count").value
        return list(cls.array("events", 24)[:count])

    def set_levels(self, *values: int) -> None:
        levels = self.array("level_values", 8)
        for index, value in enumerate(values):
            levels[index] = value
        self.word("level_value_count").value = len(values)

    def test_gates_preserve_exact_comparisons_and_short_circuiting(
        self,
    ) -> None:
        self.word("ota_active").value = 1
        self.notify(7)
        self.assertEqual(self.events(), [1])

        self.reset_fixture()
        self.word("transport_ready").value = 0
        self.notify(7)
        self.assertEqual(self.events(), [1, 2])

        self.reset_fixture()
        self.word("mode_ready").value = 2
        self.notify(7)
        self.assertEqual(self.events(), [1, 2, 3])
        self.assertEqual(self.word("mode_argument").value, 0x10)

        self.reset_fixture()
        self.word("ota_active").value = 2
        self.word("transport_ready").value = 2
        self.notify(7)
        self.assertEqual(self.events()[:4], [1, 2, 3, 4])

    def test_notify_clones_template_and_truncates_status_to_byte(
        self,
    ) -> None:
        self.notify(0x123456D3)
        self.assertEqual(self.word("notify_command").value, 0)
        self.assertEqual(list(self.array("notify_event", 3)), [1, 0xD3, 0])
        self.assertEqual(self.events(), [1, 2, 3, 4, 5, 5, 5])
        self.assertEqual(self.word("log_calls").value, 0)
        self.assertEqual(self.word("trace_calls").value, 0)

    def test_success_diagnostics_preserve_metadata_and_level_reads(
        self,
    ) -> None:
        self.set_levels(2, 0, 4)
        self.notify(0xA5)
        self.assertEqual(
            self.events(),
            [1, 2, 3, 4, 5, 6, 5, 5, 7],
        )
        self.assertEqual(
            list(self.array("log_fields", 7)),
            [
                4,
                0x00781570,
                0x006E8ECC,
                0x0074BD4C,
                0x51,
                0x0072B814,
                0xA5,
            ],
        )
        self.assertEqual(
            list(self.array("trace_fields", 5))[:4],
            [0x10400000, 0x006FBB64, 0x006FBB64, 0xA5],
        )

    def test_trace_bit_zero_short_circuits_fallback_level_read(
        self,
    ) -> None:
        self.set_levels(0, 1, 4)
        self.notify(3)
        self.assertEqual(self.word("level_calls").value, 2)
        self.assertEqual(self.events(), [1, 2, 3, 4, 5, 5, 7])
        self.assertEqual(self.word("log_calls").value, 0)
        self.assertEqual(self.word("trace_calls").value, 1)

    def test_failure_diagnostics_use_result_and_failure_metadata(
        self,
    ) -> None:
        self.signed_word("notify_result").value = -9
        self.set_levels(2, 1)
        self.notify(1)
        self.assertEqual(
            list(self.array("log_fields", 7)),
            [
                1,
                0x00781570,
                0x006E8ECC,
                0x0074BD4C,
                0x53,
                0x00720DA8,
                (-9) & UINT_MASK,
            ],
        )
        self.assertEqual(
            list(self.array("trace_fields", 5))[:4],
            [
                0x04400000,
                0x006EEC38,
                0x006EEC38,
                (-9) & UINT_MASK,
            ],
        )
        self.assertEqual(self.word("level_calls").value, 2)

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "6c10dd2b52f2d7fed25dc957b6d912b7"
            "2f050d35aef669d8861836ea250c8225",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "b65ff5cc7600a97c8a390d0cb07546af"
            "fe482965811769229a4e6085443c5d59",
        )


if __name__ == "__main__":
    unittest.main()
