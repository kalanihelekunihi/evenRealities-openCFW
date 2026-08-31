#!/usr/bin/env python3

from __future__ import annotations

import ctypes
from pathlib import Path
import random
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
PORT = ROOT / "components/shared/em9305/qpc_port"
QPC = ROOT / "third_party/qpc"

ENTRY = ctypes.CFUNCTYPE(ctypes.c_uint32, ctypes.c_void_p)
EXIT = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_uint32)
ACTION = ctypes.CFUNCTYPE(None, ctypes.c_void_p)
ISR = ctypes.CFUNCTYPE(ctypes.c_uint32, ctypes.c_void_p)
ASSERT = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int32)


class Providers(ctypes.Structure):
    _fields_ = [
        ("context", ctypes.c_void_p),
        ("critical_entry", ENTRY),
        ("critical_exit", EXIT),
        ("interrupt_disable", ACTION),
        ("interrupt_enable", ACTION),
        ("isr_context", ISR),
        ("startup", ACTION),
        ("cleanup", ACTION),
        ("idle", ACTION),
        ("assertion", ASSERT),
    ]


class Em9305QpcPortTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        compiler = shutil.which("clang") or shutil.which("cc")
        if compiler is None:
            raise unittest.SkipTest("no host C compiler")
        cls.compiler = compiler
        cls.temporary = tempfile.TemporaryDirectory(prefix="opencfw-em9305-qpc-port-")
        library = Path(cls.temporary.name) / "libem9305_qpc_port.so"
        subprocess.run(
            [
                compiler, "-std=gnu99", "-O2", "-fPIC", "-shared",
                "-ffreestanding", "-fno-builtin", "-Wall", "-Wextra",
                "-Werror", "-Wno-zero-length-array",
                "-I", str(QPC / "ports/em9305"),
                "-I", str(QPC / "include"),
                "-I", str(QPC / "src"),
                "-I", str(PORT),
                str(PORT / "runtime_qpc_port.c"),
                str(PORT / "runtime_arc_gcc_helpers.c"),
                "-o", str(library),
            ],
            check=True, capture_output=True, text=True,
        )
        cls.library = ctypes.CDLL(str(library))
        cls.install = cls.library.open_cfw_em9305_qpc_port_install
        cls.install.argtypes = [ctypes.POINTER(Providers)]
        cls.install.restype = ctypes.c_int32
        cls.library.open_cfw_em9305_qpc_port_is_configured.restype = ctypes.c_uint32
        cls.library.open_cfw_em9305_qpc_port_last_fault.restype = ctypes.c_int32
        cls.library.open_cfw_em9305_qf_crit_entry.restype = ctypes.c_uint32
        cls.library.open_cfw_em9305_qf_crit_exit.argtypes = [ctypes.c_uint32]
        cls.multiply = getattr(cls.library, "__mulsi3")
        cls.multiply.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.multiply.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        if hasattr(cls, "temporary"):
            cls.temporary.cleanup()

    def setUp(self) -> None:
        self.library.open_cfw_em9305_qpc_port_reset()

    def test_install_rejects_every_incomplete_required_provider_table(self) -> None:
        self.assertEqual(self.install(None), -1)
        providers = Providers()
        self.assertEqual(self.install(ctypes.byref(providers)), -1)
        self.assertEqual(self.library.open_cfw_em9305_qpc_port_is_configured(), 0)

    def test_complete_table_routes_critical_interrupt_and_lifecycle_calls(self) -> None:
        events: list[tuple[str, int]] = []
        context_value = 0x9305

        def context(pointer) -> int:
            return ctypes.cast(pointer, ctypes.c_void_p).value or 0

        @ENTRY
        def enter(pointer):
            events.append(("enter", context(pointer)))
            return 0xA5A55A5A

        @EXIT
        def leave(pointer, status):
            events.append(("exit", status ^ context(pointer)))

        @ACTION
        def disable(pointer):
            events.append(("disable", context(pointer)))

        @ACTION
        def enable(pointer):
            events.append(("enable", context(pointer)))

        @ISR
        def in_isr(pointer):
            events.append(("isr", context(pointer)))
            return 7

        @ACTION
        def startup(pointer):
            events.append(("startup", context(pointer)))

        @ACTION
        def cleanup(pointer):
            events.append(("cleanup", context(pointer)))

        @ACTION
        def idle(pointer):
            events.append(("idle", context(pointer)))

        @ASSERT
        def assertion(_pointer, _module, _location):
            self.fail("assertion provider must not run on the valid path")

        providers = Providers(
            ctypes.c_void_p(context_value), enter, leave, disable, enable,
            in_isr, startup, cleanup, idle, assertion,
        )
        self.assertEqual(self.install(ctypes.byref(providers)), 0)
        self.assertEqual(self.library.open_cfw_em9305_qpc_port_is_configured(), 1)
        self.assertEqual(self.library.open_cfw_em9305_qpc_port_last_fault(), 0)
        self.assertEqual(self.library.open_cfw_em9305_qf_crit_entry(), 0xA5A55A5A)
        self.library.open_cfw_em9305_qf_crit_exit(0x10203040)
        self.library.open_cfw_em9305_qf_int_disable()
        self.library.open_cfw_em9305_qf_int_enable()
        self.assertEqual(self.library.open_cfw_em9305_qk_isr_context(), 1)
        self.library.QF_onStartup()
        self.library.QF_onCleanup()
        self.library.QK_onIdle()
        self.assertEqual(
            [event[0] for event in events],
            ["enter", "exit", "disable", "enable", "isr", "startup", "cleanup", "idle"],
        )

    def test_cleanup_is_the_only_optional_callback(self) -> None:
        @ENTRY
        def enter(_context):
            return 0

        @EXIT
        def leave(_context, _status):
            return None

        @ACTION
        def action(_context):
            return None

        @ISR
        def in_isr(_context):
            return 0

        @ASSERT
        def assertion(_context, _module, _location):
            return None

        providers = Providers(None, enter, leave, action, action, in_isr,
                              action, ACTION(), action, assertion)
        self.assertEqual(self.install(ctypes.byref(providers)), 0)
        self.library.QF_onCleanup()

    def test_freestanding_multiply_helper_matches_low_word_semantics(self) -> None:
        rng = random.Random(0x9305)
        vectors = [(0, 0), (1, 1), (0xFFFFFFFF, 2), (0x80000000, 3)]
        vectors.extend((rng.getrandbits(32), rng.getrandbits(32)) for _ in range(2000))
        for left, right in vectors:
            self.assertEqual(self.multiply(left, right), (left * right) & 0xFFFFFFFF)


if __name__ == "__main__":
    unittest.main()
