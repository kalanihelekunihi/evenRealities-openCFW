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
SOURCE = COMPONENT_ROOT / "onboarding_runtime_init.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "onboarding_runtime_init_host.c"
)


class OnboardingRuntimeInitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "onboarding_runtime_init.dylib"
            if sys.platform == "darwin"
            else "onboarding_runtime_init.so"
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
            cls.loaded.open_cfw_test_onboarding_runtime_init_reset
        )
        cls.reset_fixture.argtypes = []
        cls.reset_fixture.restype = None
        cls.initialize = cls.loaded.open_cfw_onboarding_runtime_initialize
        cls.initialize.argtypes = []
        cls.initialize.restype = ctypes.c_int

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset_fixture()

    @classmethod
    def word(cls, suffix: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_onboarding_runtime_init_{suffix}",
        )

    @classmethod
    def array(
        cls,
        suffix: str,
        length: int,
    ) -> ctypes.Array[ctypes.c_uint]:
        return (ctypes.c_uint * length).in_dll(
            cls.loaded,
            f"open_cfw_test_onboarding_runtime_init_{suffix}",
        )

    @classmethod
    def events(cls) -> list[int]:
        count = cls.word("event_count").value
        return list(cls.array("events", 16)[:count])

    def configure_success(self) -> None:
        self.word("prerequisite").value = 1
        self.word("thread_result").value = 0x12345678
        attributes = self.array("attribute_values", 3)
        attributes[:] = [0x20071EA0, 0x2003FA98, 0x1000]

    def test_success_preserves_exact_thread_creation_abi(self) -> None:
        self.configure_success()
        self.assertEqual(self.initialize(), 1)
        self.assertEqual(self.events(), [1, 2, 3, 4, 5, 6])
        self.assertEqual(
            list(self.array("thread_fields", 7)),
            [
                0x0047E879,
                0x0078EBCC,
                0x1000,
                0,
                0x36,
                0x2003FA98,
                0x20071EA0,
            ],
        )
        self.assertEqual(self.word("thread_handle").value, 0x12345678)
        self.assertEqual(self.word("fail_stop_calls").value, 0)

    def test_core_initialization_precedes_fresh_prerequisite_read(self) -> None:
        self.word("core_sets_prerequisite").value = 7
        self.word("thread_result").value = 1
        self.assertEqual(self.initialize(), 1)
        self.assertEqual(self.events(), [1, 2, 3, 4, 5, 6])
        self.assertEqual(self.word("prerequisite_reads").value, 1)

    def test_missing_prerequisite_enters_fail_stop_without_thread_work(
        self,
    ) -> None:
        self.assertEqual(self.initialize(), 0)
        self.assertEqual(self.events(), [1, 2, 7])
        self.assertEqual(self.word("attribute_calls").value, 0)
        self.assertEqual(self.word("thread_calls").value, 0)
        self.assertEqual(self.word("store_calls").value, 0)

    def test_null_thread_is_published_before_fail_stop(self) -> None:
        self.word("prerequisite").value = 1
        self.word("thread_handle").value = 0xAAAAAAAA
        self.assertEqual(self.initialize(), 0)
        self.assertEqual(self.events(), [1, 2, 3, 4, 5, 6, 7])
        self.assertEqual(self.word("thread_handle").value, 0)
        self.assertEqual(self.word("fail_stop_calls").value, 1)

    def test_attribute_outputs_are_forwarded_after_zero_initialization(
        self,
    ) -> None:
        self.word("prerequisite").value = 1
        self.word("thread_result").value = 2
        self.array("attribute_values", 3)[:] = [
            0x11111111,
            0x22222222,
            0x33333333,
        ]
        self.assertEqual(self.initialize(), 1)
        self.assertEqual(list(self.array("attribute_inputs", 2)), [0, 0])
        self.assertEqual(
            list(self.array("thread_fields", 7))[2:],
            [
                0x33333333,
                0,
                0x36,
                0x22222222,
                0x11111111,
            ],
        )

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "c321aff8f277460c636ce8a63b3bb29816afda1ebeb27656be00d8b015fd295a",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "21a1f2345a199c2050c4bdf74221a8ff86316f908f287051f94e153bdc13041f",
        )


if __name__ == "__main__":
    unittest.main()
