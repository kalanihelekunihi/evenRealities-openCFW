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
ANALYZER = ROOT / "tools/analyze_g2_cordio_ll_sea_none_batch10_candidate.py"
SOURCE = ROOT / "research/candidates/cordio_ll_sea_none_batch10/runtime_cordio_ll_sea_none_batch10_candidate.c"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("none_batch10", ANALYZER)
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
        ("in_none_census", ctypes.c_uint8),
    ]


class Invocation(ctypes.Structure):
    _fields_ = [("words", ctypes.c_size_t * 8)]


PROVIDER = ctypes.CFUNCTYPE(
    ctypes.c_int, ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p,
    ctypes.POINTER(Invocation)
)


class NoneBatch10Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.analyzer = load_analyzer()
        compiler = shutil.which("clang") or shutil.which("cc")
        if compiler is None:
            raise unittest.SkipTest("no compiler")
        cls.temp = tempfile.TemporaryDirectory(prefix="none10-")
        library = Path(cls.temp.name) / "libnone10.so"
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
        cls.lib.open_cfw_cordio_ll_sea_none_batch10_evidence_count.restype = ctypes.c_size_t
        cls.lib.open_cfw_cordio_ll_sea_none_batch10_evidence.argtypes = [ctypes.c_size_t]
        cls.lib.open_cfw_cordio_ll_sea_none_batch10_evidence.restype = ctypes.POINTER(Evidence)
        cls.invoke = cls.lib.open_cfw_cordio_ll_sea_none_batch10_candidate
        cls.invoke.argtypes = [ctypes.c_uint32, PROVIDER, ctypes.c_void_p, ctypes.POINTER(Invocation)]
        cls.invoke.restype = ctypes.c_int

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_chained_partition(self):
        data = self.analyzer.run_audit()
        self.assertEqual(data["status"], "candidate-qualified-none-batch10")
        self.assertEqual(data["none_group"]["batch10_source_recovered"], {"functions": 19, "bytes": 3614})
        self.assertEqual(data["none_group"]["upstream_freetype_source"], {"functions": 144, "bytes": 27332})
        self.assertEqual(data["none_group"]["typed_external"], {"functions": 54, "bytes": 6312})
        self.assertEqual(data["unsupported_remainder"]["before"], {"functions": 73, "bytes": 9926})
        self.assertEqual(data["authenticated_outside_none_census"]["functions"], 1)
        self.assertEqual(data["authenticated_outside_none_census"]["bytes"], 102)
        self.assertFalse(data["adapter"]["production_routed"])

    def test_table(self):
        self.assertEqual(self.lib.open_cfw_cordio_ll_sea_none_batch10_evidence_count(), 20)
        census_total = 0
        outside_total = 0
        identities = []
        for index in range(20):
            record = self.lib.open_cfw_cordio_ll_sea_none_batch10_evidence(index).contents
            self.assertEqual(record.end - record.start, record.size)
            self.assertIn(b"FreeType Project License", record.license)
            identities.append((record.module.decode(), record.function.decode()))
            if record.in_none_census:
                census_total += record.size
            else:
                outside_total += record.size
        self.assertEqual(tuple(identities), self.analyzer.EXPECTED)
        self.assertEqual(census_total, 3614)
        self.assertEqual(outside_total, 102)
        self.assertFalse(self.lib.open_cfw_cordio_ll_sea_none_batch10_evidence(20))

    def test_exact_and_cluster_guards(self):
        data = self.analyzer.run_audit()
        records = data["none_group"]["records"]
        self.assertEqual(records["0x005DEC90"]["upstream_function"], "tt_face_build_cmaps")
        self.assertEqual(records["0x005DEFDE"]["upstream_function"], "tt_face_get_kerning")
        self.assertEqual(records["0x005DF2F2"]["upstream_function"], "tt_face_load_font_dir")
        self.assertEqual(records["0x005DFB9C"]["upstream_function"], "tt_face_get_metrics")
        self.assertEqual(records["0x005DFF5A"]["upstream_function"], "load_format_25")
        outside = data["authenticated_outside_none_census"]["records"][0]
        self.assertEqual(outside["start"], 0x005E0002)
        self.assertEqual(outside["upstream_function"], "load_post_names")
        self.assertTrue(outside["claimed_exact"])
        self.assertEqual(data["uncatalogued_clusters"]["bytes"], 1458)
        self.assertTrue(all(not row["claimed_exact"] for row in data["uncatalogued_clusters"]["records"]))

    def test_provider_boundary(self):
        calls = []

        @PROVIDER
        def provider(_context, module, function, invocation):
            calls.append((module.decode(), function.decode()))
            invocation.contents.words[0] = 41
            return 0

        invocation = Invocation()
        self.assertEqual(self.invoke(0x005DF2F2, provider, None, ctypes.byref(invocation)), 0)
        self.assertEqual(self.invoke(0x005E0002, provider, None, ctypes.byref(invocation)), 0)
        self.assertEqual(calls, [("ttload.c", "tt_face_load_font_dir"), ("ttpost.c", "load_post_names")])
        self.assertEqual(self.invoke(0x005DEE14, provider, None, ctypes.byref(invocation)), 2)
        self.assertEqual(self.invoke(0x005DF2F2, PROVIDER(), None, ctypes.byref(invocation)), 3)
        self.assertEqual(self.invoke(0x005DF2F2, provider, None, None), 1)

    def test_cli_deterministic(self):
        command = [sys.executable, str(ANALYZER)]
        first = subprocess.run(command, check=True, capture_output=True, text=True).stdout
        second = subprocess.run(command, check=True, capture_output=True, text=True).stdout
        self.assertEqual(first, second)
        self.assertEqual(json.loads(first)["status"], "candidate-qualified-none-batch10")


if __name__ == "__main__":
    unittest.main()
