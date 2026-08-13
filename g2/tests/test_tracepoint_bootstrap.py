from __future__ import annotations

import os

import ctypes
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


OPENCFW_ROOT = Path(__file__).resolve().parent.parent
COMPONENT_ROOT = OPENCFW_ROOT / "components" / "apollo_main" / "core_overlay"
SOURCE = COMPONENT_ROOT / "tracepoint_bootstrap.c"
FIXTURE = (
    OPENCFW_ROOT / "tests" / "fixtures" / "tracepoint_bootstrap_host.c"
)


class TracepointBootstrapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "tracepoint_bootstrap.dylib"
            if sys.platform == "darwin"
            else "tracepoint_bootstrap.so"
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
            cls.loaded.open_cfw_test_tracepoint_bootstrap_reset
        )
        cls.reset_fixture.argtypes = []
        cls.reset_fixture.restype = None
        cls.set_existing_handle = (
            cls.loaded.open_cfw_test_tracepoint_bootstrap_set_existing_handle
        )
        cls.set_existing_handle.argtypes = [ctypes.c_uint]
        cls.set_existing_handle.restype = None
        cls.has_handle = (
            cls.loaded.open_cfw_test_tracepoint_bootstrap_has_handle
        )
        cls.has_handle.argtypes = []
        cls.has_handle.restype = ctypes.c_uint
        cls.storage_matches = (
            cls.loaded
            .open_cfw_test_tracepoint_bootstrap_storage_argument_matches
        )
        cls.storage_matches.argtypes = []
        cls.storage_matches.restype = ctypes.c_uint
        cls.initialize = cls.loaded.open_cfw_tracepoint_runtime_initialize
        cls.initialize.argtypes = []
        cls.initialize.restype = None
        cls.invoke_callback = (
            cls.loaded.open_cfw_test_tracepoint_bootstrap_invoke_callback
        )
        cls.invoke_callback.argtypes = [ctypes.c_void_p]
        cls.invoke_callback.restype = None

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset_fixture()

    @classmethod
    def word(cls, suffix: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_tracepoint_bootstrap_{suffix}",
        )

    @classmethod
    def uintptr(cls, suffix: str) -> ctypes.c_size_t:
        return ctypes.c_size_t.in_dll(
            cls.loaded,
            f"open_cfw_test_tracepoint_bootstrap_{suffix}",
        )

    @classmethod
    def text(cls, suffix: str, capacity: int) -> str:
        value = (ctypes.c_char * capacity).in_dll(
            cls.loaded,
            f"open_cfw_test_tracepoint_bootstrap_{suffix}",
        )
        return bytes(value).split(b"\0", 1)[0].decode()

    @classmethod
    def events(cls) -> list[int]:
        count = cls.word("event_count").value
        values = (ctypes.c_uint * 16).in_dll(
            cls.loaded,
            "open_cfw_test_tracepoint_bootstrap_events",
        )
        return list(values[:count])

    def test_existing_handle_makes_initialization_idempotent(self) -> None:
        self.set_existing_handle(1)
        self.initialize()
        self.assertEqual(self.events(), [])
        self.assertEqual(self.word("create_calls").value, 0)
        self.assertEqual(self.word("setup_calls").value, 0)
        self.assertEqual(self.word("begin_calls").value, 0)
        self.assertEqual(self.word("fatal_calls").value, 0)
        self.assertEqual(self.has_handle(), 1)

    def test_success_preserves_timer_abi_and_call_order(self) -> None:
        self.initialize()
        self.assertEqual(self.events(), [1, 2, 3])
        self.assertEqual(self.word("create_calls").value, 1)
        self.assertEqual(self.word("setup_calls").value, 1)
        self.assertEqual(self.word("begin_calls").value, 1)
        self.assertEqual(self.word("fatal_calls").value, 0)
        self.assertEqual(self.text("name", 32), "tracepoint_defer")
        self.assertEqual(self.word("period").value, 2000)
        self.assertEqual(self.word("auto_reload").value, 0)
        self.assertEqual(self.word("identifier").value, 0)
        self.assertNotEqual(self.uintptr("callback_argument").value, 0)
        self.assertEqual(self.storage_matches(), 1)
        self.assertEqual(self.uintptr("handle_seen_by_create").value, 0)
        self.assertNotEqual(
            self.uintptr("handle_seen_by_setup").value,
            0,
        )
        self.assertEqual(
            self.uintptr("handle_seen_by_setup").value,
            self.uintptr("handle_seen_by_begin").value,
        )
        self.assertEqual(self.has_handle(), 1)

    def test_created_handle_suppresses_repeated_initialization(self) -> None:
        self.initialize()
        self.initialize()
        self.assertEqual(self.events(), [1, 2, 3])
        self.assertEqual(self.word("create_calls").value, 1)
        self.assertEqual(self.word("setup_calls").value, 1)
        self.assertEqual(self.word("begin_calls").value, 1)

    def test_null_creation_result_takes_only_fail_stop_path(self) -> None:
        self.word("create_null").value = 1
        self.initialize()
        self.assertEqual(self.events(), [1, 4])
        self.assertEqual(self.word("create_calls").value, 1)
        self.assertEqual(self.word("fatal_calls").value, 1)
        self.assertEqual(self.word("setup_calls").value, 0)
        self.assertEqual(self.word("begin_calls").value, 0)
        self.assertEqual(self.has_handle(), 0)

    def test_registered_callback_uses_void_pointer_timer_abi(self) -> None:
        self.initialize()
        self.invoke_callback(ctypes.c_void_p(0xA5A55A5A))
        self.assertEqual(self.events(), [1, 2, 3, 5])
        self.assertEqual(self.word("callback_calls").value, 1)
        self.assertEqual(
            self.uintptr("callback_timer_argument").value,
            0xA5A55A5A,
        )


if __name__ == "__main__":
    unittest.main()
