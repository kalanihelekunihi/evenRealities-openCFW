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
ANALYZER = ROOT / "tools/analyze_em9305_slave_connection_boundary.py"
SOURCE = ROOT / "components/shared/em9305/runtime_controller_slave_connection_boundary.c"

OK = 0
INVALID = 1
UNSUPPORTED = 2
FAILED = 3


def load_analyzer():
    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    spec = importlib.util.spec_from_file_location(
        "analyze_em9305_slave_connection_boundary", ANALYZER,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load EM9305 slave-connection analyzer")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Invocation(ctypes.Structure):
    _fields_ = [("words", ctypes.c_size_t * 8)]


PROVIDER = ctypes.CFUNCTYPE(
    ctypes.c_int32, ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(Invocation),
)


class Ports(ctypes.Structure):
    _fields_ = [("context", ctypes.c_void_p), ("provider", PROVIDER)]


class Evidence(ctypes.Structure):
    _fields_ = [
        ("stock_start", ctypes.c_uint32),
        ("stock_end", ctypes.c_uint32),
        ("name", ctypes.c_char_p),
        ("stock_sha256", ctypes.c_char_p),
        ("source_status", ctypes.c_char_p),
    ]


class Em9305SlaveConnectionBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        compiler = shutil.which("clang") or shutil.which("cc")
        if compiler is None:
            raise unittest.SkipTest("no host C compiler")
        cls.compiler = compiler
        cls.temporary = tempfile.TemporaryDirectory(prefix="opencfw-em9305-slv-conn-")
        library = Path(cls.temporary.name) / "libem9305_slv_conn.so"
        subprocess.run(
            [
                compiler, "-std=c11", "-O2", "-fPIC", "-shared",
                "-ffreestanding", "-fno-builtin", "-Wall", "-Wextra", "-Werror",
                "-I", str(SOURCE.parent), str(SOURCE), "-o", str(library),
            ],
            check=True, capture_output=True, text=True,
        )
        cls.library = ctypes.CDLL(str(library))
        cls.boundary = cls.library.open_cfw_em9305_slv_conn_boundary
        cls.boundary.argtypes = [ctypes.POINTER(Ports), ctypes.c_int,
                                 ctypes.POINTER(Invocation)]
        cls.boundary.restype = ctypes.c_int32

    @classmethod
    def tearDownClass(cls) -> None:
        if hasattr(cls, "temporary"):
            cls.temporary.cleanup()

    def test_audit_promotes_largest_residual_only_to_typed_boundary(self) -> None:
        result = self.analyzer.run_audit()
        self.assertEqual(result["status"], "candidate-qualified-fail-closed")
        self.assertTrue(result["read_only"])
        self.assertFalse(result["hardware_operations"])
        self.assertEqual(result["license"], "MIT")
        self.assertEqual(result["function_count"], 6)
        self.assertEqual(result["decision"]["bytes"], 3_126)
        self.assertEqual(
            result["decision"]["readiness"],
            "typed_unsupported_external_boundary",
        )
        self.assertFalse(result["exact_source_available"])
        self.assertFalse(result["redistribution_authority_resolved"])
        self.assertFalse(result["candidate"]["production_routed"])
        self.assertEqual(result["hardware_validation"], "blocked by unavailable physical evidence")

    def test_evidence_descriptors_cover_six_function_bodies(self) -> None:
        array_type = Evidence * 6
        evidence = array_type.in_dll(
            self.library, "open_cfw_em9305_slv_conn_evidence_map",
        )
        self.assertEqual(evidence[0].stock_start, 0x00329888)
        self.assertEqual(evidence[-1].stock_end, 0x0032A4BE)
        self.assertEqual(
            [item.name.decode() for item in evidence],
            [
                "lctrSlvConnEndOp", "lctrSlvConnExecute",
                "lctrSlvConnExecuteSm", "lctrSlvConnResetHandler",
                "lctrSlvConnRxCompletion", "lctrSlvConnTxCompletion",
            ],
        )
        self.assertEqual(sum(item.stock_end - item.stock_start for item in evidence), 3_118)
        self.assertTrue(all(len(item.stock_sha256.decode()) == 64 for item in evidence))

    def test_boundary_rejects_invalid_inputs_and_missing_provider(self) -> None:
        invocation = Invocation((1, 2, 3, 4, 5, 6, 7, 8))
        ports = Ports()
        self.assertEqual(self.boundary(None, 0, ctypes.byref(invocation)), INVALID)
        self.assertEqual(self.boundary(ctypes.byref(ports), 0, None), INVALID)
        self.assertEqual(self.boundary(ctypes.byref(ports), -1, ctypes.byref(invocation)), INVALID)
        self.assertEqual(self.boundary(ctypes.byref(ports), 6, ctypes.byref(invocation)), INVALID)
        for entry in range(6):
            self.assertEqual(
                self.boundary(ctypes.byref(ports), entry, ctypes.byref(invocation)),
                UNSUPPORTED,
            )

    def test_provider_receives_each_typed_id_context_and_carrier(self) -> None:
        calls: list[tuple[int, int, list[int]]] = []

        @PROVIDER
        def provider(context, entry, invocation):
            calls.append((ctypes.cast(context, ctypes.c_void_p).value or 0,
                          entry, list(invocation.contents.words)))
            invocation.contents.words[entry] += 100
            return 0

        ports = Ports(ctypes.c_void_p(0x9305), provider)
        for entry in range(6):
            invocation = Invocation((10, 11, 12, 13, 14, 15, 16, 17))
            self.assertEqual(
                self.boundary(ctypes.byref(ports), entry, ctypes.byref(invocation)), OK,
            )
            self.assertEqual(invocation.words[entry], 110 + entry)
        self.assertEqual([item[1] for item in calls], list(range(6)))
        self.assertTrue(all(item[0] == 0x9305 for item in calls))

    def test_provider_failure_is_normalized(self) -> None:
        @PROVIDER
        def failure(_context, _entry, _invocation):
            return 19

        ports = Ports(None, failure)
        invocation = Invocation()
        self.assertEqual(
            self.boundary(ctypes.byref(ports), 3, ctypes.byref(invocation)), FAILED,
        )

    def test_parent_cluster_identity_mutation_fails_closed(self) -> None:
        original = self.analyzer.clusters.analyze
        report = original()
        altered = copy.deepcopy(report)
        altered["clusters"][0]["segment_sha256"] = "0" * 64
        self.analyzer.clusters.analyze = lambda: altered
        try:
            with self.assertRaisesRegex(self.analyzer.BoundaryError, "identity drift"):
                self.analyzer.run_audit()
        finally:
            self.analyzer.clusters.analyze = original

    def test_freestanding_object_has_no_undefined_runtime_imports(self) -> None:
        object_path = Path(self.temporary.name) / "slave_connection.o"
        subprocess.run(
            [
                self.compiler, "-std=c11", "-O2", "-ffreestanding", "-fno-builtin",
                "-Wall", "-Wextra", "-Werror", "-I", str(SOURCE.parent),
                "-c", str(SOURCE), "-o", str(object_path),
            ],
            check=True, capture_output=True, text=True,
        )
        nm = shutil.which("nm")
        if nm is None:
            raise unittest.SkipTest("nm unavailable")
        completed = subprocess.run(
            [nm, "-u", str(object_path)], check=True, capture_output=True, text=True,
        )
        self.assertEqual(completed.stdout.strip(), "")

    def test_json_cli_is_machine_readable(self) -> None:
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        completed = subprocess.run(
            [sys.executable, str(ANALYZER), "--json"], cwd=ROOT,
            env=environment, check=True, capture_output=True, text=True,
        )
        result = json.loads(completed.stdout)
        self.assertEqual(result["decision"]["bytes"], 3_126)


if __name__ == "__main__":
    unittest.main()
