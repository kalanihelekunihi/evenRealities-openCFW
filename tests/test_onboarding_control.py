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
SOURCE = COMPONENT_ROOT / "onboarding_control.c"
FIXTURE = OPENCFW_ROOT / "tests" / "fixtures" / "onboarding_control_host.c"
UINT_MASK = (1 << 32) - 1


class OnboardingControlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "onboarding_control.dylib"
            if sys.platform == "darwin"
            else "onboarding_control.so"
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

        cls.reset_fixture = cls.loaded.open_cfw_test_onboarding_control_reset
        cls.reset_fixture.argtypes = []
        cls.reset_fixture.restype = None
        cls.update = cls.loaded.open_cfw_onboarding_control_update
        cls.update.argtypes = [ctypes.c_uint, ctypes.c_void_p]
        cls.update.restype = ctypes.c_int
        cls.acquire_uses_a = (
            cls.loaded.open_cfw_test_onboarding_control_acquire_uses_a
        )
        cls.acquire_uses_a.argtypes = []
        cls.acquire_uses_a.restype = ctypes.c_uint
        cls.release_uses_b = (
            cls.loaded.open_cfw_test_onboarding_control_release_uses_b
        )
        cls.release_uses_b.argtypes = []
        cls.release_uses_b.restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset_fixture()

    @classmethod
    def word(cls, suffix: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_onboarding_control_{suffix}",
        )

    @classmethod
    def byte_array(cls, suffix: str) -> ctypes.Array[ctypes.c_ubyte]:
        return (ctypes.c_ubyte * 3).in_dll(
            cls.loaded,
            f"open_cfw_test_onboarding_control_{suffix}",
        )

    @classmethod
    def state(cls) -> list[int]:
        return list(cls.byte_array("state"))

    @classmethod
    def events(cls) -> list[int]:
        count = cls.word("event_count").value
        values = (ctypes.c_uint * 8).in_dll(
            cls.loaded,
            "open_cfw_test_onboarding_control_events",
        )
        return list(values[:count])

    def test_invalid_commands_clear_pending_state_before_rejection(
        self,
    ) -> None:
        for command in (0, 4, 0xFF, 0x100, 0x104):
            with self.subTest(command=command):
                self.reset_fixture()
                self.assertEqual(self.update(command, None), 1)
                self.assertEqual(self.state(), [7, 9, 0])
                self.assertEqual(self.events(), [])

    def test_event_commands_acknowledge_without_payload_or_lock(
        self,
    ) -> None:
        for command in (2, 3, 0x102, 0x103):
            with self.subTest(command=command):
                self.reset_fixture()
                self.assertEqual(self.update(command, None), 0)
                self.assertEqual(self.state(), [7, 9, 0])
                self.assertEqual(self.events(), [])

    def test_matching_config_preserves_secondary_state(self) -> None:
        payload = (ctypes.c_ubyte * 1)(7)
        self.word("acquire_result").value = 0xA5A5A5A5
        self.word("release_result").value = 0x5A5A5A5A
        self.assertEqual(self.update(1, payload), 0)
        self.assertEqual(self.events(), [1, 2])
        self.assertEqual(self.state(), [7, 9, 2])
        self.assertEqual(
            list(self.byte_array("state_seen_by_acquire")),
            [7, 9, 0],
        )
        self.assertEqual(
            list(self.byte_array("state_seen_by_release")),
            [7, 9, 2],
        )
        self.assertEqual(self.word("wait_ticks").value, UINT_MASK)
        self.assertEqual(self.acquire_uses_a(), 1)

    def test_changed_config_clears_secondary_state_and_refreshes_mutex(
        self,
    ) -> None:
        payload = (ctypes.c_ubyte * 1)(0xD3)
        self.word("change_mutex_on_acquire").value = 1
        self.assertEqual(self.update(0x101, payload), 0)
        self.assertEqual(self.events(), [1, 2])
        self.assertEqual(self.state(), [0xD3, 0, 2])
        self.assertEqual(self.word("acquire_calls").value, 1)
        self.assertEqual(self.word("release_calls").value, 1)
        self.assertEqual(self.acquire_uses_a(), 1)
        self.assertEqual(self.release_uses_b(), 1)

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "014cc7b276dae2821b07db265008992a8"
            "05ce33d270eef4d4b6b1d049b1e25e1",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "9dae14ecdfefeaf7b49c400152242e23a"
            "0aae21bbc29730241a6e7238595a4ca",
        )


if __name__ == "__main__":
    unittest.main()
