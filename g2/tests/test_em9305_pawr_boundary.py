#!/usr/bin/env python3

from __future__ import annotations

import copy
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
ANALYZER = ROOT / "tools/analyze_em9305_pawr_boundary.py"
SOURCE = ROOT / "components/shared/em9305/runtime_controller_pawr_boundary.c"


def load_analyzer():
    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    spec = importlib.util.spec_from_file_location("analyze_em9305_pawr_boundary", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Invocation(ctypes.Structure):
    _fields_ = [("words", ctypes.c_size_t * 8)]


PROVIDER = ctypes.CFUNCTYPE(ctypes.c_int32, ctypes.c_void_p, ctypes.c_int,
                            ctypes.POINTER(Invocation))


class Ports(ctypes.Structure):
    _fields_ = [("context", ctypes.c_void_p), ("provider", PROVIDER)]


class Em9305PawrBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        compiler = shutil.which("clang") or shutil.which("cc")
        if compiler is None:
            raise unittest.SkipTest("no host compiler")
        cls.compiler = compiler
        cls.temporary = tempfile.TemporaryDirectory(prefix="opencfw-em9305-pawr-")
        library = Path(cls.temporary.name) / "libpawr.so"
        subprocess.run(
            [compiler, "-std=c11", "-O2", "-fPIC", "-shared", "-ffreestanding",
             "-fno-builtin", "-Wall", "-Wextra", "-Werror", "-I", str(SOURCE.parent),
             str(SOURCE), "-o", str(library)],
            check=True, capture_output=True, text=True,
        )
        cls.library = ctypes.CDLL(str(library))
        cls.boundary = cls.library.open_cfw_em9305_pawr_boundary
        cls.boundary.argtypes = [ctypes.POINTER(Ports), ctypes.c_int,
                                 ctypes.POINTER(Invocation)]
        cls.boundary.restype = ctypes.c_int32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_audit_closes_second_largest_span_only_as_typed_boundary(self) -> None:
        result = self.analyzer.run_audit()
        self.assertEqual(result["status"], "candidate-qualified-fail-closed")
        self.assertEqual(result["decision"]["bytes"], 1_804)
        self.assertEqual(result["function_count"], 4)
        self.assertFalse(result["exact_source_available"])
        self.assertFalse(result["redistribution_authority_resolved"])
        self.assertFalse(result["candidate"]["production_routed"])
        self.assertEqual(result["hardware_validation"], "blocked by unavailable physical evidence")

    def test_boundary_fails_closed_and_forwards_all_ids(self) -> None:
        invocation = Invocation((1, 2, 3, 4, 5, 6, 7, 8))
        ports = Ports()
        self.assertEqual(self.boundary(None, 0, ctypes.byref(invocation)), 1)
        self.assertEqual(self.boundary(ctypes.byref(ports), 0, None), 1)
        self.assertEqual(self.boundary(ctypes.byref(ports), -1, ctypes.byref(invocation)), 1)
        self.assertEqual(self.boundary(ctypes.byref(ports), 4, ctypes.byref(invocation)), 1)
        self.assertEqual(self.boundary(ctypes.byref(ports), 0, ctypes.byref(invocation)), 2)
        calls = []

        @PROVIDER
        def provider(context, entry, carrier):
            calls.append((ctypes.cast(context, ctypes.c_void_p).value, entry,
                          list(carrier.contents.words)))
            return 0

        ports = Ports(ctypes.c_void_p(0x9305), provider)
        for entry in range(4):
            self.assertEqual(self.boundary(ctypes.byref(ports), entry,
                                           ctypes.byref(invocation)), 0)
        self.assertEqual([item[1] for item in calls], [0, 1, 2, 3])

    def test_provider_failure_is_distinct(self) -> None:
        @PROVIDER
        def failure(_context, _entry, _carrier):
            return 9

        ports = Ports(None, failure)
        self.assertEqual(self.boundary(ctypes.byref(ports), 2,
                                       ctypes.byref(Invocation())), 3)

    def test_parent_identity_mutation_fails_closed(self) -> None:
        original = self.analyzer.clusters.analyze
        altered = copy.deepcopy(original())
        altered["clusters"][1]["segment_sha256"] = "0" * 64
        self.analyzer.clusters.analyze = lambda: altered
        try:
            with self.assertRaisesRegex(self.analyzer.BoundaryError, "identity drift"):
                self.analyzer.run_audit()
        finally:
            self.analyzer.clusters.analyze = original

    def test_freestanding_object_has_no_undefined_imports(self) -> None:
        object_path = Path(self.temporary.name) / "pawr.o"
        subprocess.run(
            [self.compiler, "-std=c11", "-O2", "-ffreestanding", "-fno-builtin",
             "-Wall", "-Wextra", "-Werror", "-I", str(SOURCE.parent), "-c",
             str(SOURCE), "-o", str(object_path)],
            check=True, capture_output=True, text=True,
        )
        nm = shutil.which("nm")
        if nm is None:
            raise unittest.SkipTest("nm unavailable")
        result = subprocess.run([nm, "-u", str(object_path)], check=True,
                                capture_output=True, text=True)
        self.assertEqual(result.stdout.strip(), "")

    def test_json_cli(self) -> None:
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        result = subprocess.run([sys.executable, str(ANALYZER), "--json"], cwd=ROOT,
                                env=environment, check=True, capture_output=True, text=True)
        self.assertEqual(json.loads(result.stdout)["decision"]["bytes"], 1_804)


if __name__ == "__main__":
    unittest.main()
