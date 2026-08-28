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
ANALYZER = ROOT / "tools/analyze_g2_cordio_ll_sea_hop4_residue_candidate.py"
SOURCE = ROOT / "research/candidates/cordio_ll_sea_hop4_residue/runtime_cordio_ll_sea_hop4_residue_candidate.c"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("hop4_residue", ANALYZER)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load analyzer")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Evidence(ctypes.Structure):
    _fields_ = [("start", ctypes.c_uint32), ("end", ctypes.c_uint32),
                ("size", ctypes.c_size_t), ("group", ctypes.c_int),
                ("module", ctypes.c_char_p), ("function", ctypes.c_char_p),
                ("license", ctypes.c_char_p)]


class Invocation(ctypes.Structure):
    _fields_ = [("words", ctypes.c_size_t * 8)]


PROVIDER = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_char_p,
                            ctypes.c_char_p, ctypes.POINTER(Invocation))


class Hop4ResidueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.analyzer = load_analyzer()
        cc = shutil.which("clang") or shutil.which("cc")
        if cc is None:
            raise unittest.SkipTest("no host compiler")
        cls.temp = tempfile.TemporaryDirectory(prefix="hop4-residue-")
        library = Path(cls.temp.name) / "libhop4.so"
        subprocess.run([cc, "-std=c11", "-O2", "-fPIC", "-shared",
                        "-ffreestanding", "-fno-builtin", "-Wall", "-Wextra",
                        "-Werror", "-I", str(SOURCE.parent), str(SOURCE), "-o",
                        str(library)], check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.open_cfw_cordio_ll_sea_hop4_residue_evidence_count.restype = ctypes.c_size_t
        cls.lib.open_cfw_cordio_ll_sea_hop4_residue_evidence.argtypes = [ctypes.c_size_t]
        cls.lib.open_cfw_cordio_ll_sea_hop4_residue_evidence.restype = ctypes.POINTER(Evidence)
        cls.invoke = cls.lib.open_cfw_cordio_ll_sea_hop4_residue_candidate
        cls.invoke.argtypes = [ctypes.c_uint32, PROVIDER, ctypes.c_void_p,
                               ctypes.POINTER(Invocation)]
        cls.invoke.restype = ctypes.c_int

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "temp"):
            cls.temp.cleanup()

    def test_audit_closes_hop4_caller_and_hop2_residue(self):
        result = self.analyzer.run_audit()
        self.assertEqual(result["status"], "candidate-qualified-hop4-residue")
        source = result["source_attribution"]
        self.assertEqual(source["hop2_residue"], {"functions": 3, "bytes": 308})
        self.assertEqual(source["island_caller"], {"functions": 1, "bytes": 448})
        self.assertEqual(source["hop4"], {"functions": 8, "bytes": 948})
        self.assertEqual(result["unsupported_remainder"]["after"],
                         {"functions": 198, "bytes": 33_644})
        self.assertEqual(result["unsupported_remainder"]["typed_external_hop2"],
                         {"functions": 0, "bytes": 0})
        self.assertFalse(result["adapter"]["production_routed"])

    def test_table_partition_and_license(self):
        self.assertEqual(self.lib.open_cfw_cordio_ll_sea_hop4_residue_evidence_count(), 12)
        totals = {0: [0, 0], 1: [0, 0], 2: [0, 0]}
        for index in range(12):
            item = self.lib.open_cfw_cordio_ll_sea_hop4_residue_evidence(index).contents
            self.assertEqual(item.end - item.start, item.size)
            self.assertTrue(item.module and item.function)
            self.assertIn(b"FreeType Project License", item.license)
            totals[item.group][0] += 1
            totals[item.group][1] += item.size
        self.assertEqual(totals, {0: [3, 308], 1: [1, 448], 2: [8, 948]})
        self.assertFalse(self.lib.open_cfw_cordio_ll_sea_hop4_residue_evidence(12))

    def test_residue_identities_are_exact(self):
        records = self.analyzer.run_audit()["source_attribution"]["records"]
        expected = {
            "0x005D185E": ("psobjs.c", "ps_builder_check_points"),
            "0x005D1986": ("psobjs.c", "ps_builder_close_contour"),
            "0x005D1ED0": ("t1decode.c", "t1_lookup_glyph_by_stdcharcode_ps"),
            "0x005D3068": ("psft.c", "cf2_decoder_parse_charstrings"),
            "0x005D40C0": ("pshints.c", "cf2_glyphpath_computeIntersection"),
        }
        for address, identity in expected.items():
            item = records[address]
            self.assertEqual((item["upstream_module"], item["upstream_function"]), identity)
            self.assertEqual(len(item["sha256"]), 64)

    def test_provider_boundary(self):
        calls = []

        @PROVIDER
        def provider(_ctx, module, function, invocation):
            calls.append((module.decode(), function.decode()))
            invocation.contents.words[0] = 9
            return 0

        invocation = Invocation()
        self.assertEqual(self.invoke(0x005D1986, provider, None, ctypes.byref(invocation)), 0)
        self.assertEqual(calls, [("psobjs.c", "ps_builder_close_contour")])
        self.assertEqual(self.invoke(0, provider, None, ctypes.byref(invocation)), 2)
        self.assertEqual(self.invoke(0x005D1986, PROVIDER(), None, ctypes.byref(invocation)), 3)
        self.assertEqual(self.invoke(0x005D1986, provider, None, None), 1)

    def test_cli_deterministic(self):
        command = [sys.executable, str(ANALYZER)]
        first = subprocess.run(command, check=True, capture_output=True, text=True).stdout
        second = subprocess.run(command, check=True, capture_output=True, text=True).stdout
        self.assertEqual(first, second)
        self.assertEqual(json.loads(first)["status"], "candidate-qualified-hop4-residue")


if __name__ == "__main__":
    unittest.main()
