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
ANALYZER = ROOT / "tools/analyze_g2_cordio_ll_sea_none_batch9_candidate.py"
SOURCE = ROOT / "research/candidates/cordio_ll_sea_none_batch9/runtime_cordio_ll_sea_none_batch9_candidate.c"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("none_batch9", ANALYZER)
    if spec is None or spec.loader is None:
        raise RuntimeError("load failed")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Evidence(ctypes.Structure):
    _fields_ = [
        ("start", ctypes.c_uint32),
        ("end", ctypes.c_uint32),
        ("size", ctypes.c_size_t),
        ("module", ctypes.c_char_p),
        ("function", ctypes.c_char_p),
        ("license", ctypes.c_char_p),
    ]


class Invocation(ctypes.Structure):
    _fields_ = [("words", ctypes.c_size_t * 8)]


PROVIDER = ctypes.CFUNCTYPE(
    ctypes.c_int, ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p,
    ctypes.POINTER(Invocation)
)


class NoneBatch9Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.analyzer = load_analyzer()
        compiler = shutil.which("clang") or shutil.which("cc")
        if compiler is None:
            raise unittest.SkipTest("no compiler")
        cls.temp = tempfile.TemporaryDirectory(prefix="none9-")
        library = Path(cls.temp.name) / "libnone9.so"
        subprocess.run(
            [
                compiler, "-std=c11", "-O2", "-fPIC", "-shared",
                "-ffreestanding", "-fno-builtin", "-Wall", "-Wextra",
                "-Werror", "-I", str(SOURCE.parent), str(SOURCE), "-o",
                str(library),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.open_cfw_cordio_ll_sea_none_batch9_evidence_count.restype = ctypes.c_size_t
        cls.lib.open_cfw_cordio_ll_sea_none_batch9_evidence.argtypes = [ctypes.c_size_t]
        cls.lib.open_cfw_cordio_ll_sea_none_batch9_evidence.restype = ctypes.POINTER(Evidence)
        cls.invoke = cls.lib.open_cfw_cordio_ll_sea_none_batch9_candidate
        cls.invoke.argtypes = [ctypes.c_uint32, PROVIDER, ctypes.c_void_p, ctypes.POINTER(Invocation)]
        cls.invoke.restype = ctypes.c_int

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_chained_partition(self):
        data = self.analyzer.run_audit()
        self.assertEqual(data["status"], "candidate-qualified-none-batch9")
        self.assertEqual(data["none_group"]["batch9_source_recovered"], {"functions": 20, "bytes": 4542})
        self.assertEqual(data["none_group"]["upstream_freetype_source"], {"functions": 125, "bytes": 23718})
        self.assertEqual(data["none_group"]["typed_external"], {"functions": 73, "bytes": 9926})
        self.assertEqual(data["unsupported_remainder"]["before"], {"functions": 93, "bytes": 14468})
        self.assertFalse(data["adapter"]["production_routed"])

    def test_table(self):
        self.assertEqual(self.lib.open_cfw_cordio_ll_sea_none_batch9_evidence_count(), 20)
        total = 0
        names = []
        for index in range(20):
            record = self.lib.open_cfw_cordio_ll_sea_none_batch9_evidence(index).contents
            total += record.size
            names.append(record.function.decode())
            self.assertEqual(record.end - record.start, record.size)
            self.assertEqual(record.module, b"ttcmap.c")
            self.assertIn(b"FreeType Project License", record.license)
        self.assertEqual(tuple(names), self.analyzer.EXPECTED)
        self.assertEqual(total, 4542)
        self.assertFalse(self.lib.open_cfw_cordio_ll_sea_none_batch9_evidence(20))

    def test_exact_and_cluster_guards(self):
        data = self.analyzer.run_audit()
        records = data["none_group"]["records"]
        self.assertEqual(records["0x005DC542"]["upstream_function"], "tt_cmap0_validate")
        self.assertEqual(records["0x005DD584"]["upstream_function"], "tt_cmap8_validate")
        self.assertEqual(records["0x005DDB3A"]["upstream_function"], "tt_cmap12_validate")
        self.assertEqual(records["0x005DE2CE"]["upstream_function"], "tt_cmap14_validate")
        self.assertEqual(records["0x005DE9D2"]["upstream_function"], "tt_cmap14_variant_chars")
        self.assertEqual(records["0x005DEC32"]["disposition"], "typed_external")
        self.assertEqual(data["uncatalogued_clusters"]["bytes"], 2824)
        self.assertTrue(all(not row["claimed_exact"] for row in data["uncatalogued_clusters"]["records"]))

    def test_provider_fail_closed(self):
        calls = []

        @PROVIDER
        def provider(_context, module, function, invocation):
            calls.append((module.decode(), function.decode()))
            invocation.contents.words[0] = 37
            return 0

        invocation = Invocation()
        self.assertEqual(self.invoke(0x005DE2CE, provider, None, ctypes.byref(invocation)), 0)
        self.assertEqual(calls, [("ttcmap.c", "tt_cmap14_validate")])
        self.assertEqual(self.invoke(0x005DE72A, provider, None, ctypes.byref(invocation)), 2)
        self.assertEqual(self.invoke(0x005DE2CE, PROVIDER(), None, ctypes.byref(invocation)), 3)
        self.assertEqual(self.invoke(0x005DE2CE, provider, None, None), 1)

    def test_cli_deterministic(self):
        command = [sys.executable, str(ANALYZER)]
        first = subprocess.run(command, check=True, capture_output=True, text=True).stdout
        second = subprocess.run(command, check=True, capture_output=True, text=True).stdout
        self.assertEqual(first, second)
        self.assertEqual(json.loads(first)["status"], "candidate-qualified-none-batch9")


if __name__ == "__main__":
    unittest.main()
