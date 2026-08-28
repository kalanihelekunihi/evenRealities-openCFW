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
ANALYZER = ROOT / "tools/analyze_g2_cordio_ll_sea_none_batch12_candidate.py"
SOURCE = ROOT / "research/candidates/cordio_ll_sea_none_batch12/runtime_cordio_ll_sea_none_batch12_candidate.c"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("none_batch12", ANALYZER)
    if spec is None or spec.loader is None:
        raise RuntimeError("load failed")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Evidence(ctypes.Structure):
    _fields_ = [
        ("start", ctypes.c_uint32), ("end", ctypes.c_uint32),
        ("size", ctypes.c_size_t), ("provider", ctypes.c_char_p),
        ("module", ctypes.c_char_p), ("function", ctypes.c_char_p),
        ("license", ctypes.c_char_p),
    ]


class Invocation(ctypes.Structure):
    _fields_ = [("words", ctypes.c_size_t * 8)]


PROVIDER = ctypes.CFUNCTYPE(
    ctypes.c_int, ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p,
    ctypes.c_char_p, ctypes.POINTER(Invocation)
)


class NoneBatch12Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.analyzer = load_analyzer()
        compiler = shutil.which("clang") or shutil.which("cc")
        if compiler is None:
            raise unittest.SkipTest("no compiler")
        cls.temp = tempfile.TemporaryDirectory(prefix="none12-")
        library = Path(cls.temp.name) / "libnone12.so"
        subprocess.run(
            [compiler, "-std=c11", "-O2", "-fPIC", "-shared",
             "-ffreestanding", "-fno-builtin", "-Wall", "-Wextra",
             "-Werror", "-I", str(SOURCE.parent), str(SOURCE), "-o", str(library)],
            check=True, capture_output=True, text=True,
        )
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.open_cfw_cordio_ll_sea_none_batch12_evidence_count.restype = ctypes.c_size_t
        cls.lib.open_cfw_cordio_ll_sea_none_batch12_evidence.argtypes = [ctypes.c_size_t]
        cls.lib.open_cfw_cordio_ll_sea_none_batch12_evidence.restype = ctypes.POINTER(Evidence)
        cls.invoke = cls.lib.open_cfw_cordio_ll_sea_none_batch12_candidate
        cls.invoke.argtypes = [ctypes.c_uint32, PROVIDER, ctypes.c_void_p, ctypes.POINTER(Invocation)]
        cls.invoke.restype = ctypes.c_int

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_final_partition_is_closed(self):
        data = self.analyzer.run_audit()
        self.assertEqual(data["status"], "candidate-qualified-none-batch12-closed")
        self.assertEqual(data["none_group"]["batch12_source_recovered"], {"functions": 14, "bytes": 796})
        self.assertEqual(data["none_group"]["classified"], {"functions": 198, "bytes": 33644})
        self.assertEqual(data["none_group"]["unclassified"], {"functions": 0, "bytes": 0})
        self.assertEqual(data["none_group"]["upstream_freetype_source"], {"functions": 192, "bytes": 33124})
        self.assertEqual(data["none_group"]["upstream_segger_rtt_provider"], {"functions": 6, "bytes": 520})
        self.assertEqual(data["unsupported_remainder"]["before"], {"functions": 14, "bytes": 796})
        self.assertEqual(data["unsupported_remainder"]["after"], {"functions": 0, "bytes": 0})
        self.assertFalse(data["adapter"]["production_routed"])

    def test_table_and_licenses(self):
        self.assertEqual(self.lib.open_cfw_cordio_ll_sea_none_batch12_evidence_count(), 14)
        total = 0
        freetype = segger = 0
        identities = []
        for index in range(14):
            record = self.lib.open_cfw_cordio_ll_sea_none_batch12_evidence(index).contents
            total += record.size
            identities.append((record.provider.decode(), record.module.decode(), record.function.decode()))
            self.assertEqual(record.end - record.start, record.size)
            if record.provider == b"SEGGER":
                segger += record.size
                self.assertIn(b"SEGGER RTT redistributable", record.license)
            else:
                freetype += record.size
                self.assertIn(b"FreeType Project License", record.license)
        self.assertEqual(total, 796)
        self.assertEqual((freetype, segger), (276, 520))
        self.assertEqual(identities[0], ("FreeType", "t1cmap.c", "t1_cmap_std_init"))
        self.assertEqual(identities[-1], ("FreeType", "ttbdf.c", "tt_face_free_bdf_props"))
        self.assertFalse(self.lib.open_cfw_cordio_ll_sea_none_batch12_evidence(14))

    def test_exact_and_typed_boundary_guards(self):
        data = self.analyzer.run_audit()
        records = data["none_group"]["records"]
        self.assertEqual(records["0x005D1D64"]["upstream_function"], "t1_cmap_std_char_index")
        self.assertEqual(records["0x005D2EFE"]["upstream_function"], "cf2_free_instance")
        self.assertEqual(records["0x005D9950"]["upstream_function"], "SEGGER_RTT_Init")
        self.assertEqual(records["0x005D9ABC"]["upstream_function"], "SEGGER_RTT_WriteNoLock")
        self.assertEqual(records["0x005DC266"]["upstream_function"], "tt_face_free_bdf_props")
        boundaries = data["typed_non_census_boundaries"]
        self.assertEqual((boundaries["clusters"], boundaries["bytes"]), (4, 1118))
        self.assertEqual(boundaries["unclassified"], {"clusters": 0, "bytes": 0})
        self.assertTrue(all(not row["claimed_exact"] and not row["unclassified"] and row["reason"] for row in boundaries["records"]))

    def test_provider_and_fail_closed_boundary(self):
        calls = []

        @PROVIDER
        def provider(_context, owner, module, function, invocation):
            calls.append((owner.decode(), module.decode(), function.decode()))
            invocation.contents.words[0] = 47
            return 0

        invocation = Invocation()
        self.assertEqual(self.invoke(0x005D1D2A, provider, None, ctypes.byref(invocation)), 0)
        self.assertEqual(self.invoke(0x005D9B28, provider, None, ctypes.byref(invocation)), 0)
        self.assertEqual(calls, [("FreeType", "t1cmap.c", "t1_cmap_std_init"), ("SEGGER", "SEGGER_RTT.c", "SEGGER_RTT_Write")])
        self.assertEqual(self.invoke(0x005D1DD4, provider, None, ctypes.byref(invocation)), 2)
        self.assertEqual(self.invoke(0x005D1D2A, PROVIDER(), None, ctypes.byref(invocation)), 3)
        self.assertEqual(self.invoke(0x005D1D2A, provider, None, None), 1)

    def test_cli_deterministic(self):
        command = [sys.executable, str(ANALYZER)]
        first = subprocess.run(command, check=True, capture_output=True, text=True).stdout
        second = subprocess.run(command, check=True, capture_output=True, text=True).stdout
        self.assertEqual(first, second)
        self.assertEqual(json.loads(first)["none_group"]["unclassified"]["functions"], 0)


if __name__ == "__main__":
    unittest.main()
