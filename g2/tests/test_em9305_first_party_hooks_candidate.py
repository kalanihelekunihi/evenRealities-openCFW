#!/usr/bin/env python3

from __future__ import annotations

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
ANALYZER = ROOT / "tools/analyze_em9305_first_party_hooks_candidate.py"
SOURCE = ROOT / "components/shared/em9305/runtime_first_party_hooks_candidate.c"
HEADER = SOURCE.with_suffix(".h")

OK = 0
INVALID_ARGUMENT = 1
UNRESOLVED_PROVIDER = 2
PROVIDER_FAILED = 3


def load_analyzer():
    spec = importlib.util.spec_from_file_location(
        "analyze_em9305_first_party_hooks_candidate", ANALYZER,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load first-party hook analyzer")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Invocation(ctypes.Structure):
    _fields_ = [("words", ctypes.c_size_t * 4)]


OPAQUE = ctypes.CFUNCTYPE(
    ctypes.c_int, ctypes.c_void_p, ctypes.POINTER(Invocation),
)
IDLE_STEP = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p)
IDLE_FINAL = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_uint32)


class Providers(ctypes.Structure):
    _fields_ = [
        ("context", ctypes.c_void_p),
        ("startup_hook_target", OPAQUE),
        ("myapp_module", OPAQUE),
        ("vendor_resume_extension", OPAQUE),
        ("vendor_startup_extension", OPAQUE),
        ("qf_resume_target", OPAQUE),
        ("idle_step_0x00333d7c", IDLE_STEP),
        ("idle_step_0x003100ec", IDLE_STEP),
        ("idle_final_0x00310728", IDLE_FINAL),
    ]


class Evidence(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_int),
        ("stock_start", ctypes.c_size_t),
        ("stock_end_exclusive", ctypes.c_size_t),
        ("stock_bytes", ctypes.c_size_t),
        ("stock_sha256", ctypes.c_char_p),
        ("family", ctypes.c_char_p),
        ("model", ctypes.c_int),
    ]


class Em9305FirstPartyHooksCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        compiler = shutil.which("clang") or shutil.which("cc")
        if compiler is None:
            raise unittest.SkipTest("no host C compiler")
        cls.compiler = compiler
        cls.temporary = tempfile.TemporaryDirectory(prefix="opencfw-em9305-hooks-")
        library = Path(cls.temporary.name) / "libem9305_hooks.so"
        subprocess.run(
            [
                compiler, "-std=c11", "-O2", "-fPIC", "-shared",
                "-ffreestanding", "-fno-builtin", "-Wall", "-Wextra", "-Werror",
                "-I", str(SOURCE.parent), str(SOURCE), "-o", str(library),
            ],
            check=True, capture_output=True, text=True,
        )
        cls.library = ctypes.CDLL(str(library))
        cls.library.open_cfw_em9305_first_party_span_evidence.argtypes = [ctypes.c_int]
        cls.library.open_cfw_em9305_first_party_span_evidence.restype = ctypes.POINTER(Evidence)
        cls.opaque_names = (
            "open_cfw_em9305_startup_hook_target_candidate",
            "open_cfw_em9305_myapp_module_candidate",
            "open_cfw_em9305_vendor_resume_extension_candidate",
            "open_cfw_em9305_vendor_startup_extension_candidate",
            "open_cfw_em9305_qf_resume_internal_hook_candidate",
            "open_cfw_em9305_qf_startup_internal_hook_candidate",
        )
        for name in cls.opaque_names:
            function = getattr(cls.library, name)
            function.argtypes = [ctypes.POINTER(Providers), ctypes.POINTER(Invocation)]
            function.restype = ctypes.c_int
        cls.idle = cls.library.open_cfw_em9305_qk_idle_internal_hook_candidate
        cls.idle.argtypes = [ctypes.POINTER(Providers)]
        cls.idle.restype = ctypes.c_int

    @classmethod
    def tearDownClass(cls) -> None:
        if hasattr(cls, "temporary"):
            cls.temporary.cleanup()

    def test_audit_authenticates_seven_spans_and_hook_table(self) -> None:
        result = self.analyzer.run_audit()
        self.assertEqual(result["status"], "candidate-qualified-fail-closed")
        self.assertTrue(result["read_only"])
        self.assertFalse(result["hardware_operations"])
        self.assertEqual(result["license"], "MIT")
        stock = result["stock_first_party"]
        self.assertEqual(stock["span_count"], 7)
        self.assertEqual(stock["total_bytes"], 1_224)
        self.assertEqual(len(stock["hook_table"]["targets"]), 9)
        candidate = result["candidate"]
        self.assertEqual(candidate["provider_required_spans"], 4)
        self.assertEqual(candidate["exact_tail_branch_spans"], 2)
        self.assertEqual(candidate["exact_ordered_call_shell_spans"], 1)
        self.assertFalse(candidate["production_routed"])

    def test_evidence_map_is_closed_and_invalid_ids_fail_closed(self) -> None:
        observed = []
        for span_id in range(7):
            pointer = self.library.open_cfw_em9305_first_party_span_evidence(span_id)
            self.assertTrue(pointer)
            item = pointer.contents
            observed.append((item.id, item.stock_start, item.stock_end_exclusive,
                             item.stock_bytes, item.model))
            self.assertEqual(item.stock_end_exclusive - item.stock_start, item.stock_bytes)
            self.assertEqual(len(item.stock_sha256.decode()), 64)
            self.assertTrue(item.family.decode())
        self.assertEqual(sum(item[3] for item in observed), 1_224)
        self.assertEqual([item[4] for item in observed], [0, 0, 0, 0, 1, 1, 2])
        self.assertFalse(self.library.open_cfw_em9305_first_party_span_evidence(-1))
        self.assertFalse(self.library.open_cfw_em9305_first_party_span_evidence(7))

    def test_all_opaque_boundaries_reject_missing_inputs_and_providers(self) -> None:
        invocation = Invocation((11, 22, 33, 44))
        providers = Providers()
        for name in self.opaque_names:
            function = getattr(self.library, name)
            self.assertEqual(function(None, ctypes.byref(invocation)), INVALID_ARGUMENT)
            self.assertEqual(function(ctypes.byref(providers), None), INVALID_ARGUMENT)
            self.assertEqual(
                function(ctypes.byref(providers), ctypes.byref(invocation)),
                UNRESOLVED_PROVIDER,
            )

    def test_opaque_boundary_forwards_carrier_and_normalizes_failure(self) -> None:
        calls: list[tuple[int, list[int]]] = []

        @OPAQUE
        def success(context, invocation):
            calls.append((ctypes.cast(context, ctypes.c_void_p).value or 0,
                          list(invocation.contents.words)))
            return OK

        @OPAQUE
        def failure(_context, _invocation):
            return UNRESOLVED_PROVIDER

        providers = Providers()
        providers.context = ctypes.c_void_p(0x9305)
        providers.vendor_resume_extension = success
        invocation = Invocation((1, 2, 3, 4))
        function = self.library.open_cfw_em9305_vendor_resume_extension_candidate
        self.assertEqual(function(ctypes.byref(providers), ctypes.byref(invocation)), OK)
        self.assertEqual(calls, [(0x9305, [1, 2, 3, 4])])
        providers.vendor_resume_extension = failure
        self.assertEqual(
            function(ctypes.byref(providers), ctypes.byref(invocation)),
            PROVIDER_FAILED,
        )

    def test_startup_tail_branch_delegates_to_authenticated_target_span(self) -> None:
        calls: list[list[int]] = []

        @OPAQUE
        def target(_context, invocation):
            calls.append(list(invocation.contents.words))
            return OK

        providers = Providers()
        providers.startup_hook_target = target
        invocation = Invocation((9, 8, 7, 6))
        function = self.library.open_cfw_em9305_qf_startup_internal_hook_candidate
        self.assertEqual(function(ctypes.byref(providers), ctypes.byref(invocation)), OK)
        self.assertEqual(calls, [[9, 8, 7, 6]])

    def test_idle_shell_prevalidates_then_calls_in_exact_order_with_zero(self) -> None:
        events: list[tuple[str, int]] = []

        @IDLE_STEP
        def first(context):
            events.append(("333d7c", ctypes.cast(context, ctypes.c_void_p).value or 0))
            return OK

        @IDLE_STEP
        def second(context):
            events.append(("3100ec", ctypes.cast(context, ctypes.c_void_p).value or 0))
            return OK

        @IDLE_FINAL
        def final(context, argument):
            events.append(("310728", argument))
            self.assertEqual(ctypes.cast(context, ctypes.c_void_p).value, 0x55)
            return OK

        providers = Providers()
        providers.context = ctypes.c_void_p(0x55)
        providers.idle_step_0x00333d7c = first
        providers.idle_step_0x003100ec = second
        self.assertEqual(self.idle(ctypes.byref(providers)), UNRESOLVED_PROVIDER)
        self.assertEqual(events, [])
        providers.idle_final_0x00310728 = final
        self.assertEqual(self.idle(ctypes.byref(providers)), OK)
        self.assertEqual(events, [("333d7c", 0x55), ("3100ec", 0x55), ("310728", 0)])

    def test_idle_shell_stops_after_provider_failure(self) -> None:
        events: list[str] = []

        @IDLE_STEP
        def first(_context):
            events.append("first")
            return OK

        @IDLE_STEP
        def second(_context):
            events.append("second")
            return INVALID_ARGUMENT

        @IDLE_FINAL
        def final(_context, _argument):
            events.append("final")
            return OK

        providers = Providers()
        providers.idle_step_0x00333d7c = first
        providers.idle_step_0x003100ec = second
        providers.idle_final_0x00310728 = final
        self.assertEqual(self.idle(ctypes.byref(providers)), PROVIDER_FAILED)
        self.assertEqual(events, ["first", "second"])

    def test_freestanding_object_has_no_undefined_runtime_imports(self) -> None:
        with tempfile.TemporaryDirectory(prefix="opencfw-em9305-hooks-object-") as directory:
            output = Path(directory) / "candidate.o"
            subprocess.run(
                [
                    self.compiler, "-std=c11", "-O2", "-ffreestanding",
                    "-fno-builtin", "-fno-stack-protector", "-Wall", "-Wextra",
                    "-Werror", "-I", str(SOURCE.parent), "-c", str(SOURCE),
                    "-o", str(output),
                ],
                check=True, capture_output=True, text=True,
            )
            nm = shutil.which("nm")
            if nm is not None:
                undefined = subprocess.run(
                    [nm, "-u", str(output)], check=True, capture_output=True, text=True,
                ).stdout.strip()
                self.assertEqual(undefined, "")

    def test_json_cli_is_machine_readable(self) -> None:
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        completed = subprocess.run(
            [sys.executable, str(ANALYZER), "--json"], cwd=ROOT,
            env=environment, check=True, capture_output=True, text=True,
        )
        result = json.loads(completed.stdout)
        self.assertEqual(result["stock_first_party"]["total_bytes"], 1_224)
        self.assertFalse(result["candidate"]["production_routed"])

    def test_sources_are_isolated_mit_candidates(self) -> None:
        self.assertIn("SPDX-License-Identifier: MIT", SOURCE.read_text())
        self.assertIn("SPDX-License-Identifier: MIT", HEADER.read_text())
        forbidden = ("overlay.json", "open_cfw.py", "apollo_overlay.py")
        combined = SOURCE.read_text() + HEADER.read_text()
        for item in forbidden:
            self.assertNotIn(item, combined)


if __name__ == "__main__":
    unittest.main()
