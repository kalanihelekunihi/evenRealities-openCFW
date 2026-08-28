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
ANALYZER = ROOT / "tools/analyze_em9305_unclassified_tail_candidate.py"
SOURCE = ROOT / "components/shared/em9305/runtime_unclassified_tail_candidate.c"

OK = 0
INVALID_ARGUMENT = 1
UNSUPPORTED_EXTERNAL = 2
PROVIDER_FAILED = 3


def load_analyzer():
    spec = importlib.util.spec_from_file_location(
        "analyze_em9305_unclassified_tail_candidate", ANALYZER,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load EM9305 tail analyzer")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ExternalInvocation(ctypes.Structure):
    _fields_ = [("words", ctypes.c_size_t * 4)]


class ExternalEvidence(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_int),
        ("stock_start", ctypes.c_size_t),
        ("stock_end_exclusive", ctypes.c_size_t),
        ("stock_bytes", ctypes.c_size_t),
        ("stock_sha256", ctypes.c_char_p),
    ]


EXTERNAL_PROVIDER = ctypes.CFUNCTYPE(
    ctypes.c_int, ctypes.c_void_p, ctypes.c_int,
    ctypes.POINTER(ExternalInvocation),
)


class Em9305UnclassifiedTailCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        compiler = shutil.which("clang") or shutil.which("cc")
        if compiler is None:
            raise unittest.SkipTest("no host C compiler")
        cls.compiler = compiler
        cls.temporary = tempfile.TemporaryDirectory(prefix="opencfw-em9305-tail-")
        library = Path(cls.temporary.name) / "libem9305_tail.so"
        subprocess.run(
            [
                compiler, "-std=c11", "-O2", "-fPIC", "-shared",
                "-ffreestanding", "-fno-builtin", "-Wall", "-Wextra", "-Werror",
                "-I", str(SOURCE.parent), str(SOURCE), "-o", str(library),
            ],
            check=True, capture_output=True, text=True,
        )
        cls.library = ctypes.CDLL(str(library))
        cls.library.open_cfw_em9305_tail_external_evidence.argtypes = [ctypes.c_int]
        cls.library.open_cfw_em9305_tail_external_evidence.restype = ctypes.POINTER(ExternalEvidence)
        cls.external = cls.library.open_cfw_em9305_tail_external_candidate
        cls.external.argtypes = [
            ctypes.c_int, EXTERNAL_PROVIDER, ctypes.c_void_p,
            ctypes.POINTER(ExternalInvocation),
        ]
        cls.external.restype = ctypes.c_int

        for suffix, ctype in (("u8", ctypes.c_uint8), ("u16", ctypes.c_uint16),
                              ("u32", ctypes.c_uint32)):
            load = getattr(cls.library, f"open_cfw_em9305_tail_load_{suffix}_candidate")
            load.argtypes = [ctypes.POINTER(ctype), ctypes.POINTER(ctype)]
            load.restype = ctypes.c_int
            store = getattr(cls.library, f"open_cfw_em9305_tail_store_{suffix}_candidate")
            store.argtypes = [ctypes.POINTER(ctype), ctype]
            store.restype = ctypes.c_int
        cls.library.open_cfw_em9305_tail_load_u8_at_candidate.argtypes = [
            ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_uint8),
        ]
        cls.library.open_cfw_em9305_tail_load_u8_at_candidate.restype = ctypes.c_int
        cls.library.open_cfw_em9305_tail_store_u8_at_candidate.argtypes = [
            ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t, ctypes.c_uint8,
        ]
        cls.library.open_cfw_em9305_tail_store_u8_at_candidate.restype = ctypes.c_int
        cls.library.open_cfw_em9305_tail_u8_nonzero_candidate.argtypes = [ctypes.c_uint8]
        cls.library.open_cfw_em9305_tail_u8_nonzero_candidate.restype = ctypes.c_uint32
        cls.library.open_cfw_em9305_tail_u8_equals_candidate.argtypes = [
            ctypes.c_uint8, ctypes.c_uint8,
        ]
        cls.library.open_cfw_em9305_tail_u8_equals_candidate.restype = ctypes.c_uint32
        cls.library.open_cfw_em9305_tail_set_bits32_candidate.argtypes = [
            ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint32,
        ]
        cls.library.open_cfw_em9305_tail_set_bits32_candidate.restype = ctypes.c_int
        cls.library.open_cfw_em9305_tail_zero_memory_candidate.argtypes = [
            ctypes.c_void_p, ctypes.c_size_t,
        ]
        cls.library.open_cfw_em9305_tail_zero_memory_candidate.restype = ctypes.c_int

    @classmethod
    def tearDownClass(cls) -> None:
        if hasattr(cls, "temporary"):
            cls.temporary.cleanup()

    def test_analyzer_closes_all_36_spans_and_890_bytes(self) -> None:
        result = self.analyzer.run_audit()
        self.assertEqual(result["status"], "candidate-qualified-exhaustive")
        self.assertTrue(result["read_only"])
        self.assertFalse(result["hardware_operations"])
        self.assertEqual(result["license"], "MIT")
        tail = result["tail"]
        self.assertEqual(tail["span_count"], 36)
        self.assertEqual(tail["total_bytes"], 890)
        self.assertEqual(len(tail["decisions"]), 36)
        self.assertEqual(tail["partition"]["reconstructible"], {"spans": 21, "bytes": 260})
        self.assertEqual(tail["partition"]["unsupported_external"], {"spans": 15, "bytes": 630})
        self.assertTrue(all(
            item["ownership_claim"] == "unchanged-unclassified"
            for item in tail["decisions"].values()
        ))
        self.assertFalse(result["candidate"]["production_routed"])

    def test_external_evidence_map_is_closed(self) -> None:
        spans = []
        for external_id in range(15):
            pointer = self.library.open_cfw_em9305_tail_external_evidence(external_id)
            self.assertTrue(pointer)
            evidence = pointer.contents
            self.assertEqual(evidence.id, external_id)
            self.assertEqual(evidence.stock_end_exclusive - evidence.stock_start,
                             evidence.stock_bytes)
            self.assertEqual(len(evidence.stock_sha256.decode()), 64)
            spans.append(evidence.stock_bytes)
        self.assertEqual(sum(spans), 630)
        self.assertFalse(self.library.open_cfw_em9305_tail_external_evidence(-1))
        self.assertFalse(self.library.open_cfw_em9305_tail_external_evidence(15))

    def test_external_boundary_fails_closed_and_forwards_only_with_provider(self) -> None:
        invocation = ExternalInvocation((1, 2, 3, 4))
        null_provider = EXTERNAL_PROVIDER()
        self.assertEqual(
            self.external(0, null_provider, None, ctypes.byref(invocation)),
            UNSUPPORTED_EXTERNAL,
        )
        self.assertEqual(self.external(15, null_provider, None,
                                       ctypes.byref(invocation)), INVALID_ARGUMENT)
        self.assertEqual(self.external(0, null_provider, None, None), INVALID_ARGUMENT)
        calls = []

        @EXTERNAL_PROVIDER
        def provider(context, external_id, words):
            calls.append((ctypes.cast(context, ctypes.c_void_p).value,
                          external_id, list(words.contents.words)))
            return OK

        self.assertEqual(
            self.external(9, provider, ctypes.c_void_p(0x9305),
                          ctypes.byref(invocation)),
            OK,
        )
        self.assertEqual(calls, [(0x9305, 9, [1, 2, 3, 4])])

        @EXTERNAL_PROVIDER
        def failure(_context, _external_id, _words):
            return UNSUPPORTED_EXTERNAL

        self.assertEqual(
            self.external(9, failure, None, ctypes.byref(invocation)),
            PROVIDER_FAILED,
        )

    def test_scalar_accessors_and_invalid_arguments(self) -> None:
        for suffix, ctype, initial, changed in (
            ("u8", ctypes.c_uint8, 0xA5, 0x3C),
            ("u16", ctypes.c_uint16, 0xA55A, 0x3CC3),
            ("u32", ctypes.c_uint32, 0xA55A1234, 0x3CC3FEDC),
        ):
            storage, output = ctype(initial), ctype()
            load = getattr(self.library, f"open_cfw_em9305_tail_load_{suffix}_candidate")
            store = getattr(self.library, f"open_cfw_em9305_tail_store_{suffix}_candidate")
            self.assertEqual(load(ctypes.byref(storage), ctypes.byref(output)), OK)
            self.assertEqual(output.value, initial)
            self.assertEqual(store(ctypes.byref(storage), changed), OK)
            self.assertEqual(storage.value, changed)
            self.assertEqual(load(None, ctypes.byref(output)), INVALID_ARGUMENT)
            self.assertEqual(load(ctypes.byref(storage), None), INVALID_ARGUMENT)
            self.assertEqual(store(None, changed), INVALID_ARGUMENT)

    def test_offset_boolean_and_constant_setter_primitives(self) -> None:
        buffer = (ctypes.c_uint8 * 32)(*range(32))
        value = ctypes.c_uint8()
        load = self.library.open_cfw_em9305_tail_load_u8_at_candidate
        store = self.library.open_cfw_em9305_tail_store_u8_at_candidate
        self.assertEqual(load(buffer, 23, ctypes.byref(value)), OK)
        self.assertEqual(value.value, 23)
        self.assertEqual(store(buffer, 12, 0x30), OK)
        self.assertEqual(buffer[12], 0x30)
        self.assertEqual(load(None, 0, ctypes.byref(value)), INVALID_ARGUMENT)
        self.assertEqual(store(None, 0, 1), INVALID_ARGUMENT)
        nonzero = self.library.open_cfw_em9305_tail_u8_nonzero_candidate
        equals = self.library.open_cfw_em9305_tail_u8_equals_candidate
        self.assertEqual([nonzero(value) for value in (0, 1, 255)], [0, 1, 1])
        self.assertEqual(equals(1, 1), 1)
        self.assertEqual(equals(1, 2), 0)

    def test_software_mmio_model_sets_only_requested_bits(self) -> None:
        register = ctypes.c_uint32(0x01234567)
        expected = register.value | (1 << 23)
        setter = self.library.open_cfw_em9305_tail_set_bits32_candidate
        self.assertEqual(setter(ctypes.byref(register), 1 << 23), OK)
        self.assertEqual(register.value, expected)
        self.assertEqual(setter(None, 1), INVALID_ARGUMENT)

    def test_zero_memory_handles_fixed_sizes_and_zero_length_null(self) -> None:
        zero = self.library.open_cfw_em9305_tail_zero_memory_candidate
        for size in (0, 1, 144, 404):
            storage = (ctypes.c_uint8 * max(size, 1))(*([0xA5] * max(size, 1)))
            self.assertEqual(zero(storage, size), OK)
            self.assertEqual(bytes(storage)[:size], bytes(size))
        self.assertEqual(zero(None, 0), OK)
        self.assertEqual(zero(None, 1), INVALID_ARGUMENT)

    def test_freestanding_object_has_no_undefined_runtime_imports(self) -> None:
        with tempfile.TemporaryDirectory(prefix="opencfw-em9305-tail-object-") as directory:
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
        self.assertEqual(result["tail"]["total_bytes"], 890)
        self.assertEqual(result["tail"]["partition"]["unsupported_external"]["bytes"], 630)


if __name__ == "__main__":
    unittest.main()
