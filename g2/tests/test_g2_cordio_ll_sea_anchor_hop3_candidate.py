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
ANALYZER = ROOT / "tools/analyze_g2_cordio_ll_sea_anchor_hop3_candidate.py"
SOURCE = ROOT / "research/candidates/cordio_ll_sea_anchor_hop3/runtime_cordio_ll_sea_anchor_hop3_candidate.c"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("anchor_hop3", ANALYZER)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load analyzer")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Evidence(ctypes.Structure):
    _fields_ = [
        ("stock_start", ctypes.c_uint32), ("stock_end_exclusive", ctypes.c_uint32),
        ("stock_bytes", ctypes.c_size_t), ("source_class", ctypes.c_int),
        ("upstream_module", ctypes.c_char_p), ("upstream_function", ctypes.c_char_p),
        ("upstream_license", ctypes.c_char_p),
    ]


class Invocation(ctypes.Structure):
    _fields_ = [("words", ctypes.c_size_t * 8)]


PROVIDER = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_char_p,
                            ctypes.c_char_p, ctypes.POINTER(Invocation))


class AnchorHop3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.analyzer = load_analyzer()
        compiler = shutil.which("clang") or shutil.which("cc")
        if compiler is None:
            raise unittest.SkipTest("no host compiler")
        cls.temp = tempfile.TemporaryDirectory(prefix="anchor-hop3-")
        library = Path(cls.temp.name) / "libanchor_hop3.so"
        subprocess.run([
            compiler, "-std=c11", "-O2", "-fPIC", "-shared", "-ffreestanding",
            "-fno-builtin", "-Wall", "-Wextra", "-Werror", "-I", str(SOURCE.parent),
            str(SOURCE), "-o", str(library),
        ], check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.open_cfw_cordio_ll_sea_anchor_hop3_evidence_count.restype = ctypes.c_size_t
        cls.lib.open_cfw_cordio_ll_sea_anchor_hop3_evidence.argtypes = [ctypes.c_size_t]
        cls.lib.open_cfw_cordio_ll_sea_anchor_hop3_evidence.restype = ctypes.POINTER(Evidence)
        cls.lib.open_cfw_cordio_ll_sea_anchor_hop3_evidence_by_address.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_cordio_ll_sea_anchor_hop3_evidence_by_address.restype = ctypes.POINTER(Evidence)
        cls.invoke = cls.lib.open_cfw_cordio_ll_sea_anchor_hop3_candidate
        cls.invoke.argtypes = [ctypes.c_uint32, PROVIDER, ctypes.c_void_p,
                               ctypes.POINTER(Invocation)]
        cls.invoke.restype = ctypes.c_int

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "temp"):
            cls.temp.cleanup()

    def test_audit_partition_and_remainder(self):
        result = self.analyzer.run_audit()
        self.assertEqual(result["status"], "candidate-qualified-anchor-hop3")
        self.assertFalse(result["hardware_operations"])
        source = result["source_attribution"]
        self.assertEqual(source["anchors"], {"functions": 12, "bytes": 9_420})
        self.assertEqual(source["hop2_refinement"], {"functions": 11, "bytes": 2_854})
        self.assertEqual(source["hop3"], {"functions": 22, "bytes": 3_400})
        self.assertEqual(result["unsupported_remainder"]["after"],
                         {"functions": 210, "bytes": 35_348})
        self.assertFalse(result["adapter"]["production_routed"])

    def test_all_evidence_rows_are_exact_upstream_sources(self):
        self.assertEqual(self.lib.open_cfw_cordio_ll_sea_anchor_hop3_evidence_count(), 45)
        totals = {0: [0, 0], 1: [0, 0], 2: [0, 0]}
        for index in range(45):
            item = self.lib.open_cfw_cordio_ll_sea_anchor_hop3_evidence(index).contents
            self.assertEqual(item.stock_end_exclusive - item.stock_start, item.stock_bytes)
            self.assertTrue(item.upstream_module)
            self.assertTrue(item.upstream_function)
            self.assertIn(b"FreeType Project License", item.upstream_license)
            totals[item.source_class][0] += 1
            totals[item.source_class][1] += item.stock_bytes
        self.assertEqual(totals, {0: [12, 9_420], 1: [11, 2_854], 2: [22, 3_400]})
        self.assertFalse(self.lib.open_cfw_cordio_ll_sea_anchor_hop3_evidence(45))

    def test_provider_routes_named_source_and_fails_closed(self):
        calls = []

        @PROVIDER
        def provider(_context, module, function, invocation):
            calls.append((module.decode(), function.decode()))
            invocation.contents.words[0] = 123
            return 0

        invocation = Invocation()
        self.assertEqual(self.invoke(0x005D4ED0, provider, None, ctypes.byref(invocation)), 0)
        self.assertEqual(calls, [("psintrp.c", "cf2_interpT2CharString")])
        self.assertEqual(invocation.words[0], 123)
        self.assertEqual(self.invoke(0x005D185E, provider, None, ctypes.byref(invocation)), 2)
        self.assertEqual(self.invoke(0x005D4ED0, PROVIDER(), None, ctypes.byref(invocation)), 3)
        self.assertEqual(self.invoke(0x005D4ED0, provider, None, None), 1)

    def test_representative_exact_identities(self):
        records = self.analyzer.run_audit()["source_attribution"]["records"]
        expected = {
            "0x005D2418": ("psblues.c", "cf2_blues_init"),
            "0x005D36B8": ("pshints.c", "cf2_hintmap_init"),
            "0x005D2196": ("cffdecode.c", "cff_lookup_glyph_by_stdcharcode"),
            "0x005D4B78": ("psintrp.c", "cf2_hintmask_setAll"),
        }
        for address, identity in expected.items():
            item = records[address]
            self.assertEqual((item["upstream_module"], item["upstream_function"]), identity)
            self.assertEqual(len(item["sha256"]), 64)

    def test_cli_is_deterministic_json(self):
        command = [sys.executable, str(ANALYZER)]
        first = subprocess.run(command, check=True, capture_output=True, text=True).stdout
        second = subprocess.run(command, check=True, capture_output=True, text=True).stdout
        self.assertEqual(first, second)
        self.assertEqual(json.loads(first)["status"], "candidate-qualified-anchor-hop3")


if __name__ == "__main__":
    unittest.main()
