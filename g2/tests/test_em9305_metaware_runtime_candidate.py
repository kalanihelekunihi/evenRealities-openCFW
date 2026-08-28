#!/usr/bin/env python3

from __future__ import annotations

import ctypes
import importlib.util
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_em9305_metaware_runtime_candidate.py"
SOURCE = ROOT / "components/shared/em9305/runtime_metaware_helpers_candidate.c"
HEADER = SOURCE.with_suffix(".h")
MASK64 = (1 << 64) - 1
INT64_MIN = -(1 << 63)


def load_analyzer():
    spec = importlib.util.spec_from_file_location(
        "analyze_em9305_metaware_runtime_candidate",
        ANALYZER,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load EM9305 MetaWare candidate analyzer")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Em9305MetaWareRuntimeCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        compiler = shutil.which("clang") or shutil.which("cc")
        if compiler is None:
            raise unittest.SkipTest("no host C compiler")
        cls.compiler = compiler
        cls.temporary = tempfile.TemporaryDirectory(prefix="opencfw-em9305-runtime-")
        library = Path(cls.temporary.name) / "libem9305_runtime.so"
        subprocess.run(
            [
                compiler,
                "-std=c11",
                "-O2",
                "-fPIC",
                "-shared",
                "-ffreestanding",
                "-fno-builtin",
                "-Wall",
                "-Wextra",
                "-Werror",
                "-I",
                str(SOURCE.parent),
                str(SOURCE),
                "-o",
                str(library),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        cls.library = ctypes.CDLL(str(library))
        for name in (
            "open_cfw_em9305_metaware_memmove_candidate",
            "open_cfw_em9305_metaware_memcpy_candidate",
            "open_cfw_em9305_metaware_memset_candidate",
        ):
            function = getattr(cls.library, name)
            function.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t]
            function.restype = ctypes.c_void_p
        cls.library.open_cfw_em9305_metaware_memset_candidate.argtypes = [
            ctypes.c_void_p,
            ctypes.c_int,
            ctypes.c_size_t,
        ]
        cls.library.open_cfw_em9305_metaware_udiv64_candidate.argtypes = [
            ctypes.c_uint64,
            ctypes.c_uint64,
        ]
        cls.library.open_cfw_em9305_metaware_udiv64_candidate.restype = ctypes.c_uint64
        cls.library.open_cfw_em9305_metaware_sdiv64_candidate.argtypes = [
            ctypes.c_int64,
            ctypes.c_int64,
        ]
        cls.library.open_cfw_em9305_metaware_sdiv64_candidate.restype = ctypes.c_int64
        for name in (
            "open_cfw_em9305_metaware_shift_left64_candidate",
            "open_cfw_em9305_metaware_shift_right64_candidate",
        ):
            function = getattr(cls.library, name)
            function.argtypes = [ctypes.c_uint64, ctypes.c_uint32]
            function.restype = ctypes.c_uint64
        cls.library.open_cfw_em9305_metaware_stack_pointer_in_bounds.argtypes = [
            ctypes.c_size_t,
            ctypes.c_size_t,
            ctypes.c_size_t,
        ]
        cls.library.open_cfw_em9305_metaware_stack_pointer_in_bounds.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        if hasattr(cls, "temporary"):
            cls.temporary.cleanup()

    def test_audit_authenticates_both_islands_and_ten_entries(self) -> None:
        result = self.analyzer.run_audit()
        self.assertEqual(result["status"], "candidate-qualified")
        self.assertTrue(result["read_only"])
        self.assertFalse(result["hardware_operations"])
        self.assertEqual(result["license"], "MIT")
        self.assertEqual(result["stock_runtime"]["total_bytes"], 980)
        self.assertEqual(
            [item["bytes"] for item in result["stock_runtime"]["islands"].values()],
            [822, 158],
        )
        self.assertEqual(len(result["stock_runtime"]["entries"]), 10)
        self.assertEqual(
            result["stock_runtime"]["entries"]["0x00332FC4"]["reference_count"],
            199,
        )
        self.assertEqual(
            result["stock_runtime"]["entries"]["0x0033301C"]["reference_count"],
            153,
        )
        self.assertFalse(result["candidate"]["production_routed"])

    def test_memcpy_and_memset_semantics_and_return_values(self) -> None:
        source = (ctypes.c_ubyte * 257)(*[index & 0xFF for index in range(257)])
        destination = (ctypes.c_ubyte * 257)()
        returned = self.library.open_cfw_em9305_metaware_memcpy_candidate(
            destination,
            source,
            257,
        )
        self.assertEqual(returned, ctypes.addressof(destination))
        self.assertEqual(bytes(destination), bytes(source))

        returned = self.library.open_cfw_em9305_metaware_memset_candidate(
            ctypes.byref(destination, 3),
            0x1AB,
            251,
        )
        self.assertEqual(returned, ctypes.addressof(destination) + 3)
        self.assertEqual(bytes(destination)[3:254], b"\xAB" * 251)

    def test_memmove_all_overlap_directions(self) -> None:
        for source_offset, destination_offset, length in (
            (0, 0, 64),
            (0, 1, 63),
            (1, 0, 63),
            (0, 32, 32),
            (32, 0, 32),
            (7, 23, 41),
            (23, 7, 41),
            (12, 18, 0),
        ):
            initial = bytearray(range(96))
            expected = bytearray(initial)
            expected[destination_offset:destination_offset + length] = bytes(
                initial[source_offset:source_offset + length]
            )
            buffer = (ctypes.c_ubyte * len(initial)).from_buffer_copy(initial)
            returned = self.library.open_cfw_em9305_metaware_memmove_candidate(
                ctypes.byref(buffer, destination_offset),
                ctypes.byref(buffer, source_offset),
                length,
            )
            self.assertEqual(returned, ctypes.addressof(buffer) + destination_offset)
            self.assertEqual(bytes(buffer), bytes(expected))

    def test_unsigned_division_boundary_and_random_vectors(self) -> None:
        vectors = [
            (0, 1), (1, 1), (MASK64, 1), (MASK64, MASK64),
            (1 << 63, 3), (MASK64, 0xFFFFFFFF), (123, 0),
        ]
        rng = random.Random(0x9305)
        vectors.extend((rng.getrandbits(64), rng.getrandbits(64)) for _ in range(2_000))
        for dividend, divisor in vectors:
            expected = MASK64 if divisor == 0 else dividend // divisor
            self.assertEqual(
                self.library.open_cfw_em9305_metaware_udiv64_candidate(
                    dividend,
                    divisor,
                ),
                expected,
                (dividend, divisor),
            )

    def test_signed_division_wrap_zero_and_random_vectors(self) -> None:
        vectors = [
            (0, 1), (1, 1), (-1, 1), (1, -1), (-1, -1),
            (INT64_MIN, -1), (INT64_MIN, 1), ((1 << 63) - 1, 3),
            (7, 0), (-7, 0),
        ]
        rng = random.Random(0x202209)
        for _ in range(2_000):
            dividend = ctypes.c_int64(rng.getrandbits(64)).value
            divisor = ctypes.c_int64(rng.getrandbits(64)).value
            vectors.append((dividend, divisor))
        for dividend, divisor in vectors:
            if divisor == 0:
                expected = 1 if dividend < 0 else -1
            elif dividend == INT64_MIN and divisor == -1:
                expected = INT64_MIN
            else:
                magnitude = abs(dividend) // abs(divisor)
                expected = -magnitude if (dividend < 0) != (divisor < 0) else magnitude
            self.assertEqual(
                self.library.open_cfw_em9305_metaware_sdiv64_candidate(
                    dividend,
                    divisor,
                ),
                expected,
                (dividend, divisor),
            )

    def test_shift_counts_are_masked_to_six_bits(self) -> None:
        values = (0, 1, 0x0123456789ABCDEF, MASK64)
        counts = (0, 1, 31, 32, 63, 64, 65, 127, 128, 0xFFFFFFFF)
        for value in values:
            for count in counts:
                shift = count & 63
                self.assertEqual(
                    self.library.open_cfw_em9305_metaware_shift_left64_candidate(value, count),
                    (value << shift) & MASK64,
                )
                self.assertEqual(
                    self.library.open_cfw_em9305_metaware_shift_right64_candidate(value, count),
                    value >> shift,
                )

    def test_stack_bounds_are_inclusive_and_reject_inverted_bounds(self) -> None:
        check = self.library.open_cfw_em9305_metaware_stack_pointer_in_bounds
        self.assertEqual(check(0x80E977, 0x80E978, 0x80F978), 0)
        self.assertEqual(check(0x80E978, 0x80E978, 0x80F978), 1)
        self.assertEqual(check(0x80F978, 0x80E978, 0x80F978), 1)
        self.assertEqual(check(0x80F979, 0x80E978, 0x80F978), 0)
        self.assertEqual(check(5, 10, 1), 0)

    def test_stack_guard_calls_injected_trap_only_out_of_bounds(self) -> None:
        callback_type = ctypes.CFUNCTYPE(None, ctypes.c_void_p)
        calls: list[int] = []

        @callback_type
        def trap(context):
            calls.append(ctypes.cast(context, ctypes.c_void_p).value or 0)

        guard = self.library.open_cfw_em9305_metaware_stack_guard_candidate
        guard.argtypes = [ctypes.c_size_t, callback_type, ctypes.c_void_p]
        guard.restype = ctypes.c_uint32
        self.assertEqual(guard(0x80E978, trap, ctypes.c_void_p(0x55)), 1)
        self.assertEqual(calls, [])
        self.assertEqual(guard(0x80E977, trap, ctypes.c_void_p(0x55)), 0)
        self.assertEqual(calls, [0x55])

    def test_freestanding_object_has_no_runtime_imports(self) -> None:
        with tempfile.TemporaryDirectory(prefix="opencfw-em9305-object-") as directory:
            output = Path(directory) / "candidate.o"
            subprocess.run(
                [
                    self.compiler,
                    "-std=c11", "-O2", "-ffreestanding", "-fno-builtin",
                    "-fno-stack-protector", "-Wall", "-Wextra", "-Werror",
                    "-I", str(SOURCE.parent), "-c", str(SOURCE), "-o", str(output),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            nm = shutil.which("nm")
            if nm is not None:
                symbols = subprocess.run(
                    [nm, "-u", str(output)],
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout.strip()
                self.assertEqual(symbols, "")

    def test_json_cli_is_machine_readable(self) -> None:
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        completed = subprocess.run(
            [sys.executable, str(ANALYZER), "--json"],
            cwd=ROOT,
            env=env,
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)
        self.assertEqual(result["stock_runtime"]["total_bytes"], 980)
        self.assertFalse(result["candidate"]["uses_c_division_or_remainder"])


if __name__ == "__main__":
    unittest.main()
