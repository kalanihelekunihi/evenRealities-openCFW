#!/usr/bin/env python3

from __future__ import annotations

import ctypes
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_cordio_ll_sea_hop2_candidate.py"
SOURCE = ROOT / "research/candidates/cordio_ll_sea_hop2/runtime_cordio_ll_sea_hop2_candidate.c"

UPSTREAM = 0
TYPED_EXTERNAL = 1
OK = 0
INVALID_ARGUMENT = 1
UNKNOWN_ADDRESS = 2
UNSUPPORTED_EXTERNAL = 3
PROVIDER_FAILED = 4


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_hop2", ANALYZER)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load hop-2 analyzer")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Evidence(ctypes.Structure):
    _fields_ = [
        ("stock_start", ctypes.c_uint32),
        ("stock_end_exclusive", ctypes.c_uint32),
        ("stock_bytes", ctypes.c_size_t),
        ("disposition", ctypes.c_int),
        ("upstream_module", ctypes.c_char_p),
        ("upstream_function", ctypes.c_char_p),
        ("upstream_license", ctypes.c_char_p),
    ]


class Invocation(ctypes.Structure):
    _fields_ = [("words", ctypes.c_size_t * 8)]


PROVIDER = ctypes.CFUNCTYPE(
    ctypes.c_int, ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p,
    ctypes.POINTER(Invocation),
)


class CordioLlSeaHop2CandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        compiler = shutil.which("clang") or shutil.which("cc")
        if compiler is None:
            raise unittest.SkipTest("no host C compiler")
        cls.temporary = tempfile.TemporaryDirectory(prefix="opencfw-hop2-")
        library = Path(cls.temporary.name) / "libhop2.so"
        subprocess.run(
            [
                compiler, "-std=c11", "-O2", "-fPIC", "-shared",
                "-ffreestanding", "-fno-builtin", "-Wall", "-Wextra", "-Werror",
                "-I", str(SOURCE.parent), str(SOURCE), "-o", str(library),
            ],
            check=True, capture_output=True, text=True,
        )
        cls.library = ctypes.CDLL(str(library))
        cls.library.open_cfw_cordio_ll_sea_hop2_evidence_count.restype = ctypes.c_size_t
        cls.library.open_cfw_cordio_ll_sea_hop2_evidence.argtypes = [ctypes.c_size_t]
        cls.library.open_cfw_cordio_ll_sea_hop2_evidence.restype = ctypes.POINTER(Evidence)
        cls.library.open_cfw_cordio_ll_sea_hop2_evidence_by_address.argtypes = [ctypes.c_uint32]
        cls.library.open_cfw_cordio_ll_sea_hop2_evidence_by_address.restype = ctypes.POINTER(Evidence)
        cls.invoke = cls.library.open_cfw_cordio_ll_sea_hop2_candidate
        cls.invoke.argtypes = [ctypes.c_uint32, PROVIDER, ctypes.c_void_p,
                               ctypes.POINTER(Invocation)]
        cls.invoke.restype = ctypes.c_int

    @classmethod
    def tearDownClass(cls) -> None:
        if hasattr(cls, "temporary"):
            cls.temporary.cleanup()

    def test_analyzer_recovers_source_and_preserves_remainder(self) -> None:
        result = self.analyzer.run_audit()
        self.assertEqual(result["status"], "candidate-qualified-hop2")
        self.assertTrue(result["read_only"])
        self.assertFalse(result["hardware_operations"])
        self.assertFalse(result["topology_correction"]["lvgl_attribution"])
        tranche = result["hop2_tranche"]
        self.assertEqual((tranche["functions"], tranche["bytes"]), (59, 5_006))
        self.assertEqual(tranche["upstream_freetype_source"],
                         {"functions": 45, "bytes": 1_844})
        self.assertEqual(tranche["typed_external"],
                         {"functions": 14, "bytes": 3_162})
        self.assertEqual(result["unsupported_remainder"]["after"],
                         {"functions": 243, "bytes": 41_602})
        self.assertEqual(result["unsupported_remainder"]["after_unselected_only"],
                         {"functions": 229, "bytes": 38_440})
        self.assertFalse(result["adapter"]["production_routed"])

    def test_exact_module_and_function_identities(self) -> None:
        records = self.analyzer.run_audit()["hop2_tranche"]["records"]
        expected = {
            "0x005D1D1C": ("psobjs.c", "cff_random"),
            "0x005D22F2": ("psarrst.c", "cf2_arrstack_init"),
            "0x005D2EA8": ("psft.c", "cf2_checkTransform"),
            "0x005D4B4C": ("psintrp.c", "cf2_hintmask_read"),
            "0x005D6D98": ("psread.c", "cf2_buf_readByte"),
            "0x005D6FF2": ("psstack.c", "cf2_stack_roll"),
        }
        for address, identity in expected.items():
            record = records[address]
            self.assertEqual((record["upstream_module"], record["upstream_function"]), identity)
            self.assertIn("FreeType Project License", record["upstream_license"])
            self.assertEqual(len(record["sha256"]), 64)

    def test_evidence_table_is_complete_and_addressable(self) -> None:
        self.assertEqual(self.library.open_cfw_cordio_ll_sea_hop2_evidence_count(), 59)
        source_count = external_count = source_bytes = external_bytes = 0
        for index in range(59):
            pointer = self.library.open_cfw_cordio_ll_sea_hop2_evidence(index)
            self.assertTrue(pointer)
            record = pointer.contents
            self.assertEqual(record.stock_end_exclusive - record.stock_start,
                             record.stock_bytes)
            lookup = self.library.open_cfw_cordio_ll_sea_hop2_evidence_by_address(
                record.stock_start,
            )
            self.assertTrue(lookup)
            self.assertEqual(lookup.contents.stock_start, record.stock_start)
            if record.disposition == UPSTREAM:
                source_count += 1
                source_bytes += record.stock_bytes
                self.assertTrue(record.upstream_module)
                self.assertTrue(record.upstream_function)
                self.assertIn(b"FreeType Project License", record.upstream_license)
            else:
                self.assertEqual(record.disposition, TYPED_EXTERNAL)
                external_count += 1
                external_bytes += record.stock_bytes
                self.assertFalse(record.upstream_module)
                self.assertFalse(record.upstream_function)
                self.assertFalse(record.upstream_license)
        self.assertEqual((source_count, source_bytes), (45, 1_844))
        self.assertEqual((external_count, external_bytes), (14, 3_162))
        self.assertFalse(self.library.open_cfw_cordio_ll_sea_hop2_evidence(59))
        self.assertFalse(self.library.open_cfw_cordio_ll_sea_hop2_evidence_by_address(0))

    def test_provider_adapter_routes_only_identified_upstream(self) -> None:
        calls: list[tuple[str, str, int]] = []

        @PROVIDER
        def provider(_context, module, function, invocation):
            calls.append((module.decode(), function.decode(), invocation.contents.words[0]))
            invocation.contents.words[1] = 0xBEEF
            return 0

        invocation = Invocation()
        invocation.words[0] = 7
        self.assertEqual(self.invoke(0x005D1D1C, provider, None,
                                     ctypes.byref(invocation)), OK)
        self.assertEqual(calls, [("psobjs.c", "cff_random", 7)])
        self.assertEqual(invocation.words[1], 0xBEEF)
        self.assertEqual(self.invoke(0x005D185E, provider, None,
                                     ctypes.byref(invocation)), UNSUPPORTED_EXTERNAL)
        self.assertEqual(len(calls), 1)
        self.assertEqual(self.invoke(0, provider, None,
                                     ctypes.byref(invocation)), UNKNOWN_ADDRESS)
        self.assertEqual(self.invoke(0x005D1D1C, PROVIDER(), None,
                                     ctypes.byref(invocation)), UNSUPPORTED_EXTERNAL)
        self.assertEqual(self.invoke(0x005D1D1C, provider, None, None), INVALID_ARGUMENT)

    def test_provider_failure_is_normalized(self) -> None:
        @PROVIDER
        def provider(_context, _module, _function, _invocation):
            return 99

        invocation = Invocation()
        self.assertEqual(self.invoke(0x005D6D98, provider, None,
                                     ctypes.byref(invocation)), PROVIDER_FAILED)

    def test_cli_json_is_deterministic(self) -> None:
        first = subprocess.run(
            [sys.executable, str(ANALYZER)], check=True,
            capture_output=True, text=True,
        ).stdout
        second = subprocess.run(
            [sys.executable, str(ANALYZER)], check=True,
            capture_output=True, text=True,
        ).stdout
        self.assertEqual(first, second)
        self.assertEqual(json.loads(first)["status"], "candidate-qualified-hop2")


if __name__ == "__main__":
    unittest.main()
