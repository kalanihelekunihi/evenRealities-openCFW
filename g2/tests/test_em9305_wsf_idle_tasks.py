#!/usr/bin/env python3

from __future__ import annotations

import ctypes
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/shared/em9305/runtime_wsf_idle_tasks.c"
CAPACITY = 3
OK = 0
INVALID = 1
FULL = 2
CALLBACK = ctypes.CFUNCTYPE(ctypes.c_uint32)


class State(ctypes.Structure):
    _fields_ = [
        ("callbacks", CALLBACK * CAPACITY),
        ("callback_count", ctypes.c_uint8),
        ("pending", ctypes.c_uint8),
    ]


class Em9305WsfIdleTasksTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        compiler = shutil.which("clang") or shutil.which("cc")
        if compiler is None:
            raise unittest.SkipTest("no host C compiler")
        cls.compiler = compiler
        cls.temporary = tempfile.TemporaryDirectory(prefix="opencfw-em9305-wsf-idle-")
        library = Path(cls.temporary.name) / "libem9305_wsf_idle.so"
        subprocess.run(
            [
                compiler, "-std=c11", "-O2", "-fPIC", "-shared",
                "-ffreestanding", "-fno-builtin", "-Wall", "-Wextra", "-Werror",
                "-I", str(SOURCE.parent), str(SOURCE), "-o", str(library),
            ],
            check=True, capture_output=True, text=True,
        )
        cls.library = ctypes.CDLL(str(library))
        cls.initialize = cls.library.open_cfw_em9305_wsf_idle_state_init
        cls.initialize.argtypes = [ctypes.POINTER(State)]
        cls.register = cls.library.open_cfw_em9305_wsf_idle_register
        cls.register.argtypes = [ctypes.POINTER(State), CALLBACK]
        cls.register.restype = ctypes.c_int32
        cls.request = cls.library.open_cfw_em9305_wsf_idle_request
        cls.request.argtypes = [ctypes.POINTER(State)]
        cls.request.restype = ctypes.c_int32
        cls.run_idle = cls.library.open_cfw_em9305_wsf_os_run_idle_tasks
        cls.run_idle.argtypes = [ctypes.POINTER(State)]
        cls.run_idle.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        if hasattr(cls, "temporary"):
            cls.temporary.cleanup()

    def test_registration_is_bounded_and_null_safe(self) -> None:
        state = State()
        self.initialize(ctypes.byref(state))
        self.assertEqual((state.callback_count, state.pending), (0, 0))
        null_callback = CALLBACK()
        self.assertEqual(self.register(None, null_callback), INVALID)
        self.assertEqual(self.register(ctypes.byref(state), null_callback), INVALID)

        callbacks = [CALLBACK(lambda: 0) for _ in range(CAPACITY + 1)]
        for callback in callbacks[:CAPACITY]:
            self.assertEqual(self.register(ctypes.byref(state), callback), OK)
        self.assertEqual(self.register(ctypes.byref(state), callbacks[-1]), FULL)
        self.assertEqual(state.callback_count, CAPACITY)

    def test_pending_gate_order_and_one_bit_or_reduction(self) -> None:
        state = State()
        self.initialize(ctypes.byref(state))
        events: list[int] = []
        values = (2, 1, 4)
        callbacks = []
        for index, value in enumerate(values):
            @CALLBACK
            def callback(index=index, value=value):
                events.append(index)
                return value
            callbacks.append(callback)
            self.assertEqual(self.register(ctypes.byref(state), callback), OK)

        self.assertEqual(self.run_idle(ctypes.byref(state)), 0)
        self.assertEqual(events, [])
        self.assertEqual(self.request(ctypes.byref(state)), OK)
        self.assertEqual(self.run_idle(ctypes.byref(state)), 1)
        self.assertEqual(events, [0, 1, 2])
        self.assertEqual(state.pending, 1)

    def test_zero_activity_clears_pending_and_skips_future_calls(self) -> None:
        state = State()
        self.initialize(ctypes.byref(state))
        calls = 0

        @CALLBACK
        def inactive():
            nonlocal calls
            calls += 1
            return 0

        self.assertEqual(self.register(ctypes.byref(state), inactive), OK)
        self.assertEqual(self.request(ctypes.byref(state)), OK)
        self.assertEqual(self.run_idle(ctypes.byref(state)), 0)
        self.assertEqual(state.pending, 0)
        self.assertEqual(self.run_idle(ctypes.byref(state)), 0)
        self.assertEqual(calls, 1)

    def test_corrupt_count_fails_closed_without_callback_access(self) -> None:
        state = State()
        self.initialize(ctypes.byref(state))
        state.callback_count = CAPACITY + 1
        state.pending = 1
        self.assertEqual(self.request(ctypes.byref(state)), INVALID)
        self.assertEqual(self.run_idle(ctypes.byref(state)), 0)

    def test_freestanding_object_has_no_undefined_symbols(self) -> None:
        object_path = Path(self.temporary.name) / "wsf_idle.o"
        subprocess.run(
            [
                self.compiler, "-std=c11", "-O2", "-ffreestanding", "-fno-builtin",
                "-Wall", "-Wextra", "-Werror", "-I", str(SOURCE.parent),
                "-c", str(SOURCE), "-o", str(object_path),
            ],
            check=True, capture_output=True, text=True,
        )
        nm = shutil.which("nm")
        if nm is None:
            raise unittest.SkipTest("nm unavailable")
        completed = subprocess.run(
            [nm, "-u", str(object_path)], check=True, capture_output=True, text=True,
        )
        self.assertEqual(completed.stdout.strip(), "")


if __name__ == "__main__":
    unittest.main()
