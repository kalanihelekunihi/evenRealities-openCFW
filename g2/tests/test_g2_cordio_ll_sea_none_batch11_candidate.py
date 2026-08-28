#!/usr/bin/env python3
from __future__ import annotations

import ctypes
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_cordio_ll_sea_none_batch11_candidate.py"
SOURCE = ROOT / "research/candidates/cordio_ll_sea_none_batch11/runtime_cordio_ll_sea_none_batch11_candidate.c"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("none_batch11", ANALYZER)
    if spec is None or spec.loader is None:
        raise RuntimeError("load failed")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Evidence(ctypes.Structure):
    _fields_ = [
        ("start", ctypes.c_uint32), ("end", ctypes.c_uint32),
        ("size", ctypes.c_size_t), ("module", ctypes.c_char_p),
        ("function", ctypes.c_char_p), ("license", ctypes.c_char_p),
    ]


class Invocation(ctypes.Structure):
    _fields_ = [("words", ctypes.c_size_t * 8)]


PROVIDER = ctypes.CFUNCTYPE(
    ctypes.c_int, ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p,
    ctypes.POINTER(Invocation)
)


class NoneBatch11Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.analyzer = load_analyzer()
        compiler = shutil.which("clang") or shutil.which("cc")
        if compiler is None:
            raise unittest.SkipTest("no compiler")
        cls.temp = tempfile.TemporaryDirectory(prefix="none11-")
        library = Path(cls.temp.name) / "libnone11.so"
        subprocess.run(
            [compiler, "-std=c11", "-O2", "-fPIC", "-shared",
             "-ffreestanding", "-fno-builtin", "-Wall", "-Wextra",
             "-Werror", "-I", str(SOURCE.parent), str(SOURCE), "-o", str(library)],
            check=True, capture_output=True, text=True,
        )
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.open_cfw_cordio_ll_sea_none_batch11_evidence_count.restype = ctypes.c_size_t
        cls.lib.open_cfw_cordio_ll_sea_none_batch11_evidence.argtypes = [ctypes.c_size_t]
        cls.lib.open_cfw_cordio_ll_sea_none_batch11_evidence.restype = ctypes.POINTER(Evidence)
        cls.invoke = cls.lib.open_cfw_cordio_ll_sea_none_batch11_candidate
        cls.invoke.argtypes = [ctypes.c_uint32, PROVIDER, ctypes.c_void_p, ctypes.POINTER(Invocation)]
        cls.invoke.restype = ctypes.c_int

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_chained_partition(self):
        data = self.analyzer.run_audit()
        self.assertEqual(data["status"], "candidate-qualified-none-batch11")
        self.assertEqual(data["none_group"]["batch11_source_recovered"], {"functions": 40, "bytes": 5516})
        self.assertEqual(data["none_group"]["upstream_freetype_source"], {"functions": 184, "bytes": 32848})
        self.assertEqual(data["none_group"]["typed_external"], {"functions": 14, "bytes": 796})
        self.assertEqual(data["unsupported_remainder"]["before"], {"functions": 54, "bytes": 6312})
        self.assertFalse(data["adapter"]["production_routed"])

    def test_table(self):
        self.assertEqual(self.lib.open_cfw_cordio_ll_sea_none_batch11_evidence_count(), 40)
        total = 0
        identities = []
        for index in range(40):
            record = self.lib.open_cfw_cordio_ll_sea_none_batch11_evidence(index).contents
            total += record.size
            identities.append((record.module.decode(), record.function.decode()))
            self.assertEqual(record.end - record.start, record.size)
            self.assertIn(b"FreeType Project License", record.license)
        self.assertEqual(tuple(identities), self.analyzer.EXPECTED)
        self.assertEqual(total, 5516)
        self.assertFalse(self.lib.open_cfw_cordio_ll_sea_none_batch11_evidence(40))

    def test_exact_and_cluster_guards(self):
        data = self.analyzer.run_audit()
        records = data["none_group"]["records"]
        self.assertEqual(records["0x005D008E"]["upstream_function"], "PS_Conv_Strtol")
        self.assertEqual(records["0x005D04E8"]["upstream_function"], "PS_Conv_EexecDecode")
        self.assertEqual(records["0x005D08F6"]["upstream_function"], "ps_parser_skip_PS_token")
        self.assertEqual(records["0x005D0DE0"]["upstream_function"], "ps_parser_load_field")
        self.assertEqual(records["0x005D1512"]["upstream_function"], "cff_builder_init")
        self.assertEqual(records["0x005D176A"]["upstream_function"], "ps_builder_init")
        self.assertEqual(records["0x005D1D2A"]["disposition"], "typed_external")
        self.assertEqual(data["uncatalogued_clusters"]["bytes"], 580)
        self.assertTrue(all(not row["claimed_exact"] for row in data["uncatalogued_clusters"]["records"]))

    def test_provider_fail_closed(self):
        calls = []

        @PROVIDER
        def provider(_context, module, function, invocation):
            calls.append((module.decode(), function.decode()))
            invocation.contents.words[0] = 43
            return 0

        invocation = Invocation()
        self.assertEqual(self.invoke(0x005D0DE0, provider, None, ctypes.byref(invocation)), 0)
        self.assertEqual(calls, [("psobjs.c", "ps_parser_load_field")])
        self.assertEqual(self.invoke(0x005D121A, provider, None, ctypes.byref(invocation)), 2)
        self.assertEqual(self.invoke(0x005D0DE0, PROVIDER(), None, ctypes.byref(invocation)), 3)
        self.assertEqual(self.invoke(0x005D0DE0, provider, None, None), 1)

    def test_cli_deterministic(self):
        command = [sys.executable, str(ANALYZER)]
        first = subprocess.run(command, check=True, capture_output=True, text=True).stdout
        second = subprocess.run(command, check=True, capture_output=True, text=True).stdout
        self.assertEqual(first, second)
        self.assertEqual(json.loads(first)["status"], "candidate-qualified-none-batch11")


if __name__ == "__main__":
    unittest.main()
