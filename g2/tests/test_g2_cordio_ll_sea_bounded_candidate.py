#!/usr/bin/env python3

from __future__ import annotations

import ctypes
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_cordio_ll_sea_bounded_candidate.py"
SOURCE = ROOT / "components/shared/cordio/runtime_cordio_ll_sea_bounded_candidate.c"

OK = 0
INVALID_ARGUMENT = 1
READ_FAILED = 2
UNSUPPORTED_EXTERNAL = 3
PROVIDER_FAILED = 4


def load_analyzer():
    spec = importlib.util.spec_from_file_location(
        "analyze_g2_cordio_ll_sea_bounded_candidate", ANALYZER,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load bounded Cordio/LL sea analyzer")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


READ16 = ctypes.CFUNCTYPE(
    ctypes.c_int, ctypes.c_void_p, ctypes.c_uint32,
    ctypes.POINTER(ctypes.c_uint16),
)
READ32 = ctypes.CFUNCTYPE(
    ctypes.c_int, ctypes.c_void_p, ctypes.c_uint32,
    ctypes.POINTER(ctypes.c_uint32),
)


class Reader(ctypes.Structure):
    _fields_ = [("context", ctypes.c_void_p), ("read_u16", READ16), ("read_u32", READ32)]


class ExternalEvidence(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_int),
        ("stock_start", ctypes.c_uint32),
        ("stock_end_exclusive", ctypes.c_uint32),
        ("stock_bytes", ctypes.c_size_t),
        ("stock_sha256", ctypes.c_char_p),
    ]


class Invocation(ctypes.Structure):
    _fields_ = [("words", ctypes.c_size_t * 8)]


EXTERNAL = ctypes.CFUNCTYPE(
    ctypes.c_int, ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(Invocation),
)


class CordioLlSeaBoundedCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        compiler = shutil.which("clang") or shutil.which("cc")
        if compiler is None:
            raise unittest.SkipTest("no host C compiler")
        cls.compiler = compiler
        cls.temporary = tempfile.TemporaryDirectory(prefix="opencfw-cordio-ll-sea-")
        library = Path(cls.temporary.name) / "libcordio_ll_sea.so"
        subprocess.run(
            [
                compiler, "-std=c11", "-O2", "-fPIC", "-shared",
                "-ffreestanding", "-fno-builtin", "-Wall", "-Wextra", "-Werror",
                "-I", str(SOURCE.parent), str(SOURCE), "-o", str(library),
            ],
            check=True, capture_output=True, text=True,
        )
        cls.library = ctypes.CDLL(str(library))
        cls.library.open_cfw_cordio_ll_sea_external_evidence.argtypes = [ctypes.c_int]
        cls.library.open_cfw_cordio_ll_sea_external_evidence.restype = ctypes.POINTER(ExternalEvidence)
        cls.external = cls.library.open_cfw_cordio_ll_sea_external_candidate
        cls.external.argtypes = [ctypes.c_int, EXTERNAL, ctypes.c_void_p, ctypes.POINTER(Invocation)]
        cls.external.restype = ctypes.c_int
        cls.library.open_cfw_cordio_ll_sea_write_once_u32_candidate.argtypes = [
            ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint32,
        ]
        cls.accessors = (
            "open_cfw_cordio_ll_sea_load_field_218_candidate",
            "open_cfw_cordio_ll_sea_load_field_214_plus_c28_candidate",
            "open_cfw_cordio_ll_sea_nested_halfword_q16_candidate",
            "open_cfw_cordio_ll_sea_nested_word_190_q16_candidate",
            "open_cfw_cordio_ll_sea_nested_word_18c_q16_candidate",
        )
        for name in cls.accessors:
            function = getattr(cls.library, name)
            function.argtypes = [ctypes.POINTER(Reader), ctypes.c_uint32,
                                 ctypes.POINTER(ctypes.c_uint32)]
            function.restype = ctypes.c_int

    @classmethod
    def tearDownClass(cls) -> None:
        if hasattr(cls, "temporary"):
            cls.temporary.cleanup()

    def make_reader(self, words: dict[int, int], halfwords: dict[int, int],
                    reads: list[tuple[int, int]]) -> tuple[Reader, READ16, READ32]:
        @READ16
        def read16(_context, address, output):
            reads.append((16, address))
            if address not in halfwords:
                return READ_FAILED
            output[0] = halfwords[address]
            return OK

        @READ32
        def read32(_context, address, output):
            reads.append((32, address))
            if address not in words:
                return READ_FAILED
            output[0] = words[address]
            return OK

        return Reader(None, read16, read32), read16, read32

    def test_analyzer_closes_all_medium_confidence_functions(self) -> None:
        result = self.analyzer.run_audit()
        self.assertEqual(result["status"], "candidate-qualified-bounded")
        self.assertTrue(result["read_only"])
        self.assertFalse(result["hardware_operations"])
        self.assertEqual(result["license"], "Apache-2.0")
        self.assertFalse(result["corrected_sea"]["lvgl_attribution"])
        self.assertFalse(result["corrected_sea"]["per_module_source_attribution_proven"])
        self.assertFalse(result["corrected_sea"]["corpus_metadata_reconciled"])
        self.assertEqual(
            result["corrected_sea"]["checked_in_summary_corpus_sha256"],
            "87d0befa001f042918bd6af83b0f50e13dd95aab160b0e520f2cb0bc55c6404e",
        )
        self.assertEqual(
            result["corrected_sea"]["current_authenticated_corpus_sha256"],
            "3ff8aa908e5841823df9384cfbffca91d657816274797f332a45ff93a8aa832f",
        )
        tranche = result["medium_confidence_tranche"]
        self.assertEqual((tranche["functions"], tranche["bytes"]), (12, 9_420))
        self.assertEqual(tranche["concrete"], {"functions": 6, "bytes": 64})
        self.assertEqual(tranche["typed_external"], {"functions": 6, "bytes": 9_356})
        self.assertEqual(result["unselected_sea_boundary"], {
            "functions": 288, "bytes": 43_446,
            "policy": "unsupported external; not admitted by this tranche",
        })
        self.assertFalse(result["candidate"]["production_routed"])

    def test_write_once_semantics_include_null_and_existing_error(self) -> None:
        function = self.library.open_cfw_cordio_ll_sea_write_once_u32_candidate
        slot = ctypes.c_uint32(0)
        function(ctypes.byref(slot), 0x12)
        self.assertEqual(slot.value, 0x12)
        function(ctypes.byref(slot), 0x34)
        self.assertEqual(slot.value, 0x12)
        function(None, 0x56)

    def test_two_direct_field_accessors_use_exact_offsets(self) -> None:
        base = 0x1000
        reads: list[tuple[int, int]] = []
        reader, read16, read32 = self.make_reader(
            {base + 0x218: 0xAABBCCDD, base + 0x214: 0x2000}, {}, reads,
        )
        output = ctypes.c_uint32()
        first = self.library.open_cfw_cordio_ll_sea_load_field_218_candidate
        second = self.library.open_cfw_cordio_ll_sea_load_field_214_plus_c28_candidate
        self.assertEqual(first(ctypes.byref(reader), base, ctypes.byref(output)), OK)
        self.assertEqual(output.value, 0xAABBCCDD)
        self.assertEqual(second(ctypes.byref(reader), base, ctypes.byref(output)), OK)
        self.assertEqual(output.value, 0x2C28)
        self.assertEqual(reads, [(32, base + 0x218), (32, base + 0x214)])
        self.assertIsNotNone(read16)
        self.assertIsNotNone(read32)

    def test_nested_halfword_accessor_preserves_read_order_and_q16(self) -> None:
        base, first, second = 0x1000, 0x2000, 0x3000
        reads: list[tuple[int, int]] = []
        reader, _read16, _read32 = self.make_reader(
            {base + 4: first, first + 0x58: second},
            {second + 0x0E: 0xFEDC}, reads,
        )
        output = ctypes.c_uint32()
        function = self.library.open_cfw_cordio_ll_sea_nested_halfword_q16_candidate
        self.assertEqual(function(ctypes.byref(reader), base, ctypes.byref(output)), OK)
        self.assertEqual(output.value, 0xFEDC0000)
        self.assertEqual(reads, [(32, base + 4), (32, first + 0x58), (16, second + 0x0E)])

    def test_nested_word_accessors_use_190_and_18c_and_wrap_q16(self) -> None:
        base, nested = 0x4000, 0x5000
        reads: list[tuple[int, int]] = []
        reader, _read16, _read32 = self.make_reader(
            {base + 0x218: nested, nested + 0x190: 0x12345678,
             nested + 0x18C: 0x89ABCDEF}, {}, reads,
        )
        output = ctypes.c_uint32()
        f190 = self.library.open_cfw_cordio_ll_sea_nested_word_190_q16_candidate
        f18c = self.library.open_cfw_cordio_ll_sea_nested_word_18c_q16_candidate
        self.assertEqual(f190(ctypes.byref(reader), base, ctypes.byref(output)), OK)
        self.assertEqual(output.value, 0x56780000)
        self.assertEqual(f18c(ctypes.byref(reader), base, ctypes.byref(output)), OK)
        self.assertEqual(output.value, 0xCDEF0000)
        self.assertEqual(reads, [
            (32, base + 0x218), (32, nested + 0x190),
            (32, base + 0x218), (32, nested + 0x18C),
        ])

    def test_reader_failures_and_invalid_arguments_fail_closed(self) -> None:
        reads: list[tuple[int, int]] = []
        reader, _read16, _read32 = self.make_reader({}, {}, reads)
        output = ctypes.c_uint32()
        for name in self.accessors:
            function = getattr(self.library, name)
            self.assertEqual(function(ctypes.byref(reader), 0x1000,
                                      ctypes.byref(output)), READ_FAILED)
            self.assertEqual(function(None, 0x1000, ctypes.byref(output)),
                             INVALID_ARGUMENT)
            self.assertEqual(function(ctypes.byref(reader), 0x1000, None),
                             INVALID_ARGUMENT)

    def test_external_map_and_provider_boundary(self) -> None:
        total = 0
        for external_id in range(6):
            pointer = self.library.open_cfw_cordio_ll_sea_external_evidence(external_id)
            self.assertTrue(pointer)
            item = pointer.contents
            self.assertEqual(item.id, external_id)
            self.assertEqual(item.stock_end_exclusive - item.stock_start, item.stock_bytes)
            self.assertEqual(len(item.stock_sha256.decode()), 64)
            total += item.stock_bytes
        self.assertEqual(total, 9_356)
        self.assertFalse(self.library.open_cfw_cordio_ll_sea_external_evidence(6))
        invocation = Invocation(tuple(range(8)))
        null_provider = EXTERNAL()
        self.assertEqual(self.external(0, null_provider, None,
                                       ctypes.byref(invocation)), UNSUPPORTED_EXTERNAL)
        calls = []

        @EXTERNAL
        def provider(context, external_id, arguments):
            calls.append((ctypes.cast(context, ctypes.c_void_p).value,
                          external_id, list(arguments.contents.words)))
            return OK

        self.assertEqual(self.external(5, provider, ctypes.c_void_p(0x55),
                                       ctypes.byref(invocation)), OK)
        self.assertEqual(calls, [(0x55, 5, list(range(8)))])

        @EXTERNAL
        def failure(_context, _external_id, _arguments):
            return READ_FAILED

        self.assertEqual(self.external(5, failure, None,
                                       ctypes.byref(invocation)), PROVIDER_FAILED)

    def test_freestanding_object_has_no_undefined_runtime_imports(self) -> None:
        with tempfile.TemporaryDirectory(prefix="opencfw-cordio-ll-object-") as directory:
            output = Path(directory) / "candidate.o"
            subprocess.run(
                [
                    self.compiler, "-std=c11", "-O2", "-ffreestanding",
                    "-fno-builtin", "-fno-stack-protector", "-Wall", "-Wextra",
                    "-Werror", "-I", str(SOURCE.parent), "-c", str(SOURCE),
                    "-o", str(output),
                ],
                check=True, capture_output=True, text=True,
            )
            nm = shutil.which("nm")
            if nm is not None:
                undefined = subprocess.run(
                    [nm, "-u", str(output)], check=True, capture_output=True, text=True,
                ).stdout.strip()
                self.assertEqual(undefined, "")

    def test_json_cli_is_machine_readable(self) -> None:
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        completed = subprocess.run(
            [sys.executable, str(ANALYZER), "--json"], cwd=ROOT,
            env=environment, check=True, capture_output=True, text=True,
        )
        result = json.loads(completed.stdout)
        self.assertEqual(result["medium_confidence_tranche"]["bytes"], 9_420)
        self.assertFalse(result["corrected_sea"]["lvgl_attribution"])


if __name__ == "__main__":
    unittest.main()
