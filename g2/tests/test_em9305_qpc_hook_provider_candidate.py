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
ANALYZER = ROOT / "tools/analyze_em9305_qpc_hook_provider_candidate.py"
SOURCE = ROOT / "components/shared/em9305/runtime_qpc_hook_provider_candidate.c"

OK = 0
MISSING = 1
FAILED = 2


def load_analyzer():
    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    spec = importlib.util.spec_from_file_location(
        "analyze_em9305_qpc_hook_provider_candidate", ANALYZER,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load EM9305 QP/C hook-provider analyzer")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


STEP = ctypes.CFUNCTYPE(ctypes.c_int32, ctypes.c_void_p)
FINAL = ctypes.CFUNCTYPE(ctypes.c_int32, ctypes.c_void_p, ctypes.c_uint32)


class Ports(ctypes.Structure):
    _fields_ = [
        ("context", ctypes.c_void_p),
        ("pal_uart_resume", STEP),
        ("wsf_os_run_idle_tasks", STEP),
        ("volt_mon_do_measurement", FINAL),
    ]


class Em9305QpcHookProviderCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        compiler = shutil.which("clang") or shutil.which("cc")
        if compiler is None:
            raise unittest.SkipTest("no host C compiler")
        cls.compiler = compiler
        cls.temporary = tempfile.TemporaryDirectory(prefix="opencfw-em9305-qpc-provider-")
        library = Path(cls.temporary.name) / "libem9305_qpc_provider.so"
        subprocess.run(
            [
                compiler, "-std=c11", "-O2", "-fPIC", "-shared",
                "-ffreestanding", "-fno-builtin", "-Wall", "-Wextra", "-Werror",
                "-I", str(SOURCE.parent), str(SOURCE), "-o", str(library),
            ],
            check=True, capture_output=True, text=True,
        )
        cls.library = ctypes.CDLL(str(library))
        cls.resume = cls.library.open_cfw_em9305_qf_resume_named_boundary
        cls.resume.argtypes = [ctypes.POINTER(Ports)]
        cls.resume.restype = ctypes.c_int32
        cls.idle = cls.library.open_cfw_em9305_qk_idle_named_boundary
        cls.idle.argtypes = [ctypes.POINTER(Ports)]
        cls.idle.restype = ctypes.c_int32

    @classmethod
    def tearDownClass(cls) -> None:
        if hasattr(cls, "temporary"):
            cls.temporary.cleanup()

    def test_audit_authenticates_named_providers_without_admitting_source(self) -> None:
        result = self.analyzer.run_audit()
        self.assertEqual(result["status"], "candidate-qualified-named-fail-closed")
        self.assertTrue(result["read_only"])
        self.assertFalse(result["hardware_operations"])
        self.assertEqual(result["license"], "MIT")
        self.assertEqual(
            set(result["providers"]),
            {"PalUartResume", "wsfOsRunIdleTasks", "VoltMon_DoMeasurement"},
        )
        self.assertTrue(all(
            item["redistribution_authority"] == "unresolved"
            for item in result["providers"].values()
        ))
        self.assertEqual(result["unresolved_providers"], [])
        self.assertEqual(
            {item["decision"] for item in result["decisions"].values()},
            {"named_provider_boundary"},
        )
        self.assertEqual(
            result["semantic_noop"]["behavior"], "return_without_state_change",
        )
        self.assertFalse(result["candidate"]["production_routed"])
        self.assertEqual(result["hardware_validation"], "deferred by project direction")

    def test_resume_boundary_fails_closed_and_normalizes_provider_status(self) -> None:
        self.assertEqual(self.resume(None), MISSING)
        ports = Ports()
        self.assertEqual(self.resume(ctypes.byref(ports)), MISSING)
        calls: list[int] = []

        @STEP
        def success(context):
            calls.append(ctypes.cast(context, ctypes.c_void_p).value or 0)
            return 0

        @STEP
        def failure(_context):
            return 7

        ports.context = ctypes.c_void_p(0x9305)
        ports.pal_uart_resume = success
        self.assertEqual(self.resume(ctypes.byref(ports)), OK)
        self.assertEqual(calls, [0x9305])
        ports.pal_uart_resume = failure
        self.assertEqual(self.resume(ctypes.byref(ports)), FAILED)

    def test_idle_boundary_preflights_and_preserves_order_and_zero_argument(self) -> None:
        events: list[tuple[str, int]] = []

        @STEP
        def wsf(context):
            events.append(("wsf", ctypes.cast(context, ctypes.c_void_p).value or 0))
            return 0

        @FINAL
        def voltage(_context, argument):
            events.append(("voltmon", argument))
            return 0

        ports = Ports()
        ports.context = ctypes.c_void_p(0x55)
        ports.wsf_os_run_idle_tasks = wsf
        self.assertEqual(self.idle(ctypes.byref(ports)), MISSING)
        self.assertEqual(events, [])
        ports.volt_mon_do_measurement = voltage
        self.assertEqual(self.idle(ctypes.byref(ports)), OK)
        self.assertEqual(events, [("wsf", 0x55), ("voltmon", 0)])

    def test_idle_boundary_stops_at_first_failed_provider(self) -> None:
        events: list[str] = []

        @STEP
        def first(_context):
            events.append("first")
            return 3

        @FINAL
        def final(_context, _argument):
            events.append("final")
            return 0

        ports = Ports(None, first, first, final)
        self.assertEqual(self.idle(ctypes.byref(ports)), FAILED)
        self.assertEqual(events, ["first"])

    def test_archive_mapping_drift_fails_closed(self) -> None:
        original = self.analyzer.json.loads

        def altered_loads(payload):
            value = original(payload)
            if isinstance(value, dict) and "functions" in value:
                value = copy.deepcopy(value)
                for item in value["functions"]:
                    if item["name"] == "PalUartResume":
                        item["matches"] = []
            return value

        self.analyzer.json.loads = altered_loads
        try:
            with self.assertRaisesRegex(self.analyzer.CandidateError, "mapping drift"):
                self.analyzer.run_audit()
        finally:
            self.analyzer.json.loads = original

    def test_freestanding_object_has_no_undefined_runtime_provider(self) -> None:
        object_path = Path(self.temporary.name) / "qpc_provider.o"
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
        self.assertEqual(result["status"], "candidate-qualified-named-fail-closed")


if __name__ == "__main__":
    unittest.main()
